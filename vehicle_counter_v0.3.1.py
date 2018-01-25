import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import uuid
import numpy as np

# Lower -> smaller changes are more readily detected
THRESHOLD_SENSITIVITY = 50  # default: 50
# The number of square pixels a contour must be before considering it a candidate for tracking
CONTOUR_SIZE = 300  # default: 500
# Higher -> contours consist of less points -> less computation
EPSILON = 0.05  # default: 0.01
# The maximum distance between vehicle and centroid to connect (in px)
LOCKON_DISTANCE = 80  # default: 80
# The minimum distance between an existing vehicle and a new vehicle
VEHICLE_DISTANCE = 350  # default: 350
# To filter instantaneous changes from the frame
KERNEL = (21, 21)
# How much the current frame impacts the average frame (higher -> more change and smaller differences)
AVERAGE_WEIGHT = 0.04  # default: 0.04
# How long a vehicle is allowed to sit around without having any new centroid
VEHICLE_TIMEOUT = 0.8  # default: 0.7
# Center on the x axis for the center line
X_CENTER = 384  # default: 400 (precisely, 384)
# Constants for drawing on the frame
RESIZE_RATIO = 0.4
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)

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
# A variable to store the counted vehicles
count = 0
# A variable to sleep for 3 secs if vehicle is found
found = False
# A variable to pause/unpause frame processing
pause = False


def main_pi():
    global cam, found
    cam = PiCamera()
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

        # print("WIDTH:", frame.shape[1])
        main_loop(frame)
        raw_capture.truncate(0)

    cv2.destroyAllWindows()
    print("Vehicles found total:", count)


def main():
    global cam, pause, found
    cam = cv2.VideoCapture('C:/Users/joe/Documents/programming/py/open_cv_desktop/videos/rec1_16s.h264')
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
            frame = cv2.resize(frame, (int(width * RESIZE_RATIO), int(height * RESIZE_RATIO)),
                               interpolation=cv2.INTER_CUBIC)
        else:
            break
        main_loop(frame)

    cam.release()
    cv2.destroyAllWindows()
    print("Vehicles found total:", count)


def main_loop(frame):
    global last_centroids, current_centroids, vehicles, frame_time
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

    if vehicles:
        detect_vehicles(frame)
    debug(frame)


def process_frame(frame):
    global avg_frame
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    _, _, gray_frame = cv2.split(hsv_frame)
    gray_frame = cv2.GaussianBlur(gray_frame, KERNEL, 0)
    # cv2.imshow("1 - GRAY", gray_frame)

    if avg_frame is None:
        avg_frame = gray_frame.copy().astype("float")
    cv2.accumulateWeighted(gray_frame, avg_frame, AVERAGE_WEIGHT)

    difference_frame = cv2.absdiff(gray_frame, cv2.convertScaleAbs(avg_frame))
    # cv2.imshow("2 - DIFFERENCE between current grayscale and average (also grayscale)", difference_frame)

    _, threshold_frame = cv2.threshold(difference_frame, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY)
    threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)
    # cv2.imshow("3 - THRESHOLD showing pixels of difference only if they are above threshold", threshold_frame)
    return threshold_frame


def aux_close(contour_1, contour_2):
    for point_1 in contour_1:
        for point_2 in contour_2:
            distance_x = abs(point_1[0][0] - point_2[0][0])
            distance_y = abs(point_1[0][1] - point_2[0][1])
            if distance_x < 300 and distance_y < 20:
                # print(True)
                return True
    # print(False)
    return False


def get_contours(frame, processed_frame):
    global pause
    _, contours, _ = cv2.findContours(processed_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = filter(lambda c: cv2.moments(c)['m00'] > CONTOUR_SIZE, contours)
    contours = [cv2.approxPolyDP(contour, EPSILON * cv2.arcLength(contour, True), True) for contour in contours]
    contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)

