import cv2
import numpy as np
import time

from Vehicle import Vehicle

KERNEL = np.ones((5, 5), np.uint8)
LEARNING_RATE = 0.1
MIN_RECTANGLE_SIZE = 150
LINE_X = 1000
LINE_START = (1000, 1000)
LINE_END = (1000, 300)
RED = [0, 0, 255]
BLUE = [255, 0, 0]
GREEN = [0, 255, 0]
WHITE = [255, 255, 255]
CIRCLE_RADIUS = 5
THICKNESS = 10
WINDOW_SIZE = 1150
X_DEVIATION = 120
Y_DEVIATION = 20

camera = cv2.VideoCapture("../vid/rec1_16s.h264")
back_sub = cv2.createBackgroundSubtractorMOG2()
count = 0
found = False
last_centroid = []
current_centroid = []
vehicles = []


def main():
    global found
    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        elif found:
            time.sleep(3)
            found = False
        else:
            return_value, image = camera.read()
            if not return_value:
                print("END OF VIDEO.")
                for vehicle in vehicles:
                    print(vehicle.get_all_centroids())
                break
            foreground = getForeground(image)
            detectVehicles(image, foreground)

            if vehicles:
                vehicles[-1].draw_vehicle_line(image, WHITE)

            # draw crossing line:
            cv2.line(image, LINE_START, LINE_END, RED, THICKNESS)
            # show windows:
            cv2.namedWindow("Main", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Main", WINDOW_SIZE, WINDOW_SIZE)
            cv2.imshow("Main", image)
            # cv2.namedWindow("Foreground", cv2.WINDOW_NORMAL)
            # cv2.resizeWindow("Foreground", WINDOW_SIZE, WINDOW_SIZE)
            # cv2.imshow("Foreground", foreground)

    camera.release()
    cv2.destroyAllWindows()


def getForeground(image):
    gray = np.float32(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    noisyForeground = back_sub.apply(gray, None, LEARNING_RATE)
    cleanForeground = cv2.morphologyEx(noisyForeground, cv2.MORPH_OPEN, KERNEL)
    return cleanForeground


def detectVehicles(image, foreground):
    global count, found, last_centroid, current_centroid
    if current_centroid:
        last_centroid = current_centroid
    current_centroid = getCentroid(foreground)
    if last_centroid:
        identify_current_centroid()
    if vehicles and not vehicles[-1].getFound():
        first_x = vehicles[-1].get_centroid(0)[0]
        last_x = vehicles[-1].get_centroid(-1)[0]
        if first_x > last_x:
            x2 = first_x
            x1 = last_x
        else:
            x1 = first_x
            x2 = last_x
        for x in range(x1, x2):
            if x == LINE_X:
                count += 1
                print("Vehicle found:", count)
                cv2.circle(image, current_centroid, CIRCLE_RADIUS + 10, GREEN, THICKNESS)
                found = True
                vehicles[-1].setFound(True)
                break


def getCentroid(foreground):
    centroidX, centroidY = 0, 0
    img, contours, hierarchy = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # each point_set may vary in size
    for point_set in contours:
        x, y, width, height = cv2.boundingRect(point_set)
        # make sure the resulting rectangle is large enough
        # for instance, there may be small point_sets resulting in too small rectangles
        # meaning an object has not been detected there
        if (width >= MIN_RECTANGLE_SIZE) and (height >= MIN_RECTANGLE_SIZE):
            centroidX = x + int(width / 2)
            centroidY = y + int(height / 2)
    return centroidX, centroidY


def identify_current_centroid():
    if current_centroid_nearby(last_centroid[0], last_centroid[1]):
        if not vehicles:
            # first vehicle:
            vehicles.append(Vehicle(current_centroid))
        else:
            last_vehicle_centroid = vehicles[-1].get_centroid(-1)
            if current_centroid_nearby(last_vehicle_centroid[0], last_vehicle_centroid[1]):
                # current vehicle:
                vehicles[-1].add_centroid(current_centroid)
            else:
                # new vehicle:
                vehicles.append(Vehicle(current_centroid))


def current_centroid_nearby(x, y):
    if (x - X_DEVIATION) < current_centroid[0] < (x + X_DEVIATION) and \
                            (y - Y_DEVIATION) < current_centroid[1] < (y + Y_DEVIATION):
        return True
    else:
        return False


if __name__ == "__main__":
    main()
