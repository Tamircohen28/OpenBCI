from typing import List

from brainflow import BoardIds
from Band import Band

# Configuration
SERIAL_PORT = 'COM5'
BOARD_ID: int = BoardIds.GANGLION_BOARD.value

# Number of samples to display on the plot at a time
SAMPLES_NUM = 50

# Frequency bands
BANDS = [
    Band('Alpha', 8, 12, 20, 200),
    Band('Beta', 13, 30, 5, 30)
    # Band('Gamma', 15, 50, 10, 200)
]

# Define parameters for real-time plot
# Number of data points to display
WINDOW_SIZE = 500
# Refresh rate in milliseconds
REFRESH_RATE = 10
SAVE_COUNT = 200

# Pins Connected to signal
OPENBCI_PINS: List[int] = [2]

##########
# FILTER #
##########
NOTCH_FILTER = 50
LOW_FILTER_LEVEL = 1
HIGH_FILTER_LEVEL = 45

BARINFLOW_VOLT_RATION = 1e6

FIG_WIDTH = 12
FIG_HEIGHT = 6


OUTPUT_DIR = "Outputs"
STATS_FILE = "statistics.json"
