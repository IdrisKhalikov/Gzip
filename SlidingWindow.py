class SlidingWindow:
    def __init__(self, size):
        self._length = size
        self._buffer = [None] * size
        self._pointer = self._length
    
    def add(self, value):
        self._pointer = (self._pointer + 1) % self._length
        self._buffer[self._pointer] = value
    
    def get_last(self, offset=0):
        assert(offset >= 0)
        return self._buffer[(self._pointer - offset) % self._length]