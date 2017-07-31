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
	drone.moveTo(-1,-1,1)
	drone.stop()
	drone.land()

except (ManualControlException,Exception), e:

    print "ManualControlException"
    drone.land()








