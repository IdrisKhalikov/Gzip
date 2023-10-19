class ProgressBar:

    def __init__(self, length, max_value):
        self._value = 0
        self._length = length
        self._max_value = max_value if max_value != 0 else 100
    
    def set_value(self, value):
        assert(0 <= value <= self._max_value)
        self._value = value
    
    def update(self):
        per_percent = self._length / self._max_value
        progress = round((self._value / self._max_value)*100, 2)
        progress_bar = (int(per_percent*self._value)*'▇').ljust(self._length, '-')
        print(f'Progress:[{progress_bar}] {progress}%', end='\r')
    
