import cv2

def on_frame(image):
    orig_image = image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (13, 13), 0)
    _, image = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(orig_image, contours, -1, (255,0,0), 5)
    return orig_image
