import cv2
import numpy as np

from Centroid import Centroid
from Vehicle import Vehicle
import VehicleInfo

KERNEL = np.ones((4, 4), np.uint8)  # 3, 4 or 5
LEARNING_RATE = 0.1  # -1 or 0.1 to 0.5
MIN_RECTANGLE_SIZE = 140  # 100 to 200

class VehicleDetector:
    __instance = None
    backSubtractor = None
    vehicles = []
    lastCentroids = []
    currentCentroids = []
    count = 0
    found = False

    @staticmethod
    def getInstance(backSubtractor):
        if not VehicleDetector.__instance:
            VehicleDetector(backSubtractor)
        return VehicleDetector.__instance

    def __init__(self, backSubtractor):
        if VehicleDetector.__instance:
            pass
        else:
            VehicleDetector.__instance = self
            self.backSubtractor = backSubtractor

    def detectVehicles(self, image):
        foreground = self.getForeground(image)

        # get centroids of the moving objects from the last and current frame
        lastCentroids = self.currentCentroids
        currentCentroids = self.getCurrentCentroids(foreground)

        # set direction of vehicles in order to better add centroids
        for vehicle in [v for v in self.vehicles if not v.getDirection() and len(v.getCentroids()) > 3]:
            vehicle.setDirection()

        # add centroids to existing vehicles or create new vehicles
        self.addCentroidsToVehicles()

        # check if vehicles crossed the center line
        cv2.line(image, (VehicleInfo.MID_X, 300), (VehicleInfo.MID_X, 1000), VehicleInfo.RED)
        self.findVehicles(image)

        # print and draw centroids
        for centroid in currentCentroids:
            print("CENTROIDS:", end=" ")
            print(centroid.getXY())
            centroid.draw(image)

        # print and draw vehicles
        for vehicle in self.vehicles:
            vehicle.print()
            vehicle.drawVehicleLine(image)

        # delete if found vehicles are off screen
        for vehicle in [v for v in self.vehicles if v.isFound]:
            if vehicle.isOffScreen(lastCentroids, currentCentroids):
                print(vehicle.getName(), "is apparently off screen.")
                # vehicles.remove(vehicle)

    def getForeground(self, image):
        gray = np.float32(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        noisyForeground = self.backSubtractor.apply(gray, None, LEARNING_RATE)
        cleanForeground = cv2.morphologyEx(noisyForeground, cv2.MORPH_OPEN, KERNEL)
        return cleanForeground

    def getCurrentCentroids(self, foreground):
        centroids = []
        _, contours, _ = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for pointSet in contours:
            x, y, width, height = cv2.boundingRect(pointSet)
            if width >= MIN_RECTANGLE_SIZE and height >= MIN_RECTANGLE_SIZE:
                centroids.append(Centroid(x + int(width / 2), y + int(height / 2)))
        return centroids

    def addCentroidsToVehicles(self):
        if self.vehicles:
            # add centroids to existing vehicles:
            for current in self.currentCentroids:
                for vehicle in self.vehicles:
                    if current.isNearBy(vehicle.getCentroid(-1), vehicle.getDirection()):
                        vehicle.addCentroid(current)
                        break
            # add centroids (which were not already added to existing vehicles) to new vehicles:
            availableCentroids = []
            for current in self.currentCentroids:
                for vehicle in self.vehicles:
                    if current not in [v for v in vehicle.getCentroids()]:
                        availableCentroids.append(current)
            for available in availableCentroids:
                for last in self.lastCentroids:
                    if available.isNearBy(last, vehicle.getDirection()):
                        self.vehicles.append(Vehicle(last, current))
        else:
            # add centroids to new vehicles:
            for current in self.currentCentroids:
                for last in self.lastCentroids:
                    if current.isNearBy(last, None):
                        self.vehicles.append(Vehicle(last, current))

    def findVehicles(self, image):
        global count, found
        for vehicle in [v for v in self.vehicles if not v.isFound()]:
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
