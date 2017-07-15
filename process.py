#!/usr/bin/python
import sys
import cv2
import numpy as np

def findColor(frame):

	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	lower = np.array([15, 210, 20],dtype = "uint8")
	upper = np.array([35, 255, 255],dtype = "uint8")
	mask = cv2.inRange(frame,lower,upper)
	cnt = np.sum(mask)
	if cnt/255 < 800:
		print("yellow not found = ",cnt/255)
		return False
	else:
		print("found yellow = ",cnt/255)
		return True

	# output = cv2.bitwise_and(frame, frame, mask = mask)

def readImage(frame):

	print 'frame shape = ',frame.shape
	print 'frame size = ', frame.size
	print 'data type = ', frame.dtype
	print 'max pixel = ', np.amax(frame)
	print 'min pixel = ', np.amin(frame)
	cv2.imshow('frame',frame)
	cv2.waitKey(0)

def Canny(frame):

	edges = cv2.Canny(frame,100,200)

	cv2.imshow('frame',edges)
	cv2.waitKey(0)

def Contour(frame):

	ret, thresh = cv2.threshold(frame, 0,255,0)

	contours,heirarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cnt = contours[0]
	print cnt
	M = cv2.moments(cnt)
	epsilon = 0.1*cv2.arcLength(cnt,True)
	approx = cv2.approxPolyDP(cnt,epsilon,True)
	print len(approx)

if __name__ == "__main__":

    filename=sys.argv[1]
    frame = cv2.imread(filename)
    findColor(frame)
    #readImage(frame)
    #Canny(frame)
    #Contour(frame)














