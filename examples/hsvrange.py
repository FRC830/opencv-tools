import cv2
import numpy as np
import params

def on_frame(image):
    orig_image = image
    hsvimage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    lower = np.array([int(params.params.get('hue_min', 0)),
                      int(params.params.get('sat_min', 0)),
                      int(params.params.get('val_min', 0))])
    upper = np.array([int(params.params.get('hue_max', 179)),
                      int(params.params.get('sat_max', 255)),
                      int(params.params.get('val_max', 255))])

    mask = cv2.inRange(hsvimage, lower, upper)
    
    new_image = cv2.bitwise_and(orig_image, orig_image, mask=mask)

    return new_image
