import cv2
import time
import uuid
import numpy as np
import csv
from pathlib import Path

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
VEHICLE_TIMEOUT = 0.6
# Center on the x axis for the center line
X_CENTER = 400
# Barrier on the right and left side for speed tracking
X_LEFT = 200
X_RIGHT = 600
X_DIST = abs(X_LEFT - X_RIGHT)
# Distance between the two barriers for speed tracking for dir left and right
SPEED_DISTANCE_LEFT = 16.5
SPEED_DISTANCE_RIGHT = 15.5
# Constants for drawing on the frame
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
# For saving data to .csv-file
FILE_PATH = 'csv/vehicles.csv'
FIELDS = ['id', 'first_seen', 'speed', 'dir']

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


def main(frame):
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
    cv2.line(frame, (X_CENTER, 0), (X_CENTER, 400), RED)
    cv2.line(frame, (X_LEFT, 0), (X_LEFT, 400), WHITE)
    cv2.line(frame, (X_RIGHT, 0), (X_RIGHT, 400), YELLOW)
    if vehicles:
        detect_vehicles(frame)
        detect_speed()
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
    # _, contours, _ = cv2.findContours(processed_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours, _ = cv2.findContours(processed_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = filter(lambda c: cv2.contourArea(c) > CONTOUR_SIZE, contours)
    contours = [cv2.approxPolyDP(contour, EPSILON * cv2.arcLength(contour, True), True) for contour in contours]

    # for i, contour in enumerate(contours):
    #     cv2.drawContours(frame, [contour], -1, WHITE)
    #     text = "Contour " + str(i)
    #     cv2.putText(frame, text, (contour[0, 0, 0], contour[0, 0, 1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1,
    #                 cv2.LINE_AA)

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
                        break
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
                left_barrier=None,
                right_barrier=None,
                speed=None,
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
    global vehicle_counter
    for i in range(len(vehicles) - 1, -1, -1):
        if frame_time - vehicles[i]['last_seen'] > VEHICLE_TIMEOUT:
            print("Removing expired vehicle {}".format(vehicles[i]['id']))
            if vehicles[i]['found']:
                write_csv(vehicles[i])
            del vehicles[i]

    for vehicle in [v for v in vehicles if not v['found'] and len(v['track']) >= 4]:
        start_x = vehicle['track'][-1][0]
        end_x = vehicle['track'][0][0]
        if start_x > end_x:
            order = -1
        else:
            order = 1
        for x in range(start_x, end_x, order):
            if x == X_CENTER:
                vehicle_counter += 1
                vehicle['found'] = True
                print("Vehicles found:", vehicle_counter)
                cv2.circle(frame, vehicle['track'][0], 10, GREEN, -1)
                break


def write_csv(vehicle):
    file = Path(FILE_PATH)
    data = dict(
        id=vehicle['id'],
        first_seen=int(vehicle['first_seen']),
        speed=vehicle['speed'],
        dir=vehicle['dir']
    )
    if file.exists():
        file = open(FILE_PATH, 'a', newline='')
        csv_writer = csv.DictWriter(file, fieldnames=FIELDS)
    else:
        file = open(FILE_PATH, 'w', newline='')
        csv_writer = csv.DictWriter(file, fieldnames=FIELDS)
        csv_writer.writeheader()
    csv_writer.writerow(data)
    file.close()


def detect_speed():
    for vehicle in [v for v in vehicles if not v['speed']]:
        if vehicle['left_barrier'] and vehicle['right_barrier']:
            speed_time = round(abs(vehicle['left_barrier'] - vehicle['right_barrier']), 3)
            if vehicle['dir'] == 'left':
                gap_left = X_LEFT - list(filter(lambda t: t[0] < X_LEFT, vehicle['track']))[-1][0]
                gap_right = X_RIGHT - list(filter(lambda t: t[0] < X_RIGHT, vehicle['track']))[-1][0]
                factor = (X_DIST + gap_left - gap_right) / X_DIST
                vehicle['speed'] = round((SPEED_DISTANCE_LEFT * factor * 3600 / speed_time) / 1000, 2)
            else:
                gap_left = list(filter(lambda t: t[0] > X_LEFT, vehicle['track']))[-1][0] - X_LEFT
                gap_right = list(filter(lambda t: t[0] > X_RIGHT, vehicle['track']))[-1][0] - X_RIGHT
                factor = (X_DIST - gap_left + gap_right) / X_DIST
                vehicle['speed'] = round((SPEED_DISTANCE_RIGHT * factor * 3600 / speed_time) / 1000, 2)
                # print(f"{SPEED_DISTANCE_RIGHT} * {factor} * 3600 / {speed_time} / 1000")
            print("VEHICLE SPEED:", vehicle['speed'], "km/h")
        else:
            start_x = vehicle['track'][-1][0]
            end_x = vehicle['track'][0][0]
            if start_x > end_x:
                order = -1
            else:
                order = 1
            for x in range(start_x, end_x, order):
                if not vehicle['left_barrier'] and x == X_LEFT:
                    vehicle['left_barrier'] = frame_time
                if not vehicle['right_barrier'] and x == X_RIGHT:
                    vehicle['right_barrier'] = frame_time


def debug(frame):
    for vehicle in vehicles:
        cv2.line(frame, vehicle['track'][-1], vehicle['track'][0], RED)
        for centroid in vehicle['track']:
            cv2.circle(frame, centroid, 5, BLUE, -1)
    cv2.imshow("4 - DEBUG with information about tracked vehicles", frame)
