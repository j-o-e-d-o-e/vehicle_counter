import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread("img/image.jpg", cv2.IMREAD_GRAYSCALE)
#img = cv2.imread("nice.jpg", cv2.BG)

##cv2.imshow("Nice",img)
##cv2.waitKey(0)
##cv2.destroyAllWindows()

plt.imshow(img, cmap="gray",interpolation="bicubic")
plt.plot([300,220],[320,320],"b", linewidth=12)
plt.show()
