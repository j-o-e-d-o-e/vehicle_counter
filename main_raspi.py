from threading import Thread
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import vehicle_counter_v1_3 as vc


class PiCam:
    def __init__(self, resolution=(320, 240), frame_rate=32):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = frame_rate
        self.raw_capture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.raw_capture,
                                                     format="bgr", use_video_port=True)
        self.frame = None
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        for frame in self.stream:
            self.frame = frame.array
            self.raw_capture.truncate(0)
            if self.stopped:
                self.stream.close()
                self.raw_capture.close()
                self.camera.close()
                return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


def main():
    vc.THRESHOLD = 20
    vc.CONTOUR_SIZE = 180
    vc.CONTOUR_X_DISTANCE = 40
    vc.CONTOUR_Y_DISTANCE = 10
    vc.LOCKON_DISTANCE = 70
    vc.VEHICLE_DISTANCE = 60
    vc.VEHICLE_TIMEOUT = 0.6
    vc.X_CENTER = 195

    cam = PiCam().start()
    time.sleep(2.0)
    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        else:
            frame = cam.read()
            vc.main(frame)

    cam.stop()
    cv2.destroyAllWindows()
    vc.file.close()
    print("Vehicles found total:", vc.vehicle_counter)

if __name__ == "__main__":
    main()
