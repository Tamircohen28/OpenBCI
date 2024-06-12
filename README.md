
# OpenBCI Brainwave Monitor

## Overview
This project is developed for the Brain-Gurion 5.0 hackathon and utilizes OpenBCI to monitor and analyze brainwave data. It is designed to help detect distress in individuals by analyzing brainwave patterns and alerting when irregular activities are observed. The entire project was developed within a 12-hour window and includes three main Python scripts: `monitor.py`, `analyze.py`, and `watch.py`.

## Features
- **Real-time Brainwave Monitoring:** Utilizes `monitor.py` to monitor and plot brainwave data in real-time.
- **Data Analysis:** Uses `analyze.py` to calculate statistics on the brainwave data to establish a baseline for normal brain activity.
- **Distress Detection:** Employs `watch.py` to continuously monitor brainwaves and alert users to irregular brain activity that may indicate distress.

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourgithub/brainwave-monitor.git
   ```
2. **Navigate to the Project Directory:**
   ```bash
   cd brainwave-monitor
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Follow these steps to run the application:

1. **Monitor Brainwaves:**
   ```bash
   python monitor.py
   ```
   - This script will start the real-time monitoring and plotting of brainwaves.

2. **Analyze Brainwaves:**
   ```bash
   python analyze.py
   ```
   - Run this script after collecting sufficient data to calculate necessary statistics for normal brain activity.

3. **Watch for Distress:**
   ```bash
   python watch.py
   ```
   - This script uses the statistics from `analyze.py` to monitor for any irregular activities and alert if anomalies are detected.

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your enhancements.

## Acknowledgments
- Thanks to the Brain-Gurion 5.0 hackathon organizers and mentors.
- Special thanks to the OpenBCI community for their invaluable resources.

## Contact
For more information, please contact [tamircohen2468@gmail.com](mailto:tamircohen2468@gmail.com).
