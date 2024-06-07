import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from mne import create_info
from mne.io import RawArray
import numpy as np
from Constant import *

RECORDED_DATA = []


def update(frame):
    global eeg_data
    data = board.get_current_board_data(WINDOW_SIZE)
    # eeg_data = data[OPENBCI_PINS, :] / 1e6

    # data = board.get_board_data()
    # Convert to volts and take the last window_size samples
    eeg_data = data[OPENBCI_PINS, :] / BARINFLOW_VOLT_RATION

    # Create RawArray and apply filters
    raw = RawArray(eeg_data, info)
    raw_notch = raw.copy().notch_filter(NOTCH_FILTER)
    clean = raw_notch.copy().filter(LOW_FILTER_LEVEL, HIGH_FILTER_LEVEL)

    for wave in BANDS:
        # Filter wave frequencies data
        wave_data = clean.copy().filter(wave.freq_low, wave.freq_high).get_data()[0] * BARINFLOW_VOLT_RATION

        # Ensure wave_data have the same length as times
        if len(wave_data) < len(times):
            wave_data = np.pad(wave_data, (len(times) - len(wave_data), 0), 'constant')
        else:
            wave_data = wave_data[-len(times):]

        # Update lines
        waves_lines_dict[wave.name].set_ydata(wave_data)

    return waves_lines_dict.values()


if __name__ == '__main__':
    # Initialize BrainFlow and set parameters
    params = BrainFlowInputParams()
    params.serial_port = SERIAL_PORT
    board = BoardShim(BOARD_ID, params)

    # Prepare session
    board.prepare_session()

    # Start stream
    board.start_stream()

    # Initialize data containers
    eeg_data = np.zeros(WINDOW_SIZE)
    times = np.linspace(-WINDOW_SIZE / board.get_sampling_rate(board.get_board_id()), 0, WINDOW_SIZE)

    # Define channel info
    ch_types = ['eeg'] * len(OPENBCI_PINS)
    ch_names = [str(pin) for pin in OPENBCI_PINS]
    info = create_info(ch_names=ch_names, sfreq=board.get_sampling_rate(board.get_board_id()), ch_types=ch_types)

    # Set up the figure and axes
    fig, axs = plt.subplots(len(BANDS), 1, figsize=(FIG_WIDTH, FIG_WIDTH))
    waves_lines_dict = {}
    for (i, wave) in enumerate(BANDS):
        wave_ax = axs[i]
        wave_line, = wave_ax.plot(times, eeg_data, label=f'{wave.name} ({wave.freq_low}-{wave.freq_high} Hz)')
        waves_lines_dict[wave.name] = wave_line

        wave_ax.set_title(f'{wave.name} Waves')
        wave_ax.set_xlabel('Time (s)')
        wave_ax.set_ylabel('Amplitude (V)')
        wave_ax.legend(loc='upper right')
        wave_ax.axhline(y=0, color='b', linestyle='--', linewidth=1)  # Horizontal line x = 0
        wave_ax.axhline(y=wave.ampl_low, color='r', linestyle='--', linewidth=0.5)  # Horizontal line at 20 µV
        wave_ax.axhline(y=wave.ampl_high, color='r', linestyle='--', linewidth=0.5)  # Horizontal line at 200 µV
        wave_ax.axhspan(wave.ampl_low, wave.ampl_high, color='green',
                        alpha=0.3)  # Horizontal span with background color
        wave_ax.set_yticks(
            [0] + [-wave.ampl_low, wave.ampl_low, wave.ampl_high, int(1.5 * wave.ampl_high)])  # Add y-axis ticks

    plt.tight_layout()

    # Create animation
    ani = FuncAnimation(fig, update, interval=REFRESH_RATE, blit=True, save_count=200)

    # Show the plot
    plt.show()

    # Stop the stream and release the session when done
    board.stop_stream()
    board.release_session()
