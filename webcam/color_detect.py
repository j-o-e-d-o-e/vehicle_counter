import cv2
import numpy as np

cam = cv2.VideoCapture(0)

while True:
    ret, image = cam.read()

    kernel = np.ones((5,5),np.uint8)
    #erodes away the boundaries of foreground objects
    erosion = cv2.erode(image,kernel,iterations = 1)
    #increases size of foreground objects
    dilation = cv2.dilate(image,kernel,iterations = 1)

    #erosion followed by dilation (useful for removing noise around foreground obj)
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    #dilation followed by erosion (useful for closing holes in foreground obj)
    closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)       
    
    cv2.imshow("Original", image)
    cv2.imshow("Erosion", erosion)
    cv2.imshow("Dilation", dilation)
    cv2.imshow("Opening", opening)
    cv2.imshow("Closing", closing)

    if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cam.release()
cv2.destroyAllWindows()
