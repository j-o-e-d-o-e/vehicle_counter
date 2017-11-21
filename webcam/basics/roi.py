import cv2
import numpy as np

img = cv2.imread("../../img/image.jpg")

roi = img[100:150,100:150]
img[50:100,50:100] = roi

img[100:150,100:150] = [255,255,255]

cv2.imshow("Image",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
