from picamera import PiCamera
import time

camera = PiCamera()
camera.start_preview()
camera.start_recording('/home/pi/Desktop/opencv/vid/rec_16s.h264')
time.sleep(16)
camera.stop_recording()
camera.stop_preview()

#play: omxplayer /Desktop/video.h264
