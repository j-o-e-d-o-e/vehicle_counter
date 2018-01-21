import cv2
# from picamera.array import PiRGBArray
# from picamera import PiCamera
import time
import uuid

# To filter instantious changes from the frame
KERNEL = (21, 21)
# Lower -> smaller changes are more readily detected
THRESHOLD_SENSITIVITY = 50  # default: 50
# The number of square pixels a contour must be before considering it a candidate for tracking
CONTOUR_SIZE = 500  # default: 500
# How much the current frame impacts the average frame (higher -> more change and smaller differences)
AVERAGE_WEIGHT = 0.04
# The maximum distance between vehicle and centroid to connect (in px)
LOCKON_DISTANCE = 80  # default: 80
# The minimum distance between an existing vehicle and a new vehicle
VEHICLE_DISTANCE = 350  # default: 350
# How long a vehicle is allowed to sit around without having any new centroid
VEHICLE_TIMEOUT = 0.7
# Center on the x axis for desktop and for raspberry
X_CENTER = 400 #320
# Constants for drawing on the frame
RESIZE_RATIO = 0.4
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)

# A variable to store the video capture or the pi camera
vc = None
# A variable to store the time when a frame was created
frame_time = None
# A variable to store the running average
avg_frame = None
# A list of centroids from the current frame
current_centroids = []
# A list of centroids from the last frame
last_centroids = []
# A list of tracked vehicles
vehicles = []
# A variable to store the counted vehicles
count = 0
# A variable to sleep for 3 secs if vehicle is found
found = False
# A variable to pause/unpause frame processing
pause = False
"""
def main_pi():
    global vc, found
    vc = PiCamera()
    vc.resolution = (640, 480)
    # vc.framerate = 32
    raw_capture = PiRGBArray(vc, size=(640, 480))
    time.sleep(0.1)
    stream = vc.capture_continuous(raw_capture, format="bgr", use_video_port=True)
    for frame in stream:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if found:
            time.sleep(3)
            found = False
        image = frame.array
        #image.setflags(write=1)
        main_loop(image)
        #key = cv2.waitKey(1) & 0xFF
        raw_capture.truncate(0)

    cv2.destroyAllWindows()
"""


def main():
    global vc, pause, found
    vc = cv2.VideoCapture('C:/Users/joe/Documents/programming/py/open_cv_desktop/videos/rec2_16s.h264')
    while True:
        if cv2.waitKey(1) & 0xFF == ord("p"):
            if pause:
                pause = False
                print("UNPAUSED")
            else:
                pause = True
                print("PAUSED")
        elif cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if pause:
            continue
        if found:
            time.sleep(3)
            found = False
        grabbed, frame = get_frame()
        if not grabbed:
            break
        main_loop(frame)

    vc.release()
    cv2.destroyAllWindows()
    print("Vehicles found total:", count)


def get_frame():
    # Grab a frame from the video capture and resizes it
    rval, frame = vc.read()
    if rval:
        height, width = frame.shape[:2]
        frame = cv2.resize(frame, (int(width * RESIZE_RATIO), int(height * RESIZE_RATIO)),
                           interpolation=cv2.INTER_CUBIC)
    return rval, frame


def main_loop(frame):
    global last_centroids, current_centroids, vehicles, frame_time
    frame_time = time.time()
    processed_frame = process_frame(frame)
    last_centroids = current_centroids
    current_centroids = get_centroids(frame, processed_frame)
    if current_centroids:
        # connect_centroids_to_vehicles()
        add_centroids_to_vehicles()

    # Draw center line
    cv2.line(frame, (X_CENTER, 100), (X_CENTER, 400), RED)

    if vehicles:
        detect_vehicles(frame)
    debug(frame)


