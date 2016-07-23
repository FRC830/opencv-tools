# Handles loading and running scripts
from __future__ import division, print_function, unicode_literals
import os
import threading
import sys
import time
import traceback

_module_path = os.path.abspath(os.path.dirname(__file__))

current_script = None

class ScriptError(Exception):
    def __init__(self, exc):
        self.exc = exc
        self.traceback = traceback.format_exc()
    def __str__(self):
        return 'Script error: ' + str(self.exc)

class ScriptLoadError(ScriptError):
    pass

def _load_file(path):
    if not os.path.isfile(path):
        raise IOError("File not found: %s" % path)
    # Add this folder to the script's module search path
    old_path = sys.path[:]
    sys.path.append(_module_path)
    try:
        with open(path) as f:
            contents = f.read()
        try:
            code = compile(contents, path, 'exec')
        except Exception as e:
            raise ScriptLoadError(e)
        env = {}
        exec(code, env, env)
        return env
    finally:
        sys.path = old_path

class Script(object):
    _loaded = False
    last_load_time = 0

    def __init__(self, path):
        self._path = path
        self.load()

    @property
    def path(self):
        return self._path

    @property
    def loaded(self):
        return self._loaded

    def load(self):
        if not self._loaded:
            try:
                self._env = _load_file(self.path)
            except ScriptLoadError as e:
                print('script load failed: %s' % e)
                self._env = {}
            self._loaded = True
            self.last_load_time = time.time()

    def unload(self):
        if self._loaded:
            self.trigger('unload')
            self._env = None
            self._loaded = False

    def reload(self):
        self.unload()
        self.load()

    def can_trigger(self, event):
        """ Check whether the script has an event handler """
        return hasattr(self._env.get('on_' + event, None), '__call__')

    def trigger(self, event, *args, **kwargs):
        """ Trigger an event handler """
        key = 'on_' + event
        if key in self._env:
            try:
                return self._env[key](*args, **kwargs)
            except (Exception, SystemExit) as e:
                raise ScriptError(e)

    __del__ = unload

class ScriptWatchThread(threading.Thread):
    daemon = True
    def run(self):
        while True:
            time.sleep(1)
            if current_script and current_script.last_load_time < os.path.getmtime(current_script.path):
                print('Reloading script: %s' % current_script.path)
                current_script.reload()

def load(path):
    global current_script
    if current_script is not None and current_script.path == path:
        current_script.reload()
    else:
        ScriptWatchThread().start()
        current_script = Script(path)
