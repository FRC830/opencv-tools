from __future__ import division, print_function, unicode_literals
import argparse
import collections
import cv2
import flask
import flask.ext.socketio as socketio
import gevent
import numpy
import random
import threading
import time

from camera import Camera, fake_camera
import params
import script

STREAM_FPS = 20

cameras = {i: fake_camera for i in range(3)}

app = flask.Flask(__name__)
app.running = False
app.config.from_object('config')
app_socketio = socketio.SocketIO(app)

@app.route('/')
def index():
    return flask.render_template('index.html', cameras=cameras, next_view='stream')

@app.route('/favicon.ico')
def favicon_redirect():
    return flask.redirect(flask.url_for('static', filename='favicon.ico'))


@app.route('/stream')
def index_redirect():
    return flask.redirect(flask.url_for('index'))

@app.route('/stream/<int:id>')
def stream(id):
    return flask.render_template('stream.html', id=id, random=hash(random.random()),
        title='Camera %i' % id,
        scripts=['params.js'])

@app.route('/stream/raw/<int:id>')
@app.route('/stream/raw/<int:id>/<random>')
def raw_stream(id, random='unused'):
    # Based on http://blog.miguelgrinberg.com/post/video-streaming-with-flask
    # The `random` parameter allows some browsers to make multiple requests to this route at once
    return flask.Response(raw_stream_gen(id), mimetype='multipart/x-mixed-replace; boundary=--frame')

# imencode() apparently isn't reentrant
encode_lock = threading.Lock()
def raw_stream_gen(id):
    while app.running:
        time.sleep(1 / STREAM_FPS)
        camera = cameras.get(id, fake_camera)
        if camera.image is not None:
            img = camera.image
        else:
            img = numpy.zeros((camera.height, camera.width, 3), numpy.uint8)
        img = cv2.resize(img, (int(camera.width * 0.6), int(camera.height * 0.6)))
        cv2.putText(img, time.strftime('%H:%M:%S'), (5, 20), cv2.cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))
        if not camera.image_ok:
            msg = 'Camera not initialized' if camera is fake_camera else 'Camera not returning images'
            cv2.putText(img, msg, (5, 40), cv2.cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))
        with encode_lock:
            pass
        _, buf = cv2.imencode('.jpeg', img)
        yield (b'--frame\r\n' +
            b'Content-Type: image/jpeg\r\n' +
            b'Content-Length: ' + str(len(buf)).encode('utf-8') + b'\r\n' +
            b'\r\n' +
            bytes(bytearray(buf)) +
            b'\r\n'
        )


@app.route('/settings')
def settings_list():
    return flask.render_template('index.html', cameras=cameras, next_view='settings', title='Camera Settings')

@app.route('/settings/<int:id>')
def settings(id):
    return flask.render_template('settings.html', id=id, title='Camera %i' % id)


@app.route('/params/edit', methods=['POST'])
def params_edit():
    params.params.update(flask.request.form.to_dict())
    return ('', 204)


class ServerThread(threading.Thread):
    daemon = True
    def run(self):
        app.running = True
        app_socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, binary=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--script', help='Path to script')
    args = parser.parse_args()
    if args.script:
        script.load(args.script)

    ServerThread().start()

    for i in cameras:
        cameras[i] = Camera(i)

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        pass
    finally:
        app.running = False

if __name__ == '__main__':
    main()
