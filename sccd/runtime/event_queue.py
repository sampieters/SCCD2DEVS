from sccd.runtime.infinity import INFINITY
from heapq import heappush, heappop

class EventQueue(object):
    def __init__(self):
        self.event_list = []
        self.event_time_numbers = {}
        self.removed = set()
    
    def __str__(self):
        return str([entry for entry in self.event_list if entry not in self.removed])
    
    def isEmpty(self):
        return not [item for item in self.event_list if not item in self.removed]
    
    def getEarliestTime(self):
        while self.event_list and (self.event_list[0] in self.removed):
            item = heappop(self.event_list)
            self.removed.remove(item)
        try:
            return self.event_list[0][0]
        except IndexError:
            return INFINITY
    
    def add(self, event_time, event):
        self.event_time_numbers[event_time] = self.event_time_numbers.setdefault(event_time, 0) + 1
        def_event = (event_time, self.event_time_numbers[event_time], event)
        heappush(self.event_list, def_event)
        return def_event
    
    def remove(self, event):
        self.removed.add(event)
        if len(self.removed) > 100:
            self.event_list = [x for x in self.event_list if x not in self.removed]
            self.removed = set()
    
    def pop(self):
        while 1:
            item = heappop(self.event_list)
            event_time = item[0]
            self.event_time_numbers[event_time] -= 1
            if not self.event_time_numbers[event_time]:
                del self.event_time_numbers[event_time]
            if item not in self.removed:
                return item[2]