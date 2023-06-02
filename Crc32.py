class Crc32:
    
    def __init__(self):
        self._crc = 0xFFFFFFFF
        self._polynom = 0xEDB88320
    
    def add_bytes(self, bytes):
        for byte in bytes:
            self.add(byte)
    
    def add(self, byte):
        self._crc ^= byte
        for i in range(7,-1,-1):
            mask = -(self._crc & 1)
            self._crc = (self._crc >> 1) ^ (self._polynom & mask)
    
    def get_crc(self):
        return ~self._crc & 0xFFFFFFFF