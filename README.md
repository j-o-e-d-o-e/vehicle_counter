# vehicle_counter

Detects and counts vehicles moving from left to right or vice versa. It can be used with webcam, pi camera or video file.

## Procedure

### Process the frame
- Convert original frame to grayscale and remove noise
- Create an average frame, which is basically the static background. Each new frame influences this average frame to a certain extent
- Compute the difference between the average and current frame to get the foreground
- Apply a threshold to this difference frame to get clean shapes of the moving objects in the foreground

### Get contours
- Get the contours and filter out small contours
- Reduce the amount of points each contour consists of and sort the contours by size
- Find contours which are close to each other using the auxiliary function aux_close() and merge these. For instance, if a is close to b and b is close to c, then a is also close to c via a. Consequently, the new merged contour consists of all three contours a, b and c.

### Get centroids and add these to vehicles or create new vehicles
- Vehicles are stored as dictionaries with the attributes: id, fist time seen, last time seen, direction, a boolean 'found' and a list of 'tracked' centroids
- If the distance isn't two great and the direction is right, the centroid will be added to this vehicle
- If there are still centroids left which could not be added to an existing vehicle, create a new vehicle
- If a centroid from the current frame is close to one of the last frame, a new vehicle will be created

###  Detect whether vehicles crossed center line
- Vehicles which haven't been seen for some time will be removed
- If a vehicle has not been found yet and has crossed the center line, the vehicle counter increments.


Helpful repo by @iandees: https://github.com/iandees/speedtrack