import cv2
import numpy as np

img = cv2.imread("img/nice.jpg")

roi = img[290:350, 200:325]
img[100:160,100:225] = roi

img[312:328, 220:310] = [255,255,255]

cv2.imshow("Image",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
