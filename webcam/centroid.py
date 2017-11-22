import cv2
import numpy as np
import time

cam = cv2.VideoCapture("../vid/recording_16s.mp4")
back_sub = cv2.createBackgroundSubtractorMOG2()
kernel = np.ones((5,5),np.uint8)
learningRate = 0.1
MIN_CONTOUR = 150
found = False
count = 0

def get_centroid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)

    cx = x + x1
    cy = y + y1

    return (cx, cy)

while True:
    ret,image = cam.read()

    gray = np.float32(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY))
    foreground = back_sub.apply(gray, None, learningRate)
    opening = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, kernel)
    cv2.line(image,(1000,1000),(1000,300),(0,0,255),40)

    img, contours, hierarchy = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for (i, contour) in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        contour_valid = (w >= MIN_CONTOUR) and (h >= MIN_CONTOUR)
        if not contour_valid:
            continue
        centroid = get_centroid(x, y, w, h)
        cv2.circle(image,centroid,55,(255,255,255))
        #print(centroid[0]) #print x-coordinate

    #range according to line thickness
    for i in range(1000,1040):
        if i == centroid[0]:
            count += 1
            print("Vehicles counted:",count)
            cv2.rectangle(image,(15,25),(200,150),(255,255,255))
            #cv2.circle(image,(100,100),100,(122,122,122))
            found = True

    cv2.namedWindow("Original",cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Original", 600,600)
    cv2.imshow("Original",image)
    if found == True:
        time.sleep(3)
        found = False

##    cv2.namedWindow("Foreground",cv2.WINDOW_NORMAL)
##    cv2.resizeWindow("Foreground", 600,600)
##    cv2.imshow("Foreground",foreground)
    
##    cv2.namedWindow("Opening",cv2.WINDOW_NORMAL)
##    cv2.resizeWindow("Opening", 600,600)
##    cv2.imshow("Opening", opening)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cam.release()
cv2.destroyAllWindows()
