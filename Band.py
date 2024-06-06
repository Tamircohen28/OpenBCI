from scipy.signal import butter, filtfilt


class Band:
    def __init__(self, name: str, low: float, high: float):
        self.name = name
        self.low = low
        self.high = high



