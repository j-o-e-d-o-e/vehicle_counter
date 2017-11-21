import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread("../../img/image.jpg", cv2.IMREAD_GRAYSCALE)

plt.imshow(img, cmap="gray",interpolation="bicubic")
plt.plot([100,120],[120,120],"b", linewidth=12)
plt.show()
