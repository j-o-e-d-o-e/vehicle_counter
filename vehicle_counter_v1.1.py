import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import uuid
import numpy as np
import csv

# Lower -> smaller changes are more readily detected
THRESHOLD = 50
# The number of square pixels a contour must have to be considered a candidate for tracking
CONTOUR_SIZE = 500
# Higher -> contours consist of less points
EPSILON = 0.05
# The maximum distance between the points of two contours to be considered close
CONTOUR_X_DISTANCE = 300
CONTOUR_Y_DISTANCE = 20
# The maximum distance between vehicle and centroid to connect
LOCKON_DISTANCE = 120
# The minimum distance between an existing vehicle and a new vehicle
VEHICLE_DISTANCE = 350
# To filter instantaneous changes from the frame
KERNEL = (21, 21)
# How much the current frame impacts the average frame
AVERAGE_WEIGHT = 0.04
# How long a vehicle is allowed to sit around without having any new centroid
VEHICLE_TIMEOUT = 0.8
# Center on the x axis for the center line
X_CENTER = 400
# Center on the y axis which separates the two lanes
Y_CENTER = 250
# Constants for drawing on the frame
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
# A variable for the path of the video file
PATH_VIDEO = '../vehicle_counter_desktop/videos/rec2_8s.h264'

# A variable to store the video capture or the pi camera
cam = None
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
# A variable to store the vehicle count
vehicle_counter = 0
# A variable to sleep for 3 secs if vehicle is found
found = False
# A variable to pause/unpause frame processing
pause = False

# For saving data to .csv-file
file = open('vehicle_counter.csv', 'w', newline='')
fields = ['id', 'first_seen', 'last_seen', 'dir', 'found', 'track']
csv_writer = csv.DictWriter(file, fieldnames=fields)
csv_writer.writeheader()


def main_pi():
    global cam
    cam = PiCamera()
    # cam.framerate = 32
    cam.resolution = (640, 480)
    raw_capture = PiRGBArray(cam, size=(640, 480))
    time.sleep(0.1)
    stream = cam.capture_continuous(raw_capture, format="bgr", use_video_port=True)
    for frame in stream:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        height, width = frame.array.shape[:2]
        frame = cv2.resize(frame.array, (int(width * 1.2), int(height * 0.9)),
                           interpolation=cv2.INTER_CUBIC)
        main_loop(frame)
        raw_capture.truncate(0)


def main_cam():
    global cam
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
        main_loop(frame)
    cam.release()


def main_vid():
    global cam, pause, found
    cam = cv2.VideoCapture(PATH_VIDEO)
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
        return_value, frame = cam.read()
        if return_value:
            height, width = frame.shape[:2]
            frame = cv2.resize(frame, (int(width * 0.4), int(height * 0.4)),
                               interpolation=cv2.INTER_CUBIC)
        else:
            break
        main_loop(frame)
    cam.release()


def main_loop(frame):
    global frame_time, last_centroids, current_centroids
    frame_time = time.time()
    processed_frame = process_frame(frame)
    contours = get_contours(frame, processed_frame)
    if contours:
        last_centroids = current_centroids
        current_centroids = get_centroids(frame, contours)
    else:
        last_centroids = current_centroids = []
    if last_centroids and current_centroids:
        add_centroids_to_vehicles()
    cv2.line(frame, (X_CENTER, 100), (X_CENTER, 400), RED)
    # cv2.line(frame, (100, Y_CENTER), (800, Y_CENTER), RED)
    if vehicles:
        detect_vehicles(frame)
    debug(frame)


def process_frame(frame):
    global avg_frame
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    _, _, gray_frame = cv2.split(hsv_frame)
    gray_frame = cv2.GaussianBlur(gray_frame, KERNEL, 0)

    if avg_frame is None:
        avg_frame = gray_frame.copy().astype("float")
    cv2.accumulateWeighted(gray_frame, avg_frame, AVERAGE_WEIGHT)

    difference_frame = cv2.absdiff(gray_frame, cv2.convertScaleAbs(avg_frame))
    # cv2.imshow("1 - DIFFERENCE between the average and current frame", difference_frame)

    _, threshold_frame = cv2.threshold(difference_frame, THRESHOLD, 255, cv2.THRESH_BINARY)
    threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)
    # cv2.imshow("2 - THRESHOLD with clean shapes of the moving objects", threshold_frame)
    return threshold_frame


