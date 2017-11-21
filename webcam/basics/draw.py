import cv2
import numpy as np
import time

cap = cv2.VideoCapture("../../vid/output.avi")

while True:
    ret, frame = cap.read()

    draw = frame.copy()
    cv2.line(draw,(0,0),(150,150),(255,255,255))
    cv2.rectangle(draw,(15,25),(200,150),(255,255,255))
    cv2.circle(draw,(100,63),55,(255,255,255))
    time.sleep(0.1)

    #cv2.imshow("Original",frame)
    cv2.imshow("Draw",draw)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
