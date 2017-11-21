import numpy as np
import time
import cv2

cam = cv2.VideoCapture(0)
back_sub = cv2.createBackgroundSubtractorMOG2()
learningRate = 0.1

while True:
    ret, image = cam.read()
    foreground = back_sub.apply(image, None, learningRate)

    cv2.imshow("Original",image)
    cv2.imshow("Foreground",foreground)

    if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cam.release()
cv2.destroyAllWindows()

