from brainflow import BoardIds
from Band import Band

# Configuration
SERIAL_PORT = 'COM5'
BOARD_ID = BoardIds.GANGLION_BOARD.value

# Number of samples to display on the plot at a time
SAMPLES_NUM = 50

# Update according to your device's sampling rate
SAMPLING_FREQUENCY = 250  # Sampling rate of the Ganglion board

# Frequency bands
BANDS = [
    Band('Delta', 0.5, 4),
    Band('Theta', 4, 8),
    Band('Alpha', 8, 13),
    Band('Beta', 13, 30),
    Band('Gamma', 30, 100)
]