##    for i, contour in enumerate(contours):
##        cv2.drawContours(frame, [contour], -1, WHITE)
##        text = "Contour " + str(i)
##        cv2.putText(frame, text, (contour[0][0][0], contour[0][0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1,
##                    cv2.LINE_AA)

    if contours:
        groups = [[] for l in range(len(contours) - 1)]
        for i, contour_1 in enumerate(contours[:-1]):
            for j, contour_2 in enumerate(contours[i + 1:]):
                # print("Contour_" + str(i) + " and " + "Contour_" + str(i + 1 + j) + " are close?", end=" ")
                if aux_close(contour_1, contour_2):
                    groups[i].append(i + j + 1)

        # print("GROUPS:", groups)
        # e.g. GROUPS: [[1, 2], [2, 3], [3]]
        # Contour0 ist nah an 1 und 2, Contour1 ist nah an 2 und 3, Contour2 ist nah an 3
        # also ergibt sich: [0, 0, 0, 0], weil Contour1 0 und 3 miteinander verbindet

        group_indices = [0] * len(contours)
        change_holder = [True] + [False] * (len(contours) - 1)
        group_num = 0
        for i, group_1 in enumerate(groups):
            if change_holder[i]:
                index = group_indices[i]
            else:
                index = group_num
                group_indices[i] = index
                change_holder[i] = True
            if group_1 == []:
                group_num = index + 1
            for j in group_1:
                group_indices[j] = index
                change_holder[j] = True
            for group_2 in groups[i + 1:]:
                if any(k in group_1 for k in group_2):
                    for l in group_2:
                        group_indices[l] = index
                        change_holder[l] = True
                else:
                    group_num = index + 1
##            print("GROUP_NUM:", group_num)
##            print("GROUP_INDICES_IN_LOOP:", group_indices)
##            print("CHANGE_HOLDER:", change_holder, "\n")
        if not change_holder[-1]:
            group_indices[len(change_holder) - 1] = group_num

        merged_contours = []
        # print("GROUP_INDICES:", group_indices)
        for i in range(max(group_indices) + 1):
            contour_indices = [j for j, v in enumerate(group_indices) if v == i]
            # print("CONTOUR_INDICES", i, ":", contour_indices)
            if contour_indices:
                contour = np.vstack(contours[i] for i in contour_indices)
                merged_contour = cv2.convexHull(contour)
                merged_contours.append(merged_contour)
        # print()

        merged_contours = sorted(merged_contours, key=lambda c: cv2.contourArea(c), reverse=True)
        cv2.drawContours(frame, merged_contours, -1, GREEN, 2)
##        if len(contours) >= 3:
##            pause = True
        return merged_contours


def get_centroids(frame, contours):
    centroids = []
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        cx = int(x + width / 2)
        cy = int(y + height / 2)
        # better to use boundinRect instead of moments to avoid zero-division
        # moments = cv2.moments(contour)
        # cx = int(moments['m10'] / moments['m00'])
        # cy = int(moments['m01'] / moments['m00'])
        cv2.circle(frame, (cx, cy), 10, RED, -1)
        centroids.append((cx, cy))
    return centroids


def add_centroids_to_vehicles():
    centroids = current_centroids.copy()
    # print("\nCENTROIDS:", centroids)
    if vehicles:
        for vehicle in vehicles:
            for current in centroids:
                distance = cv2.norm(current, vehicle['track'][0])
                if distance < LOCKON_DISTANCE:
                    if (vehicle['dir'] == 'left' and vehicle['track'][0][0] > current[0]) or (
                                    vehicle['dir'] == 'right' and vehicle['track'][0][0] < current[0]):
                        vehicle['track'].insert(0, current)
                        vehicle['last_seen'] = frame_time
                        # print("CENTROID TO BE REMOVED:", current)
                        centroids.remove(current)
        if centroids:
            # print("REMAINING CENTROIDS:", centroids)
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
    for i in range(len(vehicles) - 1, -1, -1):
        if frame_time - vehicles[i]['last_seen'] > VEHICLE_TIMEOUT:
            print("Removing expired vehicle {}".format(vehicles[i]['id']))
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
                count += 1
                print("Vehicles found:", count)
                cv2.circle(frame, vehicle['track'][0], 10, GREEN, -1)
                found = True
                vehicle['found'] = True
                break


def debug(frame):
    for vehicle in vehicles:
        cv2.line(frame, vehicle['track'][-1], vehicle['track'][0], RED)
        for centroid in vehicle['track']:
            cv2.circle(frame, centroid, 5, BLUE, -1)

    cv2.imshow("4 - PREVIEW containing information about tracked vehicles", frame)


if __name__ == "__main__":
    main_pi()
