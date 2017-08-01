#!/usr/bin/python
import time
import cv2
import math
from bebop import *
from apyros.manual import myKbhit, ManualControlException

timeDelay = 5
print 'Takeoff in %d seconds' % timeDelay
time.sleep(timeDelay)
height = 4
x_cor = 3.36
y_cor = 1.2
drone = Bebop()
drone.moveCamera( tilt=-90, pan=0 )

try:

	drone.takeoff()
	# drone.moveTo(0,0,height)
	drone.moveTo(0,-1,1)
	# drone.stop()
	# drone.moveTo(-x_cor,y_cor,height/2)
	drone.stop()
	drone.land()

except (ManualControlException,Exception), e:

    print "ManualControlException"
    drone.land()








