class Counter:
    def __init__(self):
        self._n = 0

    def inc(self):
        self._n += 1
        return self._n

    def reset(self):
        self._n = 0
