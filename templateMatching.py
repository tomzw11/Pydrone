import cv2
import numpy as np
from process import readImage

#img = cv2.imread('photos/Bebop2_20170624193338+0000.jpg',0) #negative
img = cv2.imread('photos/Bebop2_19700101000150+0000.jpg',0) #positive
#img = cv2.imread('field.jpg',0)

template = cv2.imread('book.png',0)
w, h = template.shape[::-1]

# Apply template Matching
res = cv2.matchTemplate(img,template,cv2.TM_SQDIFF)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

top_left = min_loc

bottom_right = (top_left[0] + w, top_left[1] + h)

cv2.rectangle(img,top_left, bottom_right, 255, 2)
print top_left
print bottom_right
res = res.astype(np.uint8)
readImage(res)
a1 = np.where(res>230)
print len(a1[0])

# cv2.imshow('output',img)
# cv2.waitKey(0)

