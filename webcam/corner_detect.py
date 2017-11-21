import cv2
import numpy as np

cam = cv2.VideoCapture(0)

while True:
    ret, image = cam.read()
    image.setflags(write=1)

    result = image.copy()
    gray = np.float32(cv2.cvtColor(result,cv2.COLOR_BGR2GRAY))
    corners = cv2.dilate(cv2.cornerHarris(gray,2,3,0.04),None)
    result[corners>0.02*corners.max()]=[0,0,255]

    cv2.imshow("Original",image)
    cv2.imshow("Result",result)
    if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cam.release()
cv2.destroyAllWindows()
