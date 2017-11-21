from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

#draws line & rectangle

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
for frame in stream:
        img= frame.array

        cv2.line(img,(300,200),(400,300),(104,206,151),4)
        cv2.rectangle(img,(300,200),(400,300),(0,0,255),1)
        
        cv2.imshow("Original", img) 
        rawCapture.truncate(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

cv2.destroyAllWindows()

