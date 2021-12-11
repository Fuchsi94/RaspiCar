import cv2
import os
import numpy as np

print(os.getcwd())
image = cv2.imread('lane.jpg')
print(image.shape)
image = cv2.resize(image, (1200, 800))



isClosed = True
color = (255, 0, 0)
thickness = 2

polygon = np.array([[(0, 600),  (1200, 600),  (1200, 400), (800, 250), (400, 250), (0, 400)]])
image = cv2.polylines(image, [polygon], isClosed, color, thickness)

cv2.imshow('lane', image)

cv2.waitKey(0)
cv2.destroyAllWindows()