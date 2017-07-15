#!/usr/bin/python
import time
import cv2
import math
from bebop import *
from apyros.manual import myKbhit, ManualControlException

drone = Bebop()
drone.videoDisable() # disable video stream
drone.moveCamera( tilt=-90, pan=0 )

try:

	drone.takeoff()
	drone.calibrate(1,0)
	drone.land()

except (ManualControlException,Exception), e:

    print "ManualControlException"
    drone.land()








