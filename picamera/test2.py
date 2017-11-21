import cv2
import time

cap = cv2.VideoCapture("recording.mp4")
cap.set(5,640)

while True:
    time.sleep(0.05)
    ret, frame = cap.read()

    cv2.imshow('video', frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
