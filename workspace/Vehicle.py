import cv2


class Vehicle:
    def __init__(self, centroid):
        self.found = False
        self.centroids = []
        self.centroids.append(centroid)

    def setFound(self, value):
        self.found = value

    def getFound(self):
        return self.found

    def add_centroid(self, centroid):
        self.centroids.append(centroid)

    def get_centroid(self, index):
        return self.centroids[index]

    def get_all_centroids(self):
        return self.centroids

    def draw_vehicle_line(self, image, color):
        for i in range(len(self.centroids) - 1):
            cv2.line(image, self.centroids[i], self.centroids[i + 1], color)
