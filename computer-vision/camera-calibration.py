import numpy as np
import cv2 as cv 
import glob
import os

checkerboardSize = (9, 6)
frameSize = (6000, 4000)
sensorSize = (23.5, 15.6) # in mm

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((checkerboardSize[0] * checkerboardSize[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:checkerboardSize[0], 0:checkerboardSize[1]].T.reshape(-1, 2)

objPoints = []
imgPoints = []

images = glob.glob('/mnt/c/Users/begtgonzalez/OneDrive - Delft University of Technology/Documents/University/Bicycle-Crashes/Data/03-bicycle-data/260519-mocap/*.JPG')

for image in images:
    print(image)
    img = cv.imread(image)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, corners = cv.findChessboardCorners(gray, checkerboardSize, None)

    if ret == True:
        
        objPoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgPoints.append(corners)

        cv.drawChessboardCorners(img, checkerboardSize, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(1000)

    cv.destroyAllWindows()

### Calibration

ret, cameraMatrix, dist, rvecs, tvecs =  cv.calibrateCamera(objPoints, imgPoints, frameSize, None, None)

print('Camera calibrated: ', ret)
print('\nCamera Matrix: \n', cameraMatrix)
print('\nDistortion Parameters: \n', dist)
print('\nRotation Vectors: \n', rvecs)
print('\nTranslation Vectors: \n', tvecs)

sx = sensorSize[0]/frameSize[0]
f_length_mm = cameraMatrix[0,0]*sx

print('Focal length: ', f_length_mm)