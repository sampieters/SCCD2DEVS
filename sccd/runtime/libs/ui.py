"""
 *REALLY* Small framework for creating/manipulating/deleting gui elements in Tkinter.

 NOTE: keep this synced with ui.js

 Author: Raphael Mannadiar
 Date: 2014/08/21
"""

import sys
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

from sccd.runtime.libs.drawing import drawing
from sccd.runtime.libs.utils import utils

from sccd.runtime.statecharts_core import Event


class ui:
    window = None
    __nextWindowId = 0

    EVENTS = utils._bunch(
        KEY_PRESS =             '<Key>',
        MOUSE_CLICK =             '<Button>',
        MOUSE_MOVE =             '<Motion>',
        MOUSE_PRESS =            '<ButtonPress>',
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

    @staticmethod
    def append_button(_window,text):
        button = tk.Button(_window, text=text)
        button.pack(fill=tk.BOTH, expand=1)
        return ui.wrap_element(button)


    @staticmethod
    def append_canvas(_window,width,height,style):
        canvas = tk.Canvas(_window,width=width,height=height)
        canvas.config(**style)
        canvas.pack(fill=tk.BOTH, expand=1)
        return drawing.canvas_wrapper(canvas)


    @staticmethod
    def bind_event(source,event,controller,raise_name,port="ui"):

        def __handle_event(ev=None):
            if event == ui.EVENTS.KEY_PRESS :
                controller.addInput(Event(raise_name, port, [ev.keycode,source]))

            elif event == ui.EVENTS.MOUSE_CLICK or \
                  event == ui.EVENTS.MOUSE_MOVE or \
                  event == ui.EVENTS.MOUSE_PRESS or \
                  event == ui.EVENTS.MOUSE_RELEASE or \
                    event == ui.EVENTS.MOUSE_RIGHT_CLICK :
                controller.addInput(Event(raise_name, port, [ev.x, ev.y, ev.num]))

            elif event == ui.EVENTS.WINDOW_CLOSE :
                controller.addInput(Event(raise_name, port, [source]))

            else :
                raise Exception('Unsupported event');

        if event == ui.EVENTS.WINDOW_CLOSE :
            source.protocol(event, __handle_event)

        elif issubclass(drawing.ui_element_wrapper,source.__class__) :
            source.canvas_wrapper.element.tag_bind(source.element_id, event, __handle_event)

        else :
            source.bind(event, __handle_event)


    @staticmethod
    def close_window(_window):
        _window.destroy()


    @staticmethod
    def log(value):
        print(value)


    @staticmethod
    def new_window(width,height,title=None):
        _window = tk.Toplevel(ui.window)
        if title:
            _window.title(title)
        _window.geometry(str(width)+"x"+str(height)+"+300+300")
        return _window


    @staticmethod
    def println(value,target):
        raise Exception('Not implemented yet');


    @staticmethod
    def wrap_element(element):
        return utils._bunch(element=element)

