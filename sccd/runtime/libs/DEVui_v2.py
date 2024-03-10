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
        def callback():
            window = self.mapping[window_id]
            button = tk.Button(window, text=text)
            button.pack(fill=tk.BOTH, expand=1)
            button_id = self._gen_id(button)
            self.controller.addInput(Event("button_created", res_port, [button_id]))
        # schedule in mainloop:
        self.tk.after(0, callback)

    def create_canvas(self, window_id, width, height, style, res_port):
        def callback():
            window = self.mapping[window_id]
            canvas = tk.Canvas(window, width=width, height=height)
            canvas.config(**style)
            canvas.pack(fill=tk.BOTH, expand=1)
            canvas_id = self._gen_id(canvas)
            
            #self.controller.addInput(Event("canvas_created", res_port, [canvas_id]))
            self.controller.realtime_interrupt(f"{res_port} Event(\"canvas_created\",self.{res_port},[{canvas_id}])")
        # schedule in mainloop:
        self.tk.after(0, callback)

    def create_window(self, width, height, title, res_port):
        def callback():
            window = tk.Toplevel(self.tk)
            window.title(title)
            window.geometry(str(width)+"x"+str(height)+"+300+300")
            window_id = self._gen_id(window)
            #self.controller.addInput(Event("window_created", res_port, [window_id]))

            #source = f"{res_port} Event(\"window_created\", {res_port},[{window_id}])"
            self.controller.realtime_interrupt(f"{res_port} Event(\"window_created\",self.{res_port},[{window_id}])")
        # schedule in mainloop:
        self.tk.after(0, callback)

    def destroy_window(self, window_id, res_port=None):
        def callback():
            window = self.mapping[window_id]
            window.destroy()
            if res_port != None:
                self.controller.addInput(Event("window_destroyed", res_port, [window_id]))
        # schedule in mainloop:
        self.tk.after(0, callback)

    def destroy_all(self):
        def callback():
            self.tk.destroy()
        self.tk.after(0, callback)

    def create_circle(self, canvas_id, x, y, r, style, res_port):
        def callback():
            canvas = self.mapping[canvas_id]
            circle_id = canvas.create_oval(x-r, y-r, x+r, y+r, **style)
            self.controller.addInput(Event("circle_created", res_port, [canvas_id, circle_id]))
        # schedule in mainloop:
        self.tk.after(0, callback)

    def create_rectangle(self, canvas_id, x, y, w, h, style, res_port):
        def callback():
            canvas = self.mapping[canvas_id]
            rect_id = canvas.create_rectangle(x-w/2.0, y-h/2.0, x+w/2.0, y+h/2.0, **style)
            self.controller.addInput(Event("rectangle_created", res_port, [canvas_id, rect_id]))
        # schedule in mainloop
        self.tk.after(0, callback)

    def set_element_pos(self, canvas_id, element_id, new_x, new_y):
        def callback():
            canvas = self.mapping[canvas_id]
            x, y, *_ = canvas.bbox(element_id)
            canvas.move(element_id, new_x-x, new_y-y)
        # schedule in mainloop
        self.tk.after(0, callback)

    def set_element_color(self, canvas_id, element_id, color):
        def callback():
            canvas = self.mapping[canvas_id]
            canvas.itemconfig(element_id, fill=color)
        # schedule in mainloop
        self.tk.after(0, callback)

    def move_element(self, canvas_id, element_id, dx, dy):
        def callback():
            canvas = self.mapping[canvas_id]
            canvas.move(element_id, dx, dy)
        # schedule in mainloop
        self.tk.after(0, callback)

    def destroy_element(self, canvas_id, element_id, res_port=None):
        def callback():
            canvas = self.mapping[canvas_id]
            canvas.delete(element.element_id)
            if res_port != None:
                self.controller.addInput(Event("element_destroyed", res_port, [canvas_id, element_id]))
        # schedule in mainloop
        self.tk.after(0, callback)

    def _handle_event(self, event, raise_name, port, ev=None):
        if event == EVENTS.KEY_PRESS :
            self.controller.addInput(Event(raise_name, port, [ev.keycode]))
        elif event == EVENTS.MOUSE_CLICK or \
             event == EVENTS.MOUSE_MOVE or \
             event == EVENTS.MOUSE_PRESS or \
             event == EVENTS.MOUSE_RELEASE or \
             event == EVENTS.MOUSE_RIGHT_CLICK :
            #self.controller.addInput(Event(raise_name, port, [ev.x, ev.y, ev.num]))
            self.controller.realtime_interrupt(f"{port} Event(\"{raise_name}\",self.{port},[{ev.x},{ev.y},\"{ev.num}\"])")
        elif event == EVENTS.WINDOW_CLOSE :
            #self.controller.addInput(Event(raise_name, port, []))
            self.controller.realtime_interrupt(f"{port} Event(\"{raise_name}\",self.{port},[])")
            
        else:
            raise Exception('Unsupported event: ' + str(event))

    def bind_event(self, widget_id, tk_event, sccd_event_name, port):
        def callback():
            widget = self.mapping[widget_id]
            if tk_event == EVENTS.WINDOW_CLOSE :
                widget.protocol(tk_event, partial(self._handle_event, tk_event, sccd_event_name, port))
            else:
                widget.bind(tk_event, partial(self._handle_event, tk_event, sccd_event_name, port))
        # schedule in mainloop:
        self.tk.after(0, callback)

    def bind_canvas_event(self, canvas_id, element_id, tk_event, sccd_event_name, port):
        def callback():
            canvas = self.mapping[canvas_id]
            canvas.tag_bind(element_id, tk_event, partial(self._handle_event, tk_event, sccd_event_name, port))
        # schedule in mainloop
        self.tk.after(0, callback)