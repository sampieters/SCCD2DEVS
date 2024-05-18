"""
*REALLY* Small framework for creating/manipulating/deleting gui elements in Tkinter, version 2.

The problem with version 1 (ui.py) was that the API returned and expected references to Tk objects. These references were used as event parameters and object attributes in SCCD models. This broke translation of SCCD to (PyP)DEVS: in PyPDEVS, events and state objects need to be deep-copied and serialized (for rollback), which cannot be done with Tk objects. Further, PyPDEVS is inherently multi-threaded (and possibly distributed, with migration), but all calls to Tk's API must be done from a single thread (the same thread that runs Tk's event loop).

The solution is to run Tk in its own thread, where all Tk objects reside. All communication between this thread and the SCCD model happens via asynchronous events. Tk objects never 'escape' the tk-thread. To allow the outside world to point to Tk objects, every Tk object is assigned a unique (integer) identifier.
"""

import sys
from functools import partial

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

from sccd.runtime.libs.drawing import drawing
from sccd.runtime.libs.utils import utils
from sccd.runtime.statecharts_core import Event

EVENTS = utils._bunch(
    KEY_PRESS =            '<Key>',
    MOUSE_CLICK =          '<Button>',
    MOUSE_MOVE =           '<Motion>',
    MOUSE_PRESS =          '<ButtonPress>',
    MOUSE_RELEASE =        '<ButtonRelease>',
    MOUSE_RIGHT_CLICK =    '<Button-2>' if sys.platform == "darwin" else '<Button-3>',
    WINDOW_CLOSE =         'WM_DELETE_WINDOW');

if sys.platform == "darwin":
    MOUSE_BUTTONS = utils._bunch(
        LEFT        = 1,
        MIDDLE    = 3,
        RIGHT        = 2);
else:
    MOUSE_BUTTONS = utils._bunch(
        LEFT        = 1,
        MIDDLE    = 2,
        RIGHT        = 3);

KEYCODES    = utils._bunch(
    DELETE    = 46);

class UI:
    # Parameters:
    #   controller - needed to send result events back
    def __init__(self, tk, controller):
        self.tk = tk
        self.controller = controller
        self.mapping = {} # mapping of ID to tk widget
        self.next_id = 0

    # Helper
    def _gen_id(self, tkwidget):
        id = self.next_id
        self.next_id += 1
        self.mapping[id] = tkwidget
        return id

    def create_button(self, window_id, text, res_port):
        button_id = self._gen_id(None)
        self.controller.addInput(Event("button_created", res_port, [button_id]))

    def create_canvas(self, window_id, width, height, style, res_port):
        canvas_id = self._gen_id(None)
        self.controller.addInput(Event("canvas_created", res_port, [canvas_id]))

    def create_window(self, width, height, title, res_port):
        window_id = self._gen_id(None)
        self.controller.addInput(Event("window_created", res_port, [window_id]))


    def destroy_window(self, window_id, res_port=None):
        if res_port != None:
            self.controller.addInput(Event("window_destroyed", res_port, [window_id]))

    def destroy_all(self):
        pass

    def create_text(self, canvas_id, x, y, the_text, res_port):
        canvas = self.mapping[canvas_id]
        text_id = 0
        self.controller.addInput(Event("text_created", res_port, [canvas_id, text_id]))

    def update_text(self, canvas_id, text_id, the_text, res_port):
        pass

    def create_circle(self, canvas_id, x, y, r, style, res_port):
        circle_id = 0
        self.controller.addInput(Event("circle_created", res_port, [canvas_id, circle_id]))


    def create_rectangle(self, canvas_id, x, y, w, h, style, res_port):
        rect_id = 0
        self.controller.addInput(Event("rectangle_created", res_port, [canvas_id, rect_id]))

    def set_element_pos(self, canvas_id, element_id, new_x, new_y):
        pass

    def set_element_color(self, canvas_id, element_id, color):
        pass

    def move_element(self, canvas_id, element_id, dx, dy):
        pass

    def destroy_element(self, canvas_id, element_id, res_port=None):
        if res_port != None:
            self.controller.addInput(Event("element_destroyed", res_port, [canvas_id, element_id]))

    def _handle_event(self, event, raise_name, port, ev=None):
        if event == EVENTS.KEY_PRESS :
            self.controller.addInput(Event(raise_name, port, [ev.keycode]))
        elif event == EVENTS.MOUSE_CLICK or \
             event == EVENTS.MOUSE_MOVE or \
             event == EVENTS.MOUSE_PRESS or \
             event == EVENTS.MOUSE_RELEASE or \
             event == EVENTS.MOUSE_RIGHT_CLICK :
            self.controller.addInput(Event(raise_name, port, [ev.x, ev.y, ev.num]))
        elif event == EVENTS.WINDOW_CLOSE :
            self.controller.addInput(Event(raise_name, port, []))
        else:
            raise Exception('Unsupported event: ' + str(event))

    def bind_event(self, widget_id, tk_event, sccd_event_name, port):
        pass

    def bind_canvas_event(self, canvas_id, element_id, tk_event, sccd_event_name, port):
        pass