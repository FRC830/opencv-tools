import cv2
import numpy as np
import params

def on_frame(image, camera):
    orig_image = image
    hsvimage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    lower = np.array([int(params.params.get('hue_min', 0)),
                      int(params.params.get('sat_min', 0)),
                      int(params.params.get('val_min', 0))])
    upper = np.array([int(params.params.get('hue_max', 179)),
                      int(params.params.get('sat_max', 255)),
                      int(params.params.get('val_max', 255))])

    mask = cv2.inRange(hsvimage, lower, upper)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    
    new_image = cv2.bitwise_and(orig_image, orig_image, mask=mask)

    #draw rectangle around largest contour
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(new_image,(x,y),(x+w,y+h),(0,255,0),2)

    return new_image
