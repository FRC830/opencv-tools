import cv2
import numpy as np

def find_largest_contour(source):
    contours, hierarchy = cv2.findContours(source, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        ordered = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
        return ordered[0]

def on_frame(image, camera):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([60, 100, 200], dtype=np.uint8)
    upper_bound = np.array([90, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    cont = find_largest_contour(mask)
    if cont is not None:
        cv2.drawContours(image, [cont], 0, (255,0,255), -1)
        moments = cv2.moments(cont)
        if moments["m00"]:
            cx = int((moments["m10"] / moments["m00"]))
            cy = int((moments["m01"] / moments["m00"]))
            # cv2.circle(image, (cx, cy), 7, (255, 127, 255), -1)
            height, width, channels = image.shape
            cv2.line(image, (cx, 0), (cx, height), (0, 0, 255), 4)
