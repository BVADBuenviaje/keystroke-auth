# Biometric Keystroke Authentication System

## Overview
This project is a behavioral biometric authentication system built in Python. Instead of relying solely on a traditional password ("what you know"), this system analyzes keystroke dynamics to verify a user's identity based on their unique typing rhythm ("who you are").

The system measures two primary physical behaviors:
- **Dwell Time:** The duration a specific key is physically held down.
- **Flight Time:** The time gap between releasing one key and pressing the next.

By calculating the mean and standard deviation of these microsecond timings, the system generates a statistical baseline (a normal distribution) to detect anomalies and block imposters—even if they type the correct password.

## Features
- Enrollment and authentication using keystroke dynamics
- Statistical analysis of typing patterns (mean, standard deviation)
- Baseline profile storage in JSON format
- Easy-to-use Python scripts

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd keystroke-auth
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Enrollment
Run the enrollment script to create a baseline profile:
```bash
python enrollment.py
```
Follow the on-screen instructions to type your password several times. The system will record your keystroke timings and save your profile to `baseline_profile.json`.

### Authentication
(If you have an authentication script, describe its usage here.)

## How It Works
- The system records the time each key is pressed and released.
- It calculates dwell and flight times for each typing session.
- After several samples, it computes the mean and standard deviation for each metric.
- During authentication, it compares new samples to the baseline profile to determine if the typing pattern matches.

## Requirements
- Python 3.7+
- See `requirements.txt` for dependencies

## License
MIT License
