from picamera import PiCamera
import time

camera = PiCamera()
camera.resolution = (100,100)
camera.framerate=30
camera.start_preview()
camera.start_recording('/home/pi/Desktop/recording.h264')
time.sleep(8)
camera.stop_recording()
camera.stop_preview()

#play: omxplayer /Desktop/video.h264
