from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time, cv2

#detects corners of tic-tac-toe written on a sheet

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
camera.hflip = True
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
for frame in stream:
        image = frame.array
        image.setflags(write=1)

        result = image.copy()
        gray = np.float32(cv2.cvtColor(result,cv2.COLOR_BGR2GRAY)) 
        corners = cv2.dilate(cv2.cornerHarris(gray,2,3,0.04),None)
        result[corners>0.02*corners.max()]=[0,0,255]

        cv2.imshow("Original",image)
        cv2.imshow("Result",result)
        rawCapture.truncate(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

cv2.destroyAllWindows()

