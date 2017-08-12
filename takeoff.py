#!/usr/bin/python
import time
import cv2
import math
from bebop import *
from apyros.manual import myKbhit, ManualControlException


timeDelay = 0
print 'Takeoff in %d seconds' % timeDelay
time.sleep(timeDelay)

drone = Bebop()

try:

	# drone.takeoff()
	# print 'r1' , drone.cameraTilt, drone.cameraPan
	# drone.moveCamera( tilt=-90, pan=0 )
	# print 'r2 ', drone.cameraTilt, drone.cameraPan
	drone.wait(1)
	start_time = drone.time
	# print start_time
	drone.videoEnable()
	
	while(drone.time-start_time < 5000):
		# drone.videoEnable()
		print 'streaming'
	drone.videoDisable()
	# drone.wait(1)
	# drone.moveY(1,10)
	# print 'r3 ', drone.cameraTilt, drone.cameraPan
	# drone.takePicture()
	# print 'r4 ', drone.cameraTilt, drone.cameraPan


	# drone.stop()
	# drone.moveTo(x_cor,y_cor,root_height/2)
	# drone.stop()
	# drone.land()

except (ManualControlException,Exception), e:

    print "ManualControlException or Keyboard Interrupt"
    drone.land()








