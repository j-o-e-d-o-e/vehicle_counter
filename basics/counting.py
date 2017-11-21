from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2

#counts when white paper accesses circle

count = 0
focus = False

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
for frame in stream:
        img = frame.array
        
        cv2.circle(img,(300,200),8,(104,206,151))

        if focus == False and img[200,300,0]>100 and img[200,300,1]>100 and img[200,300,2]>100:
                count+=1
                print(count)
                focus = True

        if focus == True and img[200,300,0]<100 and img[200,300,1]<100 and img[200,300,2]<100:
                focus = False
        
        cv2.imshow("Original", img)
        rawCapture.truncate(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

cv2.destroyAllWindows()

