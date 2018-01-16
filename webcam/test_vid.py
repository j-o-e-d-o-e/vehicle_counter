import cv2, time, tkinter
import numpy as np

camera = cv2.VideoCapture("../vid/rec2_8s.h264")
#window = tkinter.Tk()
BACK_SUB = cv2.createBackgroundSubtractorMOG2()
KERNEL = np.ones((5,5),np.uint8)
LEARNING_RATE = 0.1
MIN_CONTOUR_SIZE = 150
count = 0
found = False
pause = False
finished = False

def read():
    global found
    while True:
        handleInput()
        #updateWindow()
        if found:
            time.sleep(3)
            found = False
        elif finished:
            break
        elif not pause:
            ret,image = camera.read()
            if type(image).__module__ != np.__name__:
                print("END OF VIDEO.")
                break
            foreground = getForeground(image)
            cv2.line(image,(1000,1000),(1000,300),(0,0,255),40)
            detectVehicles(image,foreground)

            cv2.namedWindow("Foreground",cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Foreground", 600,600)
            cv2.imshow("Foreground", foreground)
            cv2.namedWindow("Main",cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Main", 600,600)
            cv2.imshow("Main",image)

    camera.release()
    cv2.destroyAllWindows()

def getForeground(image):
    gray = np.float32(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY))
    noisyForeground = BACK_SUB.apply(gray,None,LEARNING_RATE)
    cleanForeground = cv2.morphologyEx(noisyForeground,cv2.MORPH_OPEN,KERNEL)
    return cleanForeground

def detectVehicles(image,foreground):
    global count,found
    centroid = getCentroid(image,foreground)   
    for i in range(1000,1040): #range according to line thickness
        if centroid[0] == i:
            count += 1
            print("Vehicles found:",count)
            cv2.circle(image,centroid,20,(0,255,0),40)
            found = True

def getCentroid(image,foreground):
    centroidX = 0
    centroidY = 0
    img, contours, hierarchy = cv2.findContours(foreground,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for (i,contour) in enumerate(contours):
        (x,y,width,height) = cv2.boundingRect(contour)
        if (width >= MIN_CONTOUR_SIZE) and (height >= MIN_CONTOUR_SIZE):
            centroidX = x + int(width/2)
            centroidY = y + int(height/2)
            cv2.rectangle(foreground,(x,y),(x+width,y+height),(255,255,0))
            cv2.rectangle(image,(x,y),(x+width,y+height),(255,255,0))
            cv2.circle(image,(centroidX,centroidY),20,(255,0,0),40)
            #print(centroidX)
            break
    return (centroidX,centroidY)

def updateWindow():
    window.mainloop()

def handleInput():
    global finished, pause
    if cv2.waitKey(1) & 0xFF == ord("q"):
        finished = True
    elif (not pause) and (cv2.waitKey(1) & 0xFF == ord("p")):
        pause = True
        print("PAUSED")
    elif pause and (cv2.waitKey(1) & 0xFF == ord("c")):
        pause = False
        print("NOT PAUSED")

if __name__ == "__main__":
    read()
