#!/usr/bin/python
"""
  Basic class for communication to Parrot Bebop
  usage:
       ./bebop.py <task> [<metalog> [<F>]]
"""
import sys
import socket
import datetime
import struct
import time
import numpy as np
import math

from navdata import *
from commands import *
from video import VideoFrames


# this will be in new separate repository as common library fo droneika Python-powered drones
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException

HOST = "192.168.42.1"
DISCOVERY_PORT = 44444

NAVDATA_PORT = 43210 # d2c_port
COMMAND_PORT = 54321 # c2d_port

class Bebop:
    def __init__( self, metalog=None, onlyIFrames=True ):
        if metalog is None:
            self._discovery()
            metalog = MetaLog()
        self.navdata = metalog.createLoggedSocket( "navdata", headerFormat="<BBBI" )
        self.navdata.bind( ('',NAVDATA_PORT) )
        if metalog.replay:
            self.commandSender = CommandSenderReplay(metalog.createLoggedSocket( "cmd", headerFormat="<BBBI" ), 
                    hostPortPair=(HOST, COMMAND_PORT), checkAsserts=metalog.areAssertsEnabled())
        else:
            self.commandSender = CommandSender(metalog.createLoggedSocket( "cmd", headerFormat="<BBBI" ), 
                    hostPortPair=(HOST, COMMAND_PORT))
        self.console = metalog.createLoggedInput( "console", myKbhit ).get
        self.metalog = metalog
        self.buf = ""
        self.videoFrameProcessor = VideoFrames( onlyIFrames=onlyIFrames, verbose=False )
        self.videoCbk = None
        self.videoCbkResults = None
        self.battery = None
        self.flyingState = None
        self.flatTrimCompleted = False
        self.manualControl = False
        self.time = None
        self.moveByEnd = None
        self.altitude = None
        self.angle = (0,0,0)
        self.position = (0,0,0)
        self.speed = (0,0,0)
        self.positionGPS = None
        self.cameraTilt = 0
        self.cameraPan = 0
        self.lastImageResult = None
        self.navigateHomeState = None
        self.config()
        self.commandSender.start()
        
    def _discovery( self ):
        "start communication with the drone"
        filename = "tmp.bin" # TODO combination outDir + date/time
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        s.connect( (HOST, DISCOVERY_PORT) )
        s.send( '{"controller_type":"computer", "controller_name":"katarina", "d2c_port":"43210"}' )
        f = open( filename, "wb" )
        while True:
            data = s.recv(10240)
            if len(data) > 0:
                f.write(data)
                f.flush()
                break
        f.close()
        s.close()

    def _update( self, cmd ):
        "internal send command and return navdata"
        
        if not self.manualControl:
            self.manualControl = self.console()
            if self.manualControl:
                # raise exception only once
                raise ManualControlException()

        # send even None, to sync in/out queues
        self.commandSender.send( cmd )

        while len(self.buf) == 0:
            data = self.navdata.recv(40960)
            self.buf += data
        data, self.buf = cutPacket( self.buf )
        return data

    def _parseData( self, data ):
        try:
            parseData( data, drone=self, verbose=False )
        except AssertionError, e:
            print "AssertionError", e

    def update( self, cmd=None, ackRequest=False ):
        "send command and return navdata"
        if cmd is None:
            data = self._update( None )
        else:
            data = self._update( packData(cmd, ackRequest=ackRequest) )
        while True:
            if ackRequired(data):
                self._parseData( data )
                data = self._update( createAckPacket(data) )
            elif pongRequired(data):
                self._parseData( data ) # update self.time
                data = self._update( createPongPacket(data) )
            elif videoAckRequired(data):
                if self.videoCbk:
                    self.videoFrameProcessor.append( data )
                    frame = self.videoFrameProcessor.getFrameEx()
                    if frame:
                        self.videoCbk( frame, debug=self.metalog.replay )
                    if self.videoCbkResults:
                        ret = self.videoCbkResults()
                        if ret is not None:
                            print ret
                            self.lastImageResult = ret
                data = self._update( createVideoAckPacket(data) )
            else:
                break
        self._parseData( data )
        return data


    def setVideoCallback( self, cbk, cbkResult=None ):
        "set cbk for collected H.264 encoded video frames & access to results queue"
        self.videoCbk = cbk
        if cbkResult is None:
            self.videoCbkResults = None
        else:
            self.videoCbkResults = self.metalog.createLoggedInput( "cv2", cbkResult ).get
        
    def config( self ):
        # initial cfg
        dt = self.metalog.now()
        if dt: # for compatibility with older log files
            self.update( cmd=setDateCmd( date=dt.date() ) )
            self.update( cmd=setTimeCmd( time=dt.time() ) )
        for cmd in setSpeedSettingsCmdList( maxVerticalSpeed=1.0, maxRotationSpeed=90.0, 
                hullProtection=True, outdoor=True ):
            self.update( cmd=cmd )
        self.update( cmd=requestAllStatesCmd() )
        self.update( cmd=requestAllSettingsCmd() )
        self.moveCamera( tilt=self.cameraTilt, pan=self.cameraPan )
        self.update( videoAutorecordingCmd( enabled=False ) )


    def takeoff( self ):
       
        print "Taking off ...",
        self.update( cmd=takeoffCmd() )
        prevState = None
        for i in xrange(100):
            #print i,
            self.update( cmd=None )
            if self.flyingState != 1 and prevState == 1:
                break
            prevState = self.flyingState
        print "FLYING"
        
    def land( self ):
        speed = 75
        print 'landing'
        while self.altitude > 1 :
            self.update( movePCMDCmd( True, 0, 0, 0, -speed ) )

        self.update( cmd=landCmd() )
        if(self.flyingState==0):
            self.update( videoRecordingCmd( on=False ) )
            print 'landed'

    def hover( self, timeout ):
        startTime = self.time
        count = 0
        while(self.time-startTime<timeout):
            self.update( cmd=movePCMDCmd( active=True, roll=0, pitch=0, yaw=0, gaz=0 ) )
            count += 1
        print count

    def emergency( self ):
        self.update( cmd=emergencyCmd() )

    def trim( self ):
        print "Trim:", 
        self.flatTrimCompleted = False
        for i in xrange(10):
            print i,
            self.update( cmd=None )
        print
        self.update( cmd=trimCmd() )
        for i in xrange(10):
            print i,
            self.update( cmd=None )
            if self.flatTrimCompleted:
                break
   
    def takePicture( self ):
        self.update( cmd=takePictureCmd() )
        print 'picture taken at time ', self.time

    def videoEnable( self ):
        "enable video stream"
        self.update( cmd=videoStreamingCmd( enable=True ), ackRequest=True )

    def videoDisable( self ):
        "enable video stream"
        self.update( cmd=videoStreamingCmd( enable=False ), ackRequest=True )

    def moveCamera( self, tilt, pan ):
        "Tilt/Pan camera consign for the drone (in degrees)"
        self.update( cmd=moveCameraCmd( tilt=tilt, pan=pan) )
        self.cameraTilt, self.cameraPan = tilt, pan # maybe move this to parse data, drone should confirm that

    def resetHome( self ):
        self.update( cmd=resetHomeCmd() )

    def stop( self, timeout=3.0 ):

        print 'stopping the drone'
        startTime = self.time
        droneSpeed = self.speed[0]**2+self.speed[1]**2+self.speed[2]**2
        while(self.time-startTime<timeout and droneSpeed>0.3):
            self.update( movePCMDCmd( True, self.speed[1]*50, self.speed[0]*50, 0, -self.speed[2]*50 ) )
            droneSpeed = self.speed[0]**2+self.speed[1]**2+self.speed[2]**2

        print 'stopping position', -self.position[1], -self.position[0], -self.position[2]
        self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )

    def moveX( self, dX, speed, timeout=3.0 ):
        print 'moveX', dX
        if(dX < 0):
            speed = -speed
        assert self.time is not None
        startTime = self.time
        startPos = self.position[1]
        
        while abs(self.position[1]-startPos) < dX and self.time-startTime < timeout:

            if(self.speed[0] > 0.2):
                self.update( movePCMDCmd( True, speed, -10, 0, 0 ) )
            elif(self.speed[0] < -0.2):
                self.update( movePCMDCmd( True, speed, 10, 0, 0 ) )
            else:
                self.update( movePCMDCmd( True, speed, 0, 0, 0 ) )
            print 'speed ',self.speed
            print 'position ',self.position
        
        self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )

    def moveY( self, dY, speed, timeout=3.0 ):
        print 'moveY', dY
        if(dY < 0):
            speed = -speed
        assert self.time is not None
        startTime = self.time
        startPos = self.position[0]
        
        while abs(self.position[0]-startPos) < dY and self.time-startTime < timeout:

            if(self.speed[1] > 0.2):
                self.update( movePCMDCmd( True, -10, speed, 0, 0 ) )
            elif(self.speed[1] < -0.2):
                self.update( movePCMDCmd( True, 10, speed, 0, 0 ) )
            else:
                self.update( movePCMDCmd( True, 0, speed, 0, 0 ) )
        self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )

    def moveZ( self, altitude, timeout=3.0 ):
        speed = 50 #in percentage
        assert self.time is not None
        assert self.altitude is not None
        startTime = self.time

        if self.altitude < altitude:#going up 
            while self.altitude < altitude and self.time-startTime < timeout and altitude>0:
                self.update( movePCMDCmd( True, 0, 0, 0, speed ) )
                # print 'going up ', self.altitude, self.time-startTime
            self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )
            return

        else:
            while self.altitude > altitude and self.time-startTime < timeout and altitude>0:
                self.update( movePCMDCmd( True, 0, 0, 0, -speed ) )
                #print 'going down ', self.altitude, self.time-startTime
            self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )
            return

        self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )

    def moveBy( self, dX, dY, timeout=8.0):
        # outdated function.
        # TODO: modify targetSpeed so it doesn't use updated values.

        print 'move by ', dX, dY
        startTime = self.time
        startPosition = [0]*2
        startPosition[0] = -self.position[1]
        startPosition[1] = -self.position[0]
        print 'starting position ',startPosition

        targetPosition = [0]*2
        currentSpeed = [0]*2
        targetSpeed = [0]*2
        inputSpeed = [0]*2
        targetPosition[0] = startPosition[0]+dX
        targetPosition[1] = startPosition[1]+dY
        top_speed = 40
        initial_distance = np.sqrt(abs(targetPosition[1]-startPosition[0])**2+abs(targetPosition[0]-startPosition[1])**2)

        print 'tartgetPos x ', targetPosition[0], ' y ', targetPosition[1]

        while(self.time-startTime<timeout):
            distance = np.sqrt(abs(targetPosition[1]+self.position[0])**2+abs(targetPosition[0]+self.position[1])**2)
            # print 'distance ',distance
            if(distance<0.2):
                print 'arrived', distance
                break
            if(distance>initial_distance+2):
                print 'drone out of path', distance
                break

            targetSpeed[0] = targetPosition[0]+self.position[1]
            targetSpeed[1] = targetPosition[1]+self.position[0]
            targetSpeed[0] = targetSpeed[0]/np.sqrt(targetSpeed[0]**2+targetSpeed[1]**2)
            targetSpeed[1] = targetSpeed[1]/np.sqrt(targetSpeed[0]**2+targetSpeed[1]**2)
            #print 'targetspeed x ',targetSpeed[0],' y ',targetSpeed[1]

            currentSpeed[0] = -self.speed[1]/np.sqrt(self.speed[0]**2+self.speed[1]**2)
            currentSpeed[1] = -self.speed[0]/np.sqrt(self.speed[0]**2+self.speed[1]**2)
            #print 'currentspeed x ',currentSpeed[0], ' y ',currentSpeed[1]

            inputSpeed[0] = targetSpeed[0]-currentSpeed[0]
            inputSpeed[1] = targetSpeed[1]-currentSpeed[1]
            #print 'inputSpeed x ',inputSpeed[0],' y ',inputSpeed[1]

            self.update( movePCMDCmd( True, inputSpeed[0]*top_speed, inputSpeed[1]*top_speed, 0, 0 ) )

        self.update( cmd=movePCMDCmd( True, 0, 0, 0, 0 ) )
        endPosition = self.position
        print 'end position x ',-endPosition[1],' y ',-endPosition[0]

    def calibrate( self, dX, dY, timeout=3.0 ):

        startTime = self.time
        rotation_speed = 75
      
        print 'start angle= ',self.angle[2]
        rotation = np.arctan2(dX,dY)
        print 'rotation= ',rotation
        if(rotation+self.angle[2]>math.pi):
            rotateAngle = -2*math.pi+rotation+self.angle[2]
        elif(rotation+self.angle[2]<-math.pi):
            rotateAngle = 2*math.pi+rotation+self.angle[2]
        else:
            rotateAngle = self.angle[2]+rotation 

        if(rotation < 0):
            print 'counterclockwise', rotateAngle
            while abs(self.angle[2]-rotateAngle) > 0.1 and self.time-startTime < timeout:
                self.update( movePCMDCmd( True, 0, 0, -rotation_speed, 0 ) )
            self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )
            print 'end angle= ',self.angle[2]
            return
        else:
            print 'clockwise',rotateAngle
            while abs(self.angle[2]-rotateAngle) > 0.1 and self.time-startTime < timeout:
                self.update( movePCMDCmd( True, 0, 0, rotation_speed, 0 ) )
            self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )
            print 'end angle= ',self.angle[2]
            return

    def resetPosition( self, startAngle, altitude, timeout=5.0 ):
        print 'reset angle...'
        self.moveZ(altitude)

        rotation_speed = 75
        assert self.time is not None
        startTime = self.time
        if abs(startAngle-self.angle[2])<0.1:
            print 'already calibrated'
            self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )
        else:
            if self.angle[2] < 0:
                #print 'calibrate clockwise'
                while abs(self.angle[2]-startAngle) > 0.1 and self.time-startTime < timeout:
                    self.update( movePCMDCmd( True, 0, 0, rotation_speed, 0 ) )
                self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )
                print 'end angle= ',self.angle[2]
                return
            else:
                #print 'calibrate counterclockwise'
                while abs(self.angle[2]-startAngle) > 0.1 and self.time-startTime < timeout:
                    self.update( movePCMDCmd( True, 0, 0, -rotation_speed, 0 ) )
                self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )
                print 'end angle= ',self.angle[2]
                return

    def moveTo( self, X, Y, Z, timeout=5.0):
        print 'move to ', X, Y, Z
        startTime = self.time
        startPosition = [0]*3
        currentSpeed_norm = 0
        targetSpeed_norm = 0
        startPosition[0] = -self.position[1]
        startPosition[1] = -self.position[0]
        startPosition[2] = -self.position[2]

        print 'starting position x ', startPosition[0], ' y ', startPosition[1], ' z ', startPosition[2]

        targetPosition = [0]*3
        currentSpeed = [0]*3
        targetSpeed = [0]*3
        inputSpeed = [0]*3
        targetPosition[0] = X
        targetPosition[1] = Y
        targetPosition[2] = Z

        top_speed = 40
        initial_distance = np.sqrt(abs(targetPosition[1]-startPosition[0])**2+ \
            abs(targetPosition[0]-startPosition[1])**2+ \
            abs(targetPosition[2]-startPosition[2])**2)

        print 'tartgetPos x ', targetPosition[0], ' y ', targetPosition[1], ' z ', targetPosition[2]

        while(self.time-startTime<timeout):
            distance = np.sqrt(abs(targetPosition[1]+self.position[0])**2+ \
                abs(targetPosition[0]+self.position[1])**2+ \
                abs(targetPosition[2]+self.position[2])**2)
            # print 'flight distance ',distance
            # print 'time ',self.time
            if(distance<0.1):
                # self.moveCamera( tilt=-90, pan=0 )
                # self.takePicture();
                print 'arrived', distance
                break
            if(distance>initial_distance+2):
                print 'drone out of path', distance
                break

            targetSpeed_X = targetPosition[0]+self.position[1]
            targetSpeed_Y = targetPosition[1]+self.position[0]
            targetSpeed_Z = targetPosition[2]+self.position[2]
            targetSpeed_norm = np.sqrt(targetSpeed_X**2+targetSpeed_Y**2+targetSpeed_Z**2)

            targetSpeed[0] = targetSpeed_X/targetSpeed_norm
            targetSpeed[1] = targetSpeed_Y/targetSpeed_norm
            targetSpeed[2] = targetSpeed_Z/targetSpeed_norm
            #print 'targetspeed x ',targetSpeed[0],' y ',targetSpeed[1], ' z ', targetSpeed[2]

            currentSpeed_norm = np.sqrt(self.speed[0]**2+self.speed[1]**2+self.speed[2]**2)

            currentSpeed[0] = -self.speed[1]/currentSpeed_norm
            currentSpeed[1] = -self.speed[0]/currentSpeed_norm
            currentSpeed[2] = -self.speed[2]/currentSpeed_norm
            #print 'currentspeed x ',currentSpeed[0], ' y ',currentSpeed[1], ' z ', currentSpeed[2]

            inputSpeed[0] = targetSpeed[0]-currentSpeed[0]
            inputSpeed[1] = targetSpeed[1]-currentSpeed[1]
            inputSpeed[2] = targetSpeed[2]-currentSpeed[2]
            print 'inputSpeed x ',inputSpeed[0],' y ',inputSpeed[1], ' z ', inputSpeed[2]

            self.update( movePCMDCmd( True, inputSpeed[0]*top_speed, inputSpeed[1]*top_speed, 0, inputSpeed[2]*top_speed ) )

        self.update( cmd=movePCMDCmd( True, 0, 0, 0, 0 ) )
        endPosition = self.position
        print 'end position x ',-endPosition[1],' y ',-endPosition[0],' z ',-endPosition[2]
    
    def moveToCancel( self ):
        self.update( cmd=cancelMoveToCmd() )

    def wait( self, duration ):
        print "Wait", duration
        assert self.time is not None
        startTime = self.time
        while self.time-startTime < duration:
            self.update()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    metalog=None
    if len(sys.argv) > 2:
        metalog = MetaLog( filename=sys.argv[2] )
    if len(sys.argv) > 3 and sys.argv[3] == 'F':
        disableAsserts()

    drone = Bebop( metalog=metalog )

    print "Battery:", drone.battery