def process_frame(frame):
    global avg_frame
    # Convert the frame to Hue Saturation Value (HSV) color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Only use the Value channel of the frame
    _, _, gray_frame = cv2.split(hsv_frame)
    # Apply a blur to the frame to smooth out any instantaneous changes
    # like leaves glinting in sun or birds flying around
    gray_frame = cv2.GaussianBlur(gray_frame, KERNEL, 0)

    if avg_frame is None:
        # Set up the average if this is the first time through
        avg_frame = gray_frame.copy().astype("float")

    # Build the average scene image by accumulating this frame
    # with the existing average
    cv2.accumulateWeighted(gray_frame, avg_frame, AVERAGE_WEIGHT)
    # cv2.imshow("1 - AVERAGE accumulating current grayscales", cv2.convertScaleAbs(avg_frame))

    # Compute the grayscale difference between the current grayscale frame and
    # the average of the scene
    difference_frame = cv2.absdiff(gray_frame, cv2.convertScaleAbs(avg_frame))
    # cv2.imshow("2 - DIFFERENCE between current grayscale and average (also grayscale)", difference_frame)

    # Apply a threshold to the difference: any pixel value above the sensitivity
    # value will be set to 255 and any pixel value below will be set to 0
    # -> found object is white, background is black
    _, threshold_frame = cv2.threshold(difference_frame, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY)
    threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)
    # cv2.imshow("3 - THRESHOLD showing pixels of difference only if they are above threshold", threshold_frame)
    return threshold_frame


def get_centroids(frame, processed_frame):
    # Find contours in the processed frame
    _, contours, _ = cv2.findContours(processed_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, BLUE, 3)

    # Filter out the contours that are too small to be considered vehicles
    contours = filter(lambda c: cv2.moments(c)['m00'] > CONTOUR_SIZE, contours)
    centroids = []
    for contour in contours:
        moments = cv2.moments(contour)
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])
        cv2.circle(frame, (cx, cy), 10, RED, -1)
        centroids.append((cx, cy))
    return centroids


def add_centroids_to_vehicles():
    centroids = current_centroids.copy()
    if vehicles:
        for vehicle in vehicles:
            for current in centroids:
                distance = cv2.norm(current, vehicle['track'][0])
                if distance < LOCKON_DISTANCE:
                    if (vehicle['dir'] == 'left' and vehicle['track'][0][0] > current[0]) or (
                                    vehicle['dir'] == 'right' and vehicle['track'][0][0] < current[0]):
                        vehicle['track'].insert(0, current)
                        vehicle['last_seen'] = frame_time
                        centroids.remove(current)
        if centroids:
            for current in centroids:
                if all(cv2.norm(current, vehicle['track'][0]) > VEHICLE_DISTANCE for vehicle in vehicles):
                    add_new_vehicle(current)
    else:
        for current in current_centroids:
            add_new_vehicle(current)


def add_new_vehicle(current):
    for last in last_centroids:
        distance = cv2.norm(current, last)
        if distance < LOCKON_DISTANCE:
            vehicle = dict(
                id=str(uuid.uuid4())[:8],
                first_seen=frame_time,
                last_seen=frame_time,
                dir=None,
                found=False,
                track=[current, last],
            )
            if current[0] < last[0]:
                vehicle['dir'] = 'left'
            else:
                vehicle['dir'] = 'right'
            vehicles.append(vehicle)
            print("Vehicles currently tracked:", len(vehicles))


def detect_vehicles(frame):
    global count, found
    # Delete vehicles that haven't been seen in some amount of time
    for i in range(len(vehicles) - 1, -1, -1):
        if frame_time - vehicles[i]['last_seen'] > VEHICLE_TIMEOUT:
            print("Removing expired vehicle {}".format(vehicles[i]['id']))
            del vehicles[i]

    # Detect vehicles crossing the center line
    for vehicle in [v for v in vehicles if not v['found']]:
        start_x = vehicle['track'][-1][0]
        end_x = vehicle['track'][0][0]
        if start_x > end_x:
            order = -1
        else:
            order = 1
        for x in range(start_x, end_x, order):
            if x == X_CENTER:
                count += 1
                print("Vehicles found:", count)
                cv2.circle(frame, vehicle['track'][0], 10, GREEN, -1)
                found = True
                vehicle['found'] = True
                break


def debug(frame):
    # Draw information about the vehicles on the screen
    for vehicle in vehicles:
        cv2.line(frame, vehicle['track'][-1], vehicle['track'][0], RED)
        for centroid in vehicle['track']:
            cv2.circle(frame, centroid, 5, BLUE, -1)

    cv2.imshow("4 - PREVIEW containing information about tracked vehicles", frame)


if __name__ == "__main__":
    main()
