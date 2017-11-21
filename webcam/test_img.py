import cv2
import numpy as np

back_sub = cv2.createBackgroundSubtractorMOG2()
kernel = np.ones((5,5),np.uint8)
learningRate = 0.001

image = cv2.imread("../img/me.jpg")

foreground = back_sub.apply(image, None, learningRate)

#erodes away the boundaries of foreground objects
#erosion = cv2.erode(image,kernel,iterations = 1)
#increases size of foreground objects
#dilation = cv2.dilate(image,kernel,iterations = 1)

#erosion followed by dilation (useful for removing noise around foreground obj)
opening = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, kernel)   

cv2.imshow("Original",image)
cv2.imshow("Foreground",foreground)
cv2.imshow("Opening", opening)
#cv2.imshow("Erosion", erosion)
#cv2.imshow("Dilation", dilation)
cv2.waitKey(0)
cv2.destroyAllWindows()
