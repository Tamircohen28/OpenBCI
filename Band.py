class Band:
    def __init__(self, name: str, freq_low: float, freq_high: float, ampl_low: float, ampl_high: float):
        self.name = name
        # Frequency (Hz)
        self.freq_low = freq_low
        self.freq_high = freq_high
        # Amplitude µV
        self.ampl_low = ampl_low
        self.ampl_high = ampl_high
