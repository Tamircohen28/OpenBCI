import sys
import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from brainflow import BoardShim, BrainFlowInputParams, BoardIds
import mne
from mne.io import RawArray
from mne.channels import make_standard_montage
from mne import create_info

if __name__ == '__main__':
    # eeg_channels = BoardShim.get_eeg_channels(BoardIds.GANGLION_BOARD.value)
    # print(eeg_channels)
    # sys.exit(0)

    params = BrainFlowInputParams()
    params.serial_port = 'COM5'
    board_id = BoardIds.GANGLION_BOARD.value
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()
    time.sleep(3)
    data = board.get_board_data()  # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()

    egg_channels = [2]
    egg_data = data[egg_channels, :]
    egg_data = egg_data / 1000000

    ch_types = ['eeg'] * len(egg_channels)
    ch_names = ['2']

    # Define the sample rate (e.g., 250 Hz)
    sfreq = board.get_sampling_rate(board.get_board_id())
    print("Rate ", sfreq)
    # Create info structure
    info = create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    # Create RawArray
    raw = RawArray(egg_data, info)

    raw_notch = raw.copy().notch_filter(50)
    clean = raw_notch.copy().filter(1, 45)
    clean.compute_psd().plot()
    alpha = clean.filter(7, 12)
    beta = clean.filter(14, 19)
    print(alpha.get_data())
    print(beta.get_data())
    # Get data for plotting
    alpha_data = alpha.get_data()[0]
    beta_data = beta.get_data()[0]

    times = raw.times

    # Plot alpha and beta bands
    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(times, alpha_data, label='Alpha (7-12 Hz)')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (V)')
    plt.title('Alpha Band')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(times, beta_data, label='Beta (14-19 Hz)')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (V)')
    plt.title('Beta Band')
    plt.legend()

    plt.tight_layout()
    plt.show()
    # a = raw.copy().notch_filter(7.5, 12.5)
    # # b = raw.copy().filter(14.5, 19.5)
    #
    # # Optional: Set montage for better visualization (assuming standard 10-20 system)
    # # montage = make_standard_montage('standard_1020')
    # # a.set_montage(montage)
    #
    # # # Plot the raw data to visualize
    # # a.plot(n_channels=len(ch_names), scalings='auto', title='Alpha Waves', show=True, block=True)
    #
    # # Step 4: Compute PSD
    # psd = a.compute_psd(fmin=8., fmax=12., tmin=0, tmax=None)
    #
    # # Plot the PSD
    # psd.plot(picks='eeg', show=True, average=True)
    # print("PSD", psd)
    # # Show the PSD data using matplotlib
    # plt.figure(figsize=(10, 6))
    # for i, ch_name in enumerate(ch_names):
    #     plt.plot(psd[i], label=ch_name)
    # plt.title('Power Spectral Density (8-12 Hz)')
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Power Spectral Density (dB/Hz)')
    # plt.legend(loc='upper right')
    # plt.show()

# # Configuration
# params = BrainFlowInputParams()
# params.serial_port = 'COM3'
# board_id = BoardIds.GANGLION_BOARD.value
# num_samples = 50  # Number of samples to display on the plot at a time
# board = BoardShim(board_id, params)
#
# # Initialize board
# board.prepare_session()
#
# # Initialize data store for the plot
# eeg_data = np.zeros((num_samples, 4))  # Ganglion has 4 channels
#
#
# def update_plot(frame):
#     global eeg_data
#     data = board.get_current_board_data(num_samples)[1:5]  # Get latest EEG data
#     if data.shape[1] < num_samples:
#         # If fewer samples are returned, fill the rest with zeros
#         padded_data = np.zeros((4, num_samples))
#         padded_data[:, -data.shape[1]:] = data
#         data = padded_data
#     eeg_data = np.transpose(data)
#     for i in range(4):
#         lines[i].set_ydata(eeg_data[:, i])
#     return lines
#
#
# def init_plot():
#     for line in lines:
#         line.set_data(range(num_samples), np.zeros(num_samples))
#     return lines
#
#
# # Set up the figure for plotting
# fig, ax = plt.subplots()
# ax.set_ylim(-5000, 5000)  # Adjusted y-axis limits for a more zoomed-out view
# ax.set_xlim(0, num_samples)
# lines = [ax.plot(np.arange(num_samples), np.zeros(num_samples), label=f'Channel {i + 1}')[0] for i in range(4)]
# ax.legend()
#
# # Use matplotlib animation to update the plot in real time
# ani = FuncAnimation(fig, update_plot, init_func=init_plot, interval=10, blit=True, save_count=200)
#
# # Start streaming data
# board.start_stream()
# plt.show()
#
# # Cleanup
# board.stop_stream()
# board.release_session()
