from picamera import PiCamera
from time import sleep

def flip(pos):
    if pos == True:
        return False
    else:
        return True

camera = PiCamera()
camera.start_preview()
camera.resolution = (100,100)

"""
for i in range(100):
    #camera.hflip = flip(camera.hflip)
    camera.rotation = i * 10
    sleep(0.1)

for effect in camera.IMAGE_EFFECTS:
    camera.image_effect = effect
    sleep(3)
camera.stop_preview()
"""
