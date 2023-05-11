class Lzss:

    LOOKAHEAD = 258 #max amount of characters to encode at once
    BACKREF_LEN = 32768 #amount of characters we can backref to
    MIN_LEN = 3 #minimal length of match to make backref

    '''Each symbol/backref is saved in a tuple that contains
    three values: a bool, that represents whether
    the current segment is a symbol or a backref, and two ints,
    which are: symbol code and 0, if the segment is a symbol, and
    length and distance, if the segment is a backref'''

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._output = []
        self._cur_byte = 0
        self._byte_len = 0
    
    def _write_symbol(self, data):
        self._output.append((0, data, 0))


    def compress(self, data):
        data_len = len(data)
        index = 0
        for index in range(self.MIN_LEN):
            self._write_symbol(data[index])
        while index < len(data):
            pass