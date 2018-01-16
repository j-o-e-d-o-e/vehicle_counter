import cv2
import numpy as np
import time

def getCentroid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return (cx, cy)

def start():
    cam = cv2.VideoCapture("../vid/rec2_8s.h264")
    back_sub = cv2.createBackgroundSubtractorMOG2()
    kernel = np.ones((5,5),np.uint8)
    learningRate = 0.5
    MIN_CONTOUR = 150
    count = 0
    found = False
    while True:
        ret,image = cam.read()
        if type(image).__module__ != np.__name__:
            print("END OF VIDEO.")
            break

        gray = np.float32(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY))
        foreground = back_sub.apply(gray, None, learningRate)
        opening = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, kernel)

        img, contours, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for (i, contour) in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            contour_valid = (w >= MIN_CONTOUR) and (h >= MIN_CONTOUR)
            if not contour_valid:
                continue
            centroid = getCentroid(x, y, w, h)
            cv2.circle(image,centroid,20,(255,0,0),40)
            #print(centroid[0]) #print x-coordinate

        cv2.line(image,(1000,1000),(1000,300),(0,0,255),40)
        for i in range(1000,1040): #range according to line thickness
            if i == centroid[0]:
                count += 1
                print("Vehicles found:",count)
                cv2.circle(image,centroid,20,(0,255,0),40)
                found = True

        cv2.namedWindow("Main",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Main", 600,600)
        cv2.imshow("Main",image)

##        cv2.namedWindow("Foreground[clean]",cv2.WINDOW_NORMAL)
##        cv2.resizeWindow("Foreground[clean]", 600,600)
##        cv2.imshow("Foreground[clean]", opening)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        elif found == True:
            time.sleep(3)
            found = False

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start()
