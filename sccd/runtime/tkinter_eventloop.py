"""
Yentl added many patches to make this code TkInter compatible.
TkInter is NOT thread-safe, and this applies to the after operations as well.
Therefore, calling tk.after (or after_cancel) should NOT be done from any thread apart from the thread running TkInter itself.
See https://mail.python.org/pipermail/tkinter-discuss/2013-November/003522.html for a discussion...
What actually happens in this code, is that we check whether we are on the main thread or not.
If we are on the main thread, we invoke the code as usual.
If we are not on the main thread, we force the *run* operation to execute, even though it might not have been scheduled.
This operation, however, will run on the main thread, and from there we can then call this schedule function again.
"""

# If we are not on the main thread, we force the *run* operation

from sccd.runtime.statecharts_core import EventLoop

import math
import threading as thread

class TkEventLoop(EventLoop):
    def __init__(self, tk):
        self.ctr = 0
        self.tk = tk
        self.main_thread = thread.get_ident()

        # bind scheduler callback
        def schedule(callback, timeout, behind = False):
            if self.main_thread != thread.get_ident():
                # Use events, as Tk operations are far from thread safe...
                # Should there be a timeout, event_generate will automatically schedule this for real from inside the main loop
                tk.event_generate("<<TriggerSCCDEvent>>", when="tail")
            else:
                # As usual, use Tk after events
                if behind:
                    tk.update_idletasks()
                return tk.after(timeout, callback)

        def cancel(evt):
            if self.main_thread != thread.get_ident():
                # This will also remove the pending events, while also triggering a run first
                # That initial run, however, will not execute anything
                tk.event_generate("<<TriggerSCCDEvent>>", when="tail")
            else:
                tk.after_cancel(evt)

        EventLoop.__init__(self, schedule, cancel)

    def bind_controller(self, controller):
        self.tk.bind("<<TriggerSCCDEvent>>", controller.run)
