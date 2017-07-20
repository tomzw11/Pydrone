#!/usr/bin/python
import time
import cv2
import math
from bebop import *
from apyros.manual import myKbhit, ManualControlException

print 'Takeoff in 10 seconds'
time.sleep(10)
drone = Bebop()
drone.videoDisable() # disable video stream
drone.moveCamera( tilt=-90, pan=0 )

try:

	drone.takeoff()
	drone.moveBy(0,1)
	drone.stop()
	drone.moveBy(0,-1)
	drone.land()

except (ManualControlException,Exception), e:

    print "ManualControlException"
    drone.land()








