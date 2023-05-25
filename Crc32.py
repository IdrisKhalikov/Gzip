class Crc32:
    
    def __init__(self):
        self._crc = 0xFFFFFFFF
        self._polynom = 0xEDB88320
    
    def add(self, bytes):
        for byte in bytes:
            self._crc ^= byte
            for i in range(7,-1,-1):
                mask = -(self._crc & 1)
                self._crc = (self._crc >> 1) ^ (self._polynom & mask)

    def _reverse(self, value):
        result = 0
        for i in range(32):
            result = (result << 1) | ((value >> i) & 1)
        return result
    
    def get_crc(self):
        return ~self._crc & 0xFFFFFFFF