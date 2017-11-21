from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time, cv2

#detects the blue part of the contact lenses container

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
camera.hflip=True
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
for frame in stream:
        image = frame.array
        hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,np.array([100,50,50]),np.array([150,255,255]))
        #bitwise conjunction of two arrays/images:
        res = cv2.bitwise_and(image,image,mask=mask) 
        
        cv2.imshow("Original", image)
        #cv2.imshow("HSV", hsv)
        #cv2.imshow("Mask",mask)
        cv2.imshow("Result",res)

        rawCapture.truncate(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

cv2.destroyAllWindows()
