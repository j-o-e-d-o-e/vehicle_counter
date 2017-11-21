from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2

#two methods to initialize background subtractor
back_sub = cv2.createBackgroundSubtractorMOG2()
#back_sub = cv2.bgsegm.createBackgroundSubtractorMOG()
learningRate = 0.1

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

def filter_mask(fg_mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    # Fill any small holes
    closing = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    # Remove noise
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

    # Dilate to merge adjacent blobs
    dilation = cv2.dilate(opening, kernel, iterations = 2)

    return dilation

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
for frame in stream:
        img = frame.array
        foreground = back_sub.apply(img, None, learningRate)
        foreground = filter_mask(foreground)

        cv2.imshow("Original",img)        
        cv2.imshow("Foreground",foreground)
        rawCapture.truncate(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

cv2.destroyAllWindows()

