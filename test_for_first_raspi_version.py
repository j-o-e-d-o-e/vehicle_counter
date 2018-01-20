import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

vc = PiCamera()
vc.framerate = 32
raw_capture = PiRGBArray(vc, size=(640, 480))
time.sleep(0.1)
stream = vc.capture_continuous(raw_capture, format="bgr", use_video_port=True)
print("DIBGS")
for frame in stream:
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    height, width = frame.shape[:2]
    image = cv2.resize(frame, (int(width * RESIZE_RATIO), int(height * RESIZE_RATIO)), interpolation=cv2.INTER_CUBIC)
    image = frame.array
    image.setflags(write=1)
    main_loop(image)
    rawCapture.truncate(0)
