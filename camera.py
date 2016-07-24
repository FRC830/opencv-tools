from __future__ import division, print_function, unicode_literals
import cv2
import os
import threading
import time

import script

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue

class Camera(object):
    def __init__(self, id, fps=20, width=640, height=480):
        self._id = id
        self.cap_thread = CaptureThread(self)

        self.fps = fps
        self.width = width
        self.height = height

        self.cap_thread.start()

    @property
    def id(self):
        return self._id

    class capture_property(property):
        """ A wrapper for OpenCV capture properties

        Any changes to these attributes are queued to be processed by the
        capture thread on its next tick.
        """

        def __init__(self, name, cv_property_id):
            self.name = name
            self.cv_property_id = cv_property_id

        def __get__(self, camera, owner):
            return getattr(camera, '_' + self.name)

        def __set__(self, camera, value):
            setattr(camera, '_' + self.name, value)
            camera.cap_thread.opt_queue.put((self.cv_property_id, value))

    fps = capture_property('fps', cv2.cv.CV_CAP_PROP_FPS)
    width = capture_property('width', cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    height = capture_property('height', cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    def __getattr__(self, attr):
        """ Fall back to CaptureThread attributes """
        return getattr(self.cap_thread, attr)

class CaptureThread(threading.Thread):
    _read_lock = threading.Lock()

    if 'STATIC_IMAGE' in os.environ:
        static_image = cv2.imread(os.environ['STATIC_IMAGE'])

    def __init__(self, camera):
        super(CaptureThread, self).__init__()
        self.parent_thread = threading.current_thread()
        self.camera = camera
        self._running = False
        self.cap = cv2.VideoCapture(camera.id)
        self.opt_queue = queue.Queue()

        self.image_lock = threading.Lock()
        self._image = None
        self.image_ok = False

    def run(self):
        self._running = True
        while self._running:
            while True:
                try:
                    self.cap.set(*self.opt_queue.get(block=False))
                except queue.Empty:
                    break

            with self._read_lock:
                if getattr(self, 'static_image', None) is not None:
                    image = cv2.resize(self.static_image, (self.camera.width, self.camera.height))
                    self.image_ok = True
                else:
                    self.image_ok, image = self.cap.read()
            if self.image_ok:
                try:
                    if script.current_script:
                        image_out = script.current_script.trigger('frame', image)
                        if isinstance(image_out, type(image)):
                            image = image_out
                except script.ScriptError as e:
                    import traceback
                    print(e)
                    print(e.traceback)
                self.image = image

            time.sleep(1 / self.camera.fps)

            # Stop if the parent thread died
            if not self.parent_thread.is_alive():
                self.stop()

    def stop(self):
        self._running = False
        self.image_ok = False

    @property
    def image(self):
        with self.image_lock:
            return self._image

    @image.setter
    def image(self, image):
        with self.image_lock:
            self._image = image

class _FakeCamera:
    image = None
    image_ok = False
    fps = 0
    width = 640
    height = 480

fake_camera = _FakeCamera()
