import cv2
import numpy as np
import time

import VehicleInfo
# from VehicleDetector import VehicleDetector
from Vehicle import Vehicle
from Centroid import Centroid

KERNEL = np.ones((4, 4), np.uint8)  # 3, 4 or 5
LEARNING_RATE = 0.1  # -1 or 0.1 to 0.5
MIN_RECTANGLE_WIDTH = 150  # 100 to 200
MIN_RECTANGLE_HEIGHT = 100  # 100 to 200
WINDOW_SIZE = 970  # 600, 970 or 1150

image = []
vehicles = []
lastCentroids = []
current_centroids = []
count = 0
emptyScreens = 0
found = False
pause = False


def main():
    global pause, image, found, emptyScreens, lastCentroids, current_centroids
    camera = cv2.VideoCapture("../vid/rec2_8s.h264")
    backSubtractor = cv2.createBackgroundSubtractorMOG2()  # () or (detectShadows=False)
    # vehicleDetector = VehicleDetector.getInstance(backSubtractor)
    while True:
        if cv2.waitKey(1) & 0xFF == ord("p"):
            if pause:
                pause = False
            else:
                pause = True
        elif cv2.waitKey(1) & 0xFF == ord("q"):
            break
        elif found:
            time.sleep(3)
            found = False
        elif not pause:
            returnValue, image = camera.read()
            if not returnValue:
                break

            # get foreground containing the moving objects
            foreground = getForeground(backSubtractor)

            # get centroids of the moving objects from the last and current frame
            lastCentroids = currentCentroids
            currentCentroids = getCurrentCentroids(foreground)

            # add centroids to existing vehicles or create new vehicles
            addCentroidsToVehicles()

            # set direction of vehicles in order to better add centroids
            for vehicle in [v for v in vehicles if not v.getDirection() and len(v.getCentroids()) > 3]:
                vehicle.setDirection()

            # check if vehicles crossed the center line
            cv2.line(image, (VehicleInfo.MID_X, 300), (VehicleInfo.MID_X, 1000), VehicleInfo.RED)
            detectVehicles()

            # print and draw centroids
            print("CENTROIDS:", end=" ")
            for centroid in currentCentroids:
                print(centroid.getXY(), end=" ")
                centroid.draw(image)
            print()

            # print and draw vehicles
            for vehicle in vehicles:
                vehicle.print()
                vehicle.drawVehicleLine(image)

            # delete if found vehicles are off screen
            # if not lastCentroids and not currentCentroids:
            #     emptyScreens += 1
            #     print(emptyScreens)
            # for vehicle in [v for v in vehicles if v.isFound]:
            #     if emptyScreens >= 100:
            #         vehicles.remove(vehicle)
            #         emptyScreens = 0

            # for vehicle in [v for v in vehicles if v.isFound]:
            #     if  vehicle.isOffScreen(lastCentroids, currentCentroids):
            #         vehicles.remove(vehicle)

            # show windows:
            cv2.namedWindow("Main", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Main", WINDOW_SIZE, WINDOW_SIZE)
            cv2.imshow("Main", image)
            cv2.namedWindow("Foreground", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Foreground", WINDOW_SIZE, WINDOW_SIZE)
            cv2.imshow("Foreground", foreground)


    camera.release()
    cv2.destroyAllWindows()


def getForeground(backSubtractor):
    gray = np.float32(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    noisyForeground = backSubtractor.apply(gray, None, LEARNING_RATE)
    cleanForeground = cv2.morphologyEx(noisyForeground, cv2.MORPH_OPEN, KERNEL)
    return cleanForeground


def getCurrentCentroids(foreground):
    centroids = []
    _, contours, _ = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for pointSet in contours:
        x, y, width, height = cv2.boundingRect(pointSet)
        if width >= MIN_RECTANGLE_WIDTH and height >= MIN_RECTANGLE_HEIGHT:
            centroids.append(Centroid(x + int(width / 2), y + int(height / 2)))
    return centroids


def addCentroidsToVehicles():
    # add centroids to existing vehicles:
    for current in current_centroids:
        for vehicle in vehicles:
            if current.isNearBy(vehicle.getCentroid(-1), vehicle.getDirection()):
                vehicle.addCentroid(current)
                current_centroids.remove(current)
                break
    # add centroids to new vehicles:
    for current in current_centroids:
        for last in lastCentroids:
            if current.isNearBy(last):
                vehicles.append(Vehicle(last, current))


def detectVehicles():
    global count, found
    for vehicle in [v for v in vehicles if not v.isFound()]:
        startX = vehicle.getCentroid(0).getX()
        endX = vehicle.getCentroid(-1).getX()
        if startX > endX:
            order = -1
        else:
            order = 1
        for x in range(startX, endX, order):
            if x == VehicleInfo.MID_X:
                count += 1
                print("Vehicles found:", count)
                cv2.circle(image, vehicle.getCentroid(-1).getXY(), 10, VehicleInfo.GREEN, -1)
                found = True
                vehicle.setFound(True)
                break


if __name__ == "__main__":
    main()
