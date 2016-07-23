import cv2

colors = {
    3: (255, 0, 0),
    4: (255, 255, 0),
    5: (0, 255, 0),
    6: (0, 255, 255),
    7: (0, 0, 255),
    8: (255, 0, 255),
    'default': (255, 128, 0),
}

# RGB to BGR
for i in colors:
    colors[i] = colors[i][::-1]

def on_frame(image):
    orig_image = image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        approx = cv2.approxPolyDP(cont, 0.01 * cv2.arcLength(cont, True), True)
        sides = len(approx)
        cv2.drawContours(orig_image, [cont], 0, colors.get(sides, colors['default']), -1)
    return orig_image
