import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import butter, filtfilt
from brainflow import BoardShim, BrainFlowInputParams, BoardIds
from Constant import BANDS, SAMPLES_NUM, SERIAL_PORT, SAMPLING_FREQUENCY


# Bandpass filter function
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y


def update_plot(frame):
    global eeg_data
    data = board.get_current_board_data(SAMPLES_NUM)[0:5]  # Get latest EEG data
    if data.shape[1] < SAMPLES_NUM:
        # If fewer samples are returned, fill the rest with zeros
        padded_data = np.zeros((5, SAMPLES_NUM))
        padded_data[:, -data.shape[1]:] = data
        data = padded_data
    eeg_data = np.transpose(data)

    for i, band_obj in enumerate(BANDS):
        channel_data = eeg_data[:, i]
        filtered_data = bandpass_filter(channel_data, band_obj.low, band_obj.high, SAMPLING_FREQUENCY)
        lines[i][band_obj.name].set_ydata(filtered_data)
    return [line for band_lines in lines for line in band_lines.values()]


def init_plot():
    for band_lines in lines:
        for line in band_lines.values():
            line.set_data(range(SAMPLES_NUM), np.zeros(SAMPLES_NUM))
    return [line for band_lines in lines for line in band_lines.values()]


if __name__ == '__main__':
    # Configuration
    params = BrainFlowInputParams()
    params.serial_port = SERIAL_PORT
    board_id = BoardIds.GANGLION_BOARD.value
    # num_samples = 50  # Number of samples to display on the plot at a time
    board = BoardShim(board_id, params)

    # Initialize board
    board.prepare_session()

    # Initialize data store for the plot
    eeg_data = np.zeros((SAMPLES_NUM, 4))  # Ganglion has 4 channels

    # Set up the figure for plotting
    fig, axs = plt.subplots(len(BANDS), 1, figsize=(10, 8))

    lines = []
    for i, band_obj in enumerate(BANDS):
        ax = axs[i]
        # Plot axes x=0 and y=0, dashed.
        ax.axhline(band_obj.low, ls='--', c='black', lw=0.5)
        ax.axhline(band_obj.high, ls='--', c='black', lw=0.5)
        ax.axhline((band_obj.high + band_obj.low) / 2, ls='--', c='black', lw=0.5)
        ax.axhline(0, ls='--', c='black', lw=0.5)
        ax.set_xlim(0, SAMPLES_NUM)
        channel_lines = {}
        ax.set_ylim(-band_obj.high, band_obj.high * 2)  # Adjusted y-axis limits for a more zoomed-out view
        line, = ax.plot(np.arange(SAMPLES_NUM), np.zeros(SAMPLES_NUM), label=f'{band_obj.name}')
        channel_lines[band_obj.name] = line
        ax.legend()
        lines.append(channel_lines)

    # Use matplotlib animation to update the plot in real time
    ani = FuncAnimation(fig, update_plot, init_func=init_plot, interval=50, blit=True, save_count=200)

    # Start streaming data
    board.start_stream()
    plt.show()

    # Cleanup
    board.stop_stream()
    board.release_session()
