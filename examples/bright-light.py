import cv2

import params

def on_frame(image, camera):
    orig_image = image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (0, 0), sigmaX=5, sigmaY=5)
    _, image = cv2.threshold(image, 200, 100, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    centers = []
    for cont in contours:
        approx = cv2.approxPolyDP(cont, 0.01 * cv2.arcLength(cont, True), True)
        sides = len(approx)
        if sides > 4:
            cv2.drawContours(orig_image, [cont], 0, (255, int(params.params.get('green', 100)), 255), -1)
            moments = cv2.moments(cont)
            if moments["m00"]:
                centers.append((
                    int((moments["m10"] / moments["m00"])),
                    int((moments["m01"] / moments["m00"]))
                ))

    for c in centers:
        cv2.circle(orig_image, c, 7, (127, 127, 255), -1)
    return orig_image
