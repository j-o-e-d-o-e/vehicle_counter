# vehicle_counter

Detects and counts vehicles moving from left to right or vice versa. Also for raspberry pi.

## Procedure

### Process frame
- Convert original frame to grayscale and remove noise
- Create an average frame, which is basically the static background. Each new frame influences this average frame to some extent
- Compute the difference between average and current frame to get the foreground
- Apply a threshold to this difference frame to get clean shapes of the moving objects in the foreground

![difference](https://user-images.githubusercontent.com/26798159/35406645-ca19d1d2-0209-11e8-8abc-5a8912a21111.JPG)
![threshold](https://user-images.githubusercontent.com/26798159/35406644-c9f18b5a-0209-11e8-9d69-f1b993f88fc2.JPG)

### Get contours
- Get the contours and filter out small ones
- Reduce the amount of points each contour consists of and sort the contours by size
- Find contours which are close to each other using the auxiliary function aux_close() and merge these. For instance, if a is close to b and b is close to c, then a is also close to c via b. Consequently, the new merged contour consists of all three contours a, b and c.

![contours](https://user-images.githubusercontent.com/26798159/35406647-ca738ff6-0209-11e8-9d4c-c458819e0c37.JPG)

### Get centroids and add these to vehicles or create new vehicles
- Vehicles are stored as dictionaries with the attributes: id, fist time seen, last time seen, direction, a boolean 'found' and a list of 'tracked' centroids (blue dots)
- If the distance isn't two great and the direction is right, the centroid will be added to this vehicle. An added centroid will be removed from the list of candidates
- If there are still centroids left in the candidates list, check if a new vehicle can be created
- If a centroid from the current frame is close to one of the last frame, a new vehicle will be created

###  Detect whether vehicles crossed center line
- Vehicles which haven't been seen for some time will be removed
- If a vehicle has not been found yet and has crossed the center line, the vehicle counter increments.

![debug](https://user-images.githubusercontent.com/26798159/35406646-ca529ec2-0209-11e8-954c-534fe3939275.JPG)

### Materials
- <a href="https://github.com/iandees/speedtrack">Repo</a> by @iandees
- <a href="https://docs.opencv.org/3.3.1/d3/d05/tutorial_py_table_of_contents_contours.html">Tutorial</a> about contours
