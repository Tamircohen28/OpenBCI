import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from mne import create_info
from mne.io import RawArray
import numpy as np
from mne.utils import set_log_level

from Common.constant import *

RECORDED_DATA = {wave.name: [] for wave in BANDS}

# Disable logging from MNE
set_log_level('WARNING')


def save_recording():
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Generate a timestamped filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = os.path.join(OUTPUT_DIR, f'eeg_data_{timestamp}.csv')

    # Convert all collected data to a DataFrame and write to a CSV file
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in RECORDED_DATA.items()]))
    df.to_csv(output_file, index=False)
    print(f"Data has been saved to {output_file}")


def update(frame):
    global eeg_data
    # take the last window_size samples
    data = board.get_current_board_data(WINDOW_SIZE)

    # Convert to volts
    eeg_data = data[OPENBCI_PINS, :] / BARINFLOW_VOLT_RATION

    # Create RawArray and apply filters
    raw = RawArray(eeg_data, info)
    raw_notch = raw.copy().notch_filter(NOTCH_FILTER)
    clean = raw_notch.copy().filter(LOW_FILTER_LEVEL, HIGH_FILTER_LEVEL)

    for wave in BANDS:
        # Filter wave frequencies data
        # wave_data = clean.copy().compute_psd(fmin=wave.freq_low, fmax=wave.freq_high).get_data()[0] * 1e10
        wave_data = clean.copy().filter(wave.freq_low, wave.freq_high).get_data()[0] * BARINFLOW_VOLT_RATION

        # Ensure wave_data have the same length as times
        if len(wave_data) < len(times):
            wave_data = np.pad(wave_data, (len(times) - len(wave_data), 0), 'constant')
        else:
            wave_data = wave_data[-len(times):]

        # Update lines
        waves_lines_dict[wave.name].set_ydata(wave_data)
        # Save data for recording
        RECORDED_DATA[wave.name].extend(wave_data.tolist())

    return waves_lines_dict.values()


if __name__ == '__main__':
    # Initialize BrainFlow and set parameters
    params = BrainFlowInputParams()
    params.serial_port = SERIAL_PORT
    board = BoardShim(BOARD_ID, params)

    # TODO: add board mac and retry of connect (catch exception), timeout
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
    fig, axs = plt.subplots(len(BANDS), 1, figsize=(FIG_WIDTH, FIG_HEIGHT))
    waves_lines_dict = {}

    for (i, wave) in enumerate(BANDS):
        wave_ax = axs[i]
        wave_line, = wave_ax.plot(times, eeg_data, label=f'{wave.name} ({wave.freq_low}-{wave.freq_high} Hz)')
        waves_lines_dict[wave.name] = wave_line

        wave_ax.set_title(f'{wave.name} Waves')
        wave_ax.set_xlabel('Time (s)')
        wave_ax.set_ylabel('Amplitude (mV)')
        wave_ax.legend(loc='upper right')
        wave_ax.axhline(y=0, color='b', linestyle='--', linewidth=1)  # Horizontal line at x = 0
        wave_ax.axhline(y=wave.ampl_low, color='r', linestyle='--', linewidth=0.5)  # Horizontal line at low amplitude
        wave_ax.axhline(y=wave.ampl_high, color='r', linestyle='--',
                        linewidth=0.5)  # Horizontal line at high amplitude
        wave_ax.axhspan(wave.ampl_low, wave.ampl_high, color='green', alpha=0.3)  # Mark wanted values area
        wave_ax.set_yticks(
            [0] + [-wave.ampl_low, wave.ampl_low, wave.ampl_high, int(1.5 * wave.ampl_high)])  # Add y-axis ticks

    plt.tight_layout()

    # Create animation
    ani = FuncAnimation(fig, update, interval=REFRESH_RATE, blit=True, save_count=SAVE_COUNT)

    # Show the plot
    plt.show()

    # Stop the stream and release the session when done
    board.stop_stream()
    board.release_session()

    save_recording()
