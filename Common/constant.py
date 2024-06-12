from typing import List

from brainflow import BoardIds
from Common.band import Band

# Configuration
# TODO: Set this according to your machine
SERIAL_PORT = 'COM5'
# TODO: Set this according to your board
BOARD_ID: int = BoardIds.GANGLION_BOARD.value

# Frequency bands
BANDS = [
    Band('Alpha', 8, 12, 20, 200),
    Band('Beta', 14, 19, 5, 30)

    # Could add more costume waves, ex:
    # Band('Gamma', 15, 50, 10, 200)
]

# Define parameters for real-time plot
# Number of data points to display
WINDOW_SIZE = 1500
# Refresh rate in milliseconds
REFRESH_RATE = 10
# Number of frames to cache
SAVE_COUNT = 200

# Pins Connected to signal
# TODO: Set this to match pins connected at your board
OPENBCI_PINS: List[int] = [2]

##########
# FILTER #
##########
NOTCH_FILTER = 50
LOW_FILTER_LEVEL = 1
HIGH_FILTER_LEVEL = 45

# Brainflow send data as (µV) and we want to perform calculations as (V)
BARINFLOW_VOLT_RATION = 1e6

# plot diagram dimension
FIG_WIDTH = 12
FIG_HEIGHT = 6

OUTPUT_DIR = "../outputs"
STATS_FILE = "../statistics.json"
