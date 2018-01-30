import cv2
import vehicle_counter_v1_2 as vc


def main():
    cam = cv2.VideoCapture(0)
    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        return_value, frame = cam.read()
        if return_value:
            height, width = frame.shape[:2]
            frame = cv2.resize(frame, (int(width * 1.2), int(height * 0.9)),
                               interpolation=cv2.INTER_CUBIC)
        else:
            break
        vc.main(frame)
    cam.release()
    cv2.destroyAllWindows()
    vc.file.close()
    print("Vehicles found total:", vc.vehicle_counter)


if __name__ == "__main__":
    main()
