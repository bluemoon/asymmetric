# Go-style channels
class Channel(object):
    def __init__(self, bufsize=0):
        self.bufsize = bufsize
        self._msgs = deque()
        self._wait_df = None
        self._fire_df = None

    @_o
    def fire(self, value):
        if not self._wait_df:
            if len(self._msgs) >= self.bufsize:
                if not self._fire_df:
                    self._fire_df = Deferred()
                yield self._fire_df

        if not self._wait_df:
            assert (len(self._msgs) < self.bufsize)
            self._msgs.append(value)
            return

        assert(len(self._msgs) == 0)
        df = self._wait_df
        self._wait_df = None
        queue_task(0, df.callback, value)

    @_o
    def wait(self):
        popped = False
        if self._msgs:
            value = self._msgs.popleft()
            popped = True

        if not self._wait_df:
            self._wait_df = Deferred()
        wait_df = self._wait_df

        if self._fire_df:
            df = self._fire_df
            self._fire_df = None
            queue_task(0, df.callback, None)

        if not popped:
            value = yield wait_df
        yield value
