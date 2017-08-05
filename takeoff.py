#!/usr/bin/python
import time
import cv2
import math
from bebop import *
from apyros.manual import myKbhit, ManualControlException

timeDelay = 5
print 'Takeoff in %d seconds' % timeDelay
time.sleep(timeDelay)
root_height = 4
x_cor = 0.42*root_height
y_cor = 0.15*root_height
# level 1 first/second/third/fourth quadrant.
level1 = [\
[0.42*root_height,0.15*root_height,root_height/2],\
[-0.42*root_height,0.15*root_height,root_height/2],\
[-0.42*root_height,-0.42*root_height,root_height/2],\
[0.42*root_height,-0.42*root_height,root_height/2]]

# level 2

drone = Bebop()

try:

	drone.takeoff()
	drone.moveCamera( tilt=-90, pan=0 )

	# drone.wait(2)
	# drone.moveY(1,10)
	# drone.takePicture()
	# drone.stop()
	# drone.moveTo(x_cor,y_cor,root_height/2)
	# drone.moveTo(x_cor,y_cor,height/2)
	# drone.stop()
	drone.land()

except (ManualControlException,Exception), e:

    print "ManualControlException"
    drone.land()








