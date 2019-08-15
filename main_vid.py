import cv2
import vehicle_counter_v1_3 as vc

# A variable for the path of the video file
PATH_VIDEO = 'videos/rec2_16s.h264'
# A variable to pause/un-pause frame processing
pause = False


def main():
    global pause
    vc.SPEED_DISTANCE_LEFT = vc.SPEED_DISTANCE_RIGHT = 8
    cam = cv2.VideoCapture(PATH_VIDEO)
    while True:
        if cv2.waitKey(1) & 0xFF == ord("p"):
            if pause:
                pause = False
                print("UN-PAUSED")
            else:
                pause = True
                print("PAUSED")
        elif cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if pause:
            continue
        return_value, frame = cam.read()
        if return_value:
            height, width = frame.shape[:2]
            frame = cv2.resize(frame, (int(width * 0.4), int(height * 0.4)),
                               interpolation=cv2.INTER_CUBIC)
        else:
            break
        vc.main(frame)
    cam.release()
    cv2.destroyAllWindows()
    print("Vehicles found total:", vc.vehicle_counter)


if __name__ == "__main__":
    main()
