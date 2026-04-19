import time
import json
import numpy as np
from pynput import keyboard
import sys

# Parameters
BASELINE_FILE = "baseline_profile.json"
TARGET_PASSWORD = "math"
THRESHOLD = 2.0  # mean absolute Z-score threshold

def record_single_attempt():
    print(f"\nType '{TARGET_PASSWORD}' and press ENTER:")
    events = []
    def on_press(key):
        try:
            events.append(('press', key.char, time.time()))
        except AttributeError:
            pass
    def on_release(key):
        try:
            events.append(('release', key.char, time.time()))
        except AttributeError:
            if key == keyboard.Key.enter:
                return False
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    return events

def process_timings(events):
    press_times = {}
    release_times = {}
    for action, char, timestamp in events:
        if action == 'press' and char not in press_times:
            press_times[char] = timestamp
        elif action == 'release' and char not in release_times:
            release_times[char] = timestamp
    dwells = {}
    for char in TARGET_PASSWORD:
        if char in press_times and char in release_times:
            dwells[char] = (release_times[char] - press_times[char]) * 1000
    flights = {}
    for i in range(len(TARGET_PASSWORD) - 1):
        char1 = TARGET_PASSWORD[i]
        char2 = TARGET_PASSWORD[i+1]
        if char1 in release_times and char2 in press_times:
            flights[f"{char1}-{char2}"] = (press_times[char2] - release_times[char1]) * 1000
    return dwells, flights

def main():
    # Load baseline
    try:
        with open(BASELINE_FILE, 'r') as f:
            profile = json.load(f)
    except Exception as e:
        print(f"Error: Could not load baseline profile '{BASELINE_FILE}'. {e}")
        sys.exit(1)
    
    # Record login attempt
    events = record_single_attempt()
    typed_string = "".join([e[1] for e in events if e[0] == 'press'])
    if typed_string != TARGET_PASSWORD:
        print(f"You typed '{typed_string}'. Please type exactly '{TARGET_PASSWORD}'.")
        sys.exit(1)
    
    dwells, flights = process_timings(events)
    
    # Calculate Z-scores
    z_scores = []
    for char in TARGET_PASSWORD:
        mean = profile["dwell_means"].get(char)
        stdev = profile["dwell_stdevs"].get(char)
        val = dwells.get(char)
        if mean is None or stdev is None or val is None or stdev == 0:
            print(f"Error: Missing or invalid dwell data for '{char}'.")
            sys.exit(1)
        z = abs((val - mean) / stdev)
        z_scores.append(z)
        
    for i in range(len(TARGET_PASSWORD) - 1):
        key = f"{TARGET_PASSWORD[i]}-{TARGET_PASSWORD[i+1]}"
        mean = profile["flight_means"].get(key)
        stdev = profile["flight_stdevs"].get(key)
        val = flights.get(key)
        if mean is None or stdev is None or val is None or stdev == 0:
            print(f"Error: Missing or invalid flight data for '{key}'.")
            sys.exit(1)
        z = abs((val - mean) / stdev)
        z_scores.append(z)
        
    mean_abs_z = np.mean(z_scores)
    print(f"Mean absolute Z-score: {mean_abs_z:.2f}")
    
    if mean_abs_z <= THRESHOLD:
        print("Access Granted")
    else:
        print("Intruder Detected")

if __name__ == "__main__":
    main()