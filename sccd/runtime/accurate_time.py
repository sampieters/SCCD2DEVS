import time as t
import os

class AccurateTime:
    def __init__(self):
        if os.name == 'posix':
            self._get_wct_time = lambda self: int((t.time() - self.start_time) * 1000)
        elif os.name == 'nt':
            self._get_wct_time = lambda self: int((t.clock() - self.start_time) * 1000)
        
    def set_start_time(self):
        if os.name == 'posix':
            self.start_time = t.time()
        elif os.name == 'nt':
            self.start_time = t.clock()
            
    def get_wct(self):
        return self._get_wct_time(self)