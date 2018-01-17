import cv2

from VehicleInfo import WHITE, STEP, MIDDLE_X, font


class Vehicle:
    num = 1

    def __init__(self, lastCentroid, currentCentroid):
        self.found = False
        self.finished = False
        self.direction = None
        self.centroids = []
        self.centroids.append(lastCentroid)
        self.centroids.append(currentCentroid)
        self.name = "Vehicle" + str(Vehicle.num)
        Vehicle.num += 1

    def drawVehicleLine(self, image):
        centroid_num = 1
        title = self.name + "(" + str(len(self.centroids)) + ")"
        cv2.putText(image, title, (self.centroids[0].getX() - 100, self.centroids[0].getY() - 20), font, 1, WHITE, 2,
                    cv2.LINE_AA)
        for index, centroid in enumerate(self.centroids[:-1]):
            cv2.line(image, centroid.getXY(), self.centroids[index + 1].getXY(), WHITE)
        for centroid in self.centroids:
            cv2.circle(image, centroid.getXY(), 5, WHITE, -1)
            cv2.putText(image, str(centroid_num), centroid.getXY(), font, 1, WHITE, 1, cv2.LINE_AA)
            centroid_num += 1

    def setDirection(self):
        eastCount, westCount = 0, 0
        if len(self.centroids) > 3:
            for index, centroid in enumerate(self.centroids[:-1]):
                nextCentroid = self.centroids[index + 1]
                if nextCentroid.getX() - STEP > centroid.getX():
                    eastCount += 1
                elif nextCentroid.getX() + STEP < centroid.getX():
                    westCount += 1
            if eastCount > westCount:
                self.direction = "east"
            elif eastCount < westCount:
                self.direction = "west"

    def getDirection(self):
        return self.direction

    def setFinished(self):
        if (self.direction == "west" and self.centroids[-1].getX() < MIDDLE_X - 300) or (
                        self.direction == "east" and self.centroids[-1].getX() > MIDDLE_X + 300):
            self.finished = True

    def isFinished(self):
        return self.finished

    def setFound(self, value):
        self.found = value

    def isFound(self):
        return self.found

    def addCentroid(self, centroid):
        self.centroids.append(centroid)

    def getCentroid(self, index):
        return self.centroids[index]

    def getAllCentroids(self):
        return self.centroids

    def print(self):
        print(self.name.upper() + ": ", end="")
        print("direction:", self.direction, end=", ")
        print("found:", self.found, end=", ")
        print("finished:", self.finished)
        for centroid in self.centroids:
            print(centroid.getXY(), end=" ")
        print("\n\n")

    def getName(self):
        return self.name
