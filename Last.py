import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from mne import create_info
from mne.io import RawArray
import numpy as np

# Initialize BrainFlow and set parameters
params = BrainFlowInputParams()
params.serial_port = 'COM5'
board_id = BoardIds.GANGLION_BOARD.value
board = BoardShim(board_id, params)

# Prepare session
board.prepare_session()

# Start stream
board.start_stream()

# Define parameters for real-time plot
window_size = 1321  # Number of data points to display
refresh_rate = 10  # Refresh rate in milliseconds

# Initialize data containers
eeg_channels = [2]
eeg_data = np.zeros(window_size)
times = np.linspace(-window_size / board.get_sampling_rate(board.get_board_id()), 0, window_size)

# Define channel info
ch_types = ['eeg'] * len(eeg_channels)
ch_names = ['2']
sfreq = board.get_sampling_rate(board.get_board_id())
print("Rate:", sfreq)

info = create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)

# Set up the figure and axes
fig, (ax_alpha, ax_beta) = plt.subplots(2, 1, figsize=(12, 6))
line_alpha, = ax_alpha.plot(times, eeg_data, label='Alpha (7-12 Hz)')
line_beta, = ax_beta.plot(times, eeg_data, label='Beta (14-19 Hz)')
ax_alpha.set_title('Alpha Band')
ax_alpha.set_xlabel('Time (s)')
ax_alpha.set_ylabel('Amplitude (V)')
ax_alpha.legend()
ax_alpha.set_ylim(-100, 400)  # Set voltage range for alpha
ax_alpha.axhline(y=20, color='r', linestyle='--', linewidth=0.5)  # Horizontal line at 20 µV
ax_alpha.axhline(y=200, color='r', linestyle='--', linewidth=0.5)  # Horizontal line at 200 µV
ax_alpha.axhspan(20, 200, color='green', alpha=0.3)  # Horizontal span with background color


# ax_alpha.set_ylim(-30, 30)  # Set voltage range for alpha
ax_beta.set_title('Beta Band')
ax_beta.set_xlabel('Time (s)')
ax_beta.set_ylabel('Amplitude (V)')
ax_beta.legend()
ax_beta.set_ylim(-10, 50)  # Set voltage range for beta waves
ax_beta.axhline(y=5, color='r', linestyle='--', linewidth=0.5)  # Horizontal line at 5 µV
ax_beta.axhline(y=30, color='r', linestyle='--', linewidth=0.5)  # Horizontal line at 30 µV
ax_beta.axhspan(5, 30, color='green', alpha=0.3)  # Horizontal span with background color

plt.tight_layout()


def update(frame):
    global eeg_data
    data = board.get_current_board_data(window_size)
    eeg_data = data[eeg_channels, :] / 1000000  # Convert to volts and take the last window_size samples
    # eeg_data = data[eeg_channels, :]
    # Create RawArray and apply filters
    raw = RawArray(eeg_data, info)
    raw_notch = raw.copy().notch_filter(50)
    clean = raw_notch.copy().filter(1, 45)

    alpha = clean.copy().filter(8, 12)
    beta = clean.copy().filter(13, 30)

    alpha_data = alpha.get_data()[0] * 1000000
    beta_data = beta.get_data()[0] * 1000000

    # Ensure alpha_data and beta_data have the same length as times
    if len(alpha_data) < len(times):
        alpha_data = np.pad(alpha_data, (len(times) - len(alpha_data), 0), 'constant')
    else:
        alpha_data = alpha_data[-len(times):]

    if len(beta_data) < len(times):
        beta_data = np.pad(beta_data, (len(times) - len(beta_data), 0), 'constant')
    else:
        beta_data = beta_data[-len(times):]

    # Update lines
    line_alpha.set_ydata(alpha_data)
    line_beta.set_ydata(beta_data)
    return line_alpha, line_beta


# Create animation
ani = FuncAnimation(fig, update, interval=refresh_rate, blit=True, save_count=200)

# Show the plot
plt.show()

# Stop the stream and release the session when done
board.stop_stream()
board.release_session()
