from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2

#morphological transformations like noise reduction around foreground objects

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
for frame in stream:
        img = frame.array

        kernel = np.ones((5,5),np.uint8)
        #erodes away the boundaries of foreground objects
        erosion = cv2.erode(img,kernel,iterations = 1)
        #increases size of foreground objects
        dilation = cv2.dilate(img,kernel,iterations = 1)

        #erosion followed by dilation (useful for removing noise around foreground obj)
        opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        #dilation followed by erosion (useful for closing holes in foreground obj)
        closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)       
        
        cv2.imshow("Original", img)
        cv2.imshow("Erosion", erosion)
        cv2.imshow("Dilation", dilation)
        cv2.imshow("Opening", opening)
        cv2.imshow("Closing", closing)
        rawCapture.truncate(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

cv2.destroyAllWindows()

