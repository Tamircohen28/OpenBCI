import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from brainflow import BoardShim, BrainFlowInputParams, BoardIds

# Configuration
params = BrainFlowInputParams()
params.serial_port = 'COM3'
board_id = BoardIds.GANGLION_BOARD.value
num_samples = 50  # Number of samples to display on the plot at a time
board = BoardShim(board_id, params)

# Initialize board
board.prepare_session()

# Initialize data store for the plot
eeg_data = np.zeros((num_samples, 4))  # Ganglion has 4 channels


def update_plot(frame):
    global eeg_data
    data = board.get_current_board_data(num_samples)[1:5]  # Get latest EEG data
    if data.shape[1] < num_samples:
        # If fewer samples are returned, fill the rest with zeros
        padded_data = np.zeros((4, num_samples))
        padded_data[:, -data.shape[1]:] = data
        data = padded_data
    eeg_data = np.transpose(data)
    for i in range(4):
        lines[i].set_ydata(eeg_data[:, i])
    return lines


def init_plot():
    for line in lines:
        line.set_data(range(num_samples), np.zeros(num_samples))
    return lines


# Set up the figure for plotting
fig, ax = plt.subplots()
ax.set_ylim(-5000, 5000)  # Adjusted y-axis limits for a more zoomed-out view
ax.set_xlim(0, num_samples)
lines = [ax.plot(np.arange(num_samples), np.zeros(num_samples), label=f'Channel {i + 1}')[0] for i in range(4)]
ax.legend()

# Use matplotlib animation to update the plot in real time
ani = FuncAnimation(fig, update_plot, init_func=init_plot, interval=10, blit=True, save_count=200)

# Start streaming data
board.start_stream()
plt.show()

# Cleanup
board.stop_stream()
board.release_session()
