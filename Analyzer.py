import json

import pandas as pd
import os
from Constant import BANDS, OUTPUT_DIR, STATS_FILE  # Make sure to import BANDS correctly


def calculate_wave_statistics(csv_file, bands):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    statistics = {}
    for wave in bands:
        if wave.name not in df.columns:
            print(f"Error: '{wave.name}' column not found in the CSV file.")
            continue

        # Calculate the average and standard deviation of the wave data
        statistics[wave.name] = (df[wave.name].mean(), df[wave.name].std())

    return statistics


if __name__ == '__main__':
    print("Locating DB")
    # Define the directory and get the latest CSV file
    csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')]
    latest_file = sorted(csv_files)[-1]
    csv_file = os.path.join(OUTPUT_DIR, latest_file)
    print(f"Found '{csv_file}', Starting Analysis...")
    # Calculate statistics
    wave_statistics = calculate_wave_statistics(csv_file, BANDS)

    # Print the results
    for wave_name, stats in wave_statistics.items():
        wave_mean, wave_std = stats
        print(f"{wave_name} Wave Data: Average = {wave_mean}, Standard Deviation = {wave_std}")

    # Write statistics to a JSON file
    with open(STATS_FILE, 'w') as f:
        json.dump(wave_statistics, f, indent=4)

    print(f"Statistics have been saved to {STATS_FILE}")
