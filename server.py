from __future__ import division, print_function, unicode_literals
import argparse
import cv2
import flask
import random
import threading
import time

from camera import Camera

STREAM_FPS = 20

cameras = [Camera(0), Camera(1)]
app = flask.Flask(__name__)
app.running = False

@app.route('/')
def index():
    out = ''
    for cam in cameras:
        out += '<a href="%s">Camera %i</a><br>' % (flask.url_for('stream', id=cam.id), cam.id)
    return out

@app.route('/stream/<int:id>')
def stream(id):
    return ('<a href="/">Home</a><br>') + \
        ('<img src="/stream/raw/%i?_=%f">' % (id, time.time()))

@app.route('/stream/raw/<int:id>')
def raw_stream(id):
    return flask.Response(raw_stream_gen(cameras[id]), mimetype='multipart/x-mixed-replace; boundary=--frame')

def raw_stream_gen(camera):
    started = False
    while app.running:
        time.sleep(1 / STREAM_FPS)
        if camera.image_ok:
            started = True
            img = camera.image
            img = cv2.resize(img, (int(camera.width * 0.6), int(camera.height * 0.6)))
            cv2.putText(img, time.strftime('%H:%M:%S'), (20, 20), cv2.cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
            _, buf = cv2.imencode('.jpeg', img)
            yield (b'--frame\r\n' +
                b'Content-Type: image/jpeg\r\n' +
                b'Content-Length: ' + str(len(buf)).encode('utf-8') + b'\r\n' +
                b'\r\n' +
                bytes(bytearray(buf)) +
                b'\r\n'
            )
        else:
            if started:
                break

if __name__ == '__main__':
    app.running = True
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)
    app.running = False
