from collections.abc import Sequence
import socket

# Needed for tracking recent person locations, which are used for motion detection.
class RingBuffer(Sequence):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items = []
        self.oldestIndex = 0

    def add(self, item):
        if len(self.items) < self.capacity:
            self.items.append(item)
        else:
            self.items[self.oldestIndex] = item
            self.oldestIndex = (self.oldestIndex+1) % self.capacity

    def translateIndex(self, i):
        return (self.oldestIndex + i) % self.capacity

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.items[self.translateIndex(i)]
        if isinstance(i, slice):
            start, stop, step = i.indices(len(self.items))
            return [self.items[idx] for idx in range(start, stop, step)]

    def __len__(self):
        return len(self.items)
    

# Copied from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def getIPAddress() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
