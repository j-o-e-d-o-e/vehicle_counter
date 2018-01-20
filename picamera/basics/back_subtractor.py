from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2

#two methods to initialize background subtractor
back_sub = cv2.createBackgroundSubtractorMOG2()
#back_sub = cv2.bgsegm.createBackgroundSubtractorMOG()

camera = PiCamera()
camera.resolution = (640, 480)
#camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

learningRate = 0.1

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
for frame in stream:
        img = frame.array
        foreground = back_sub.apply(img, None, learningRate)

        cv2.imshow("Original",img)        
        cv2.imshow("Foreground",foreground)
        rawCapture.truncate(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

cv2.destroyAllWindows()

