import cv2

from VehicleInfo import X_DEVIATION as X, Y_DEVIATION as Y, WHITE


class Centroid:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def isNearBy(self, vCentroid, direction=None):
        if direction == "west":
            if self.x <= vCentroid.getX() and vCentroid.getY() - Y < self.y < vCentroid.getY() + Y:
                return True
            else:
                return False
        elif direction == "east":
            if self.x >= vCentroid.getX() and vCentroid.getY() - Y < self.y < vCentroid.getY() + Y:
                return True
            else:
                return False
        else:
            if vCentroid.getX() - X < self.x < vCentroid.getX() + X and vCentroid.getY() - Y < self.y < vCentroid.getY() + Y:
                return True
            else:
                return False

    def draw(self, image):
        cv2.circle(image, (self.x, self.y), 5, WHITE, -1)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getXY(self):
        return self.x, self.y
