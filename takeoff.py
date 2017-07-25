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

try:

	drone.takeoff()
	drone.moveBy(0,2)
	drone.stop()
	drone.moveZ(1)
	drone.moveBy(0,-2)
	drone.land()

except (ManualControlException,Exception), e:

    print "ManualControlException"
    drone.land()








