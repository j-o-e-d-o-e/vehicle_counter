from picamera.array import PiRGBArray
from picamera import PiCamera
#import numpy as np
import time, cv2

#transforms pixels to white space & copies region of image

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
for frame in stream:
        image = frame.array
        image.setflags(write=1)

        #makes pixels white
        for j in range (500,600):
                for i in range(100,300):
                        image[i,j]=[255,255,255]

        #copies region of image
        image[0:150,0:150] = image[200:350,300:450]   
        
        #sets third BGR-value of pixel(400,150) to 100
        #image.itemset((400,150,2),100)

        """
        #gets color values of pixels
        print(image[400,150])
        print("Blue:", image[400,150,0], end=" ")
        print("Green:",image[400,150,1],end=" ")
        print("Red:",image.item(400,150,2),end="\n\n")
        """
        
        cv2.imshow("Original", image)       
        rawCapture.truncate(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

cv2.destroyAllWindows()

