#!/usr/bin/python
import time
import cv2
import math
from bebop import *
from apyros.manual import myKbhit, ManualControlException

timeDelay = 5
print 'Takeoff in %d seconds' % timeDelay
time.sleep(timeDelay)
drone = Bebop()
drone.moveCamera( tilt=-90, pan=0 )

start_altitude = 1.5
second_altitude = 1
startAngle = drone.angle[2]

try:

	drone.takeoff()
	drone.resetPosition(startAngle,start_altitude)
	drone.position = [0,0,0]
	print drone.position

	drone.resetPosition(startAngle,second_altitude)
	drone.moveBy(1,1)
	drone.stop()
	drone.moveBy(-1,-1)
	drone.stop()
	drone.land()

except (ManualControlException,Exception), e:

    print "ManualControlException"
    drone.land()








