import argparse
import json
import os
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy
import pandas as pd
from matplotlib.animation import FuncAnimation
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from mne import create_info
from mne.io import RawArray
import numpy as np
import datetime
from mne.utils import set_log_level

from Constant import *

STATS = {wave.name: () for wave in BANDS}
ERROR_LINE = {wave.name: 0 for wave in BANDS}
ERROR_STATUS = {wave.name: False for wave in BANDS}

# Disable logging from MNE
set_log_level('WARNING')


def update(frame):
    global eeg_data
    data = board.get_current_board_data(WINDOW_SIZE)
    eeg_data = data[OPENBCI_PINS, :] / BARINFLOW_VOLT_RATION

    raw = RawArray(eeg_data, info)
    raw_notch = raw.copy().notch_filter(NOTCH_FILTER)
    clean = raw_notch.copy().filter(LOW_FILTER_LEVEL, HIGH_FILTER_LEVEL)

    for wave in BANDS:
        wave_data = clean.copy().filter(wave.freq_low, wave.freq_high).get_data()[0] * BARINFLOW_VOLT_RATION

        if len(wave_data) < len(times):
            wave_data = np.pad(wave_data, (len(times) - len(wave_data), 0), 'constant')
        else:
            wave_data = wave_data[-len(times):]

        waves_lines_dict[wave.name].set_ydata(wave_data)

        mean = np.mean(wave_data)
        error_line = ERROR_LINE[wave.name]

        in_error = False
        if wave.name == "Alpha":
            if mean < error_line:
                in_error = True
        else:
            if mean > error_line:
                in_error = True

        ERROR_STATUS[wave.name] = in_error

    if any(ERROR_STATUS.values()):
        print(f"User is not feeling as normal!: {ERROR_STATUS}")

    return waves_lines_dict.values()


def load_statistics(statistics_file):
    with open(statistics_file, 'r') as f:
        global STATS
        STATS = json.load(f)

    for wave in BANDS:
        mean = STATS[wave.name][0]
        std = STATS[wave.name][1]
        if wave.name == "Alpha":
            ERROR_LINE[wave.name] = mean - 2 * std
            ERROR_LINE[wave.name] = mean
            # ERROR_LINE[wave.name] = 10
        else:
            ERROR_LINE[wave.name] = mean + 2 * std
            ERROR_LINE[wave.name] = mean
            # ERROR_LINE[wave.name] = 20


if __name__ == '__main__':
    # Load statistics from the JSON file
    load_statistics(STATS_FILE)
    print(f"Statistics loaded from {STATS_FILE}")
    print(STATS)
    print("--------")
    print(ERROR_LINE)
    # time.sleep(5)

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
        error_line = ERROR_LINE[wave.name]

        wave_ax.set_title(f'{wave.name} Waves')
        wave_ax.set_xlabel('Time (s)')
        wave_ax.set_ylabel('Amplitude (V)')
        wave_ax.legend(loc='upper right')
        wave_ax.axhline(y=0, color='b', linestyle='--', linewidth=1)  # Horizontal line at x = 0
        wave_ax.axhline(y=wave.ampl_low, color='r', linestyle='--', linewidth=0.5)  # Horizontal line at low amplitude
        wave_ax.axhline(y=wave.ampl_high, color='r', linestyle='--',
                        linewidth=0.5)  # Horizontal line at high amplitude
        wave_ax.axhline(y=error_line, color='r', linestyle='--',
                        linewidth=1.5)  # Error Line
        wave_ax.axhspan(wave.ampl_low, wave.ampl_high, color='green', alpha=0.3)  # Mark wanted values area
        wave_ax.set_yticks(
            [0] + [-wave.ampl_low, error_line, wave.ampl_low, wave.ampl_high,
                   int(1.5 * wave.ampl_high)])  # Add y-axis ticks

    plt.tight_layout()

    # Create animation
    ani = FuncAnimation(fig, update, interval=REFRESH_RATE, blit=True, save_count=SAVE_COUNT)

    # Show the plot
    plt.show()

    # Stop the stream and release the session when done
    board.stop_stream()
    board.release_session()
