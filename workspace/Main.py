import cv2
import numpy as np
import time

import VehicleInfo
from Vehicle import Vehicle
from Centroid import Centroid

KERNEL = np.ones((4, 4), np.uint8)  # 3, 4 or 5
LEARNING_RATE = 0.1  # -1 or 0.1 to 0.5
MIN_RECTANGLE_SIZE = 150  # 100 to 200
WINDOW_SIZE = 970  # 600, 970 or 1150

image = []
vehicles = []
lastCentroids = []
currentCentroids = []
count = 0
found = False


def main():
    global image, found, lastCentroids, currentCentroids
    camera = cv2.VideoCapture("../vid/rec1_8s.h264")
    backSubtractor = cv2.createBackgroundSubtractorMOG2()  # () or (detectShadows=False)
    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        elif found:
            time.sleep(3)
            found = False
        else:
            returnValue, image = camera.read()
            if not returnValue:
                break

            # get foreground containing the moving objects
            foreground = getForeground(backSubtractor)

            # get centroids of the moving objects from the foreground
            lastCentroids = currentCentroids
            currentCentroids = getCurrentCentroids(foreground)

            # print and draw centroids
            # for centroid in currentCentroids:
            # centroid.draw(image)
            # print(centroid.getXY())

            # set direction of vehicles to better add centroids to these
            for vehicle in [vehicle for vehicle in vehicles if not vehicle.getDirection()]:
                vehicle.setDirection()

            # delete found vehicles if they are finished
            for vehicle in [vehicle for vehicle in vehicles if vehicle.isFound and not vehicle.isFinished()]:
                vehicle.setFinished()
            for vehicle in [vehicle for vehicle in vehicles if vehicle.isFinished()]:
                vehicle.print()
                #vehicles.remove(vehicle)

            # add centroids to vehicles, create new vehicles or dismiss centroids
            if lastCentroids and currentCentroids:
                addCentroidsToVehicles()

            # check if vehicles crossed the line
            cv2.line(image, (VehicleInfo.MIDDLE_X, 300), (VehicleInfo.MIDDLE_X, 1000), VehicleInfo.RED)
            detectVehicles()

            # draw vehicle lines:
            for vehicle in [vehicle for vehicle in vehicles if not vehicle.isFinished()]:
                vehicle.drawVehicleLine(image)

            # show windows:
            cv2.namedWindow("Main", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Main", WINDOW_SIZE, WINDOW_SIZE)
            cv2.imshow("Main", image)
            # cv2.namedWindow("Foreground", cv2.WINDOW_NORMAL)
            # cv2.resizeWindow("Foreground", WINDOW_SIZE, WINDOW_SIZE)
            # cv2.imshow("Foreground", foreground)

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
        if width >= MIN_RECTANGLE_SIZE and height >= MIN_RECTANGLE_SIZE:
            centroids.append(Centroid(x + int(width / 2), y + int(height / 2)))
    return centroids


def addCentroidsToVehicles():
    # add current centroids to current, not finished vehicles:
    for current in currentCentroids:
        for vehicle in vehicles:
            if current.isNearBy(vehicle.getCentroid(-1)):
                vehicle.addCentroid(current)
                currentCentroids.remove(current)
                break
    # add new vehicle:
    for current in currentCentroids:
        for last in lastCentroids:
            if current.isNearBy(last):
                vehicles.append(Vehicle(last, current))


def detectVehicles():
    global count, found
    for vehicle in [vehicle for vehicle in vehicles if not vehicle.isFound()]:
        startX = vehicle.getCentroid(0).getX()
        endX = vehicle.getCentroid(-1).getX()
        if startX > endX:
            order = -1
        else:
            order = 1
        for x in range(startX, endX, order):
            if x == VehicleInfo.MIDDLE_X:
                count += 1
                print("Vehicle found:", count)
                cv2.circle(image, vehicle.getCentroid(-1).getXY(), 10, VehicleInfo.GREEN, -1)
                found = True
                vehicle.setFound(True)
                break


if __name__ == "__main__":
    main()