def get_contours(frame, processed_frame):
    global pause
    _, contours, _ = cv2.findContours(processed_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = filter(lambda c: cv2.contourArea(c) > CONTOUR_SIZE, contours)
    contours = [cv2.approxPolyDP(contour, EPSILON * cv2.arcLength(contour, True), True) for contour in contours]

    for i, contour in enumerate(contours):
        cv2.drawContours(frame, [contour], -1, WHITE)
        text = "Contour " + str(i)
        cv2.putText(frame, text, (contour[0, 0, 0], contour[0, 0, 1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1,
                    cv2.LINE_AA)

    if contours:
        contours = aux_merge_contours(contours, len(contours) - 1)
        contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)
        cv2.drawContours(frame, contours, -1, GREEN, 2)
    return contours


def aux_merge_contours(contours, iterations):
    count = 0
    while count < iterations:
        clip_board = []
        is_added = [False] * len(contours)
        for i, contour_1 in enumerate(contours[:-1]):
            if aux_close(contour_1, contours[i + 1]):
                merged_contour = np.vstack((contour_1, contours[i + 1]))
                merged_contour = cv2.convexHull(merged_contour)
                clip_board.append(merged_contour)
                is_added[i] = True
            else:
                if not is_added[i]:
                    clip_board.append(contour_1)
                    is_added[i] = True
                if i == len(contours) - 2:
                    clip_board.append(contours[-1])
        contours = clip_board.copy()
        count += 1
    return contours


def aux_close(contour_1, contour_2):
    for point_1 in contour_1:
        for point_2 in contour_2:
            if not (point_1[0, 1] < Y_CENTER < point_2[0, 1] or point_1[0, 1] > Y_CENTER > point_2[0, 1]):
                distance_x = abs(point_1[0, 0] - point_2[0, 0])
                distance_y = abs(point_1[0, 1] - point_2[0, 1])
                if distance_x < CONTOUR_X_DISTANCE and distance_y < CONTOUR_Y_DISTANCE:
                    return True
    return False


def get_centroids(frame, contours):
    centroids = []
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        cx = int(x + width / 2)
        cy = int(y + height / 2)
        cv2.circle(frame, (cx, cy), 10, RED, -1)
        centroids.append((cx, cy))
    return centroids


def add_centroids_to_vehicles():
    candidates = current_centroids.copy()
    if vehicles:
        for vehicle in vehicles:
            for centroid in candidates:
                distance = cv2.norm(centroid, vehicle['track'][0])
                if distance < LOCKON_DISTANCE:
                    if (vehicle['dir'] == 'left' and vehicle['track'][0][0] > centroid[0]) or (
                                    vehicle['dir'] == 'right' and vehicle['track'][0][0] < centroid[0]):
                        vehicle['track'].insert(0, centroid)
                        vehicle['last_seen'] = frame_time
                        candidates.remove(centroid)
        if candidates:
            for centroid in candidates:
                if all(cv2.norm(centroid, vehicle['track'][0]) > VEHICLE_DISTANCE for vehicle in vehicles):
                    add_new_vehicle(centroid)
    else:
        for centroid in current_centroids:
            add_new_vehicle(centroid)


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
    global vehicle_counter, found
    for i in range(len(vehicles) - 1, -1, -1):
        if frame_time - vehicles[i]['last_seen'] > VEHICLE_TIMEOUT:
            print("Removing expired vehicle {}".format(vehicles[i]['id']))
            if vehicles[i]['found']:
                csv_writer.writerow(vehicles[i])
            del vehicles[i]

    for vehicle in [v for v in vehicles if not v['found']]:
        start_x = vehicle['track'][-1][0]
        end_x = vehicle['track'][0][0]
        if start_x > end_x:
            order = -1
        else:
            order = 1
        for x in range(start_x, end_x, order):
            if x == X_CENTER:
                vehicle_counter += 1
                print("Vehicles found:", vehicle_counter)
                cv2.circle(frame, vehicle['track'][0], 10, GREEN, -1)
                found = True
                vehicle['found'] = True
                break


def debug(frame):
    for vehicle in vehicles:
        cv2.line(frame, vehicle['track'][-1], vehicle['track'][0], RED)
        for centroid in vehicle['track']:
            cv2.circle(frame, centroid, 5, BLUE, -1)
    cv2.imshow("4 - PREVIEW with information about tracked vehicles", frame)


if __name__ == "__main__":
    main_pi()
    cv2.destroyAllWindows()
    file.close()
    print("Vehicles found total:", vehicle_counter)
