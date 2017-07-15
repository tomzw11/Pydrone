#!/usr/bin/python
import time
import cv2
import numpy as np

from process import findColor
from ftplib import FTP
from bebop import *

drone = Bebop()
drone.videoDisable() # disable video stream
drone.moveCamera( tilt=-100, pan=0 )
ftp = FTP('192.168.42.1')   # connect to host, default port
ftp.login()               
ftp.cwd('internal_000/Bebop_2/media')
ftp.retrlines('LIST')

filenames_all = ftp.nlst() # get filenames within the directory
for filename in filenames_all:

	ftp.delete(filename) # clear past files/screenshots/videos


try:

	drone.takeoff()
	drone.takePicture()
	for i in xrange(5):

		drone.wait(1)
		print 'round',i
		try:
				drone.takePicture()
				filenames_all = ftp.nlst() # get filenames within the directory
				filenames = [k for k in filenames_all if '.jpg' in k]
				#print filenames
				filename = filenames[-1]
				print filename
				ftp.retrbinary("RETR " + filename ,open(filename, 'wb').write)
				frame = cv2.imread(filename)
				if findColor(frame)==False:
					print "no object found"
					drone.update( cmd=movePCMDCmd( True, 0, 10, 0, 0 ) )
				else:
					print "object found"
					drone.hover()
					drone.flyToAltitude(1.5,2)
					drone.wait(2)
					drone.land()
					break

					    #does it need to login and quit ftp everytime?

		except Exception, e:
				print 'download error' 
				ftp.quit()
				drone.land()

	ftp.quit()
	drone.land()
   
except (ManualControlException,Exception), e:
    print
    print "Emergency Landing"
	ftp.quit()
	drone.land()

def flyBackwards():

	drone.wait(1)
	for i in xrange(3):
		drone.update( cmd=movePCMDCmd( True, 0, -10, 0, 0 ) )
		drone.wait(1)



# use pcmd commands+ drone.update() to set up video stream and more functions? 

# cv2.imshow('image',output)
# cv2.waitKey(0)
# cv2.destroyAllWindows()