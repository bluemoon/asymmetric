from collections import deque
from threading import Thread
from itertools import chain

class manager:
    def __init__(self):
        self._queue = deque()

    def push(self, event, channel=None, target=None):
        pass
    
    def __handle_events(self, event, channel):
        for handler in self._getHandlers(channel):
            pass
    
    def _getHandlers(self, _channel):
        pass
