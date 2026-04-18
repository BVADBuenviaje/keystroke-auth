import time
import json
import numpy as np
from pynput import keyboard

# Define your parameters
TARGET_PASSWORD = "math"
N_ATTEMPTS = 10

def record_single_attempt():
    """Captures discrete on_press and on_release keyboard events in milliseconds."""
    print(f"\nType '{TARGET_PASSWORD}' and press ENTER:")
    events = []
    
    def on_press(key):
        try:
            # Record events as: (action, key, timestamp)
            events.append(('press', key.char, time.time()))
        except AttributeError:
            pass # Ignore special keys like shift

    def on_release(key):
        try:
            events.append(('release', key.char, time.time()))
        except AttributeError:
            if key == keyboard.Key.enter:
                return False # Stop listener when they hit enter

    # Start the invisible stopwatch
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
        
    return events

def process_timings(events):
    """Calculates Dwell and Flight times as continuous variables."""
    press_times = {}
    release_times = {}
    
    # Extract the timestamps for each character
    for action, char, timestamp in events:
        if action == 'press' and char not in press_times:
            press_times[char] = timestamp
        elif action == 'release' and char not in release_times:
            release_times[char] = timestamp

    # 1. Dwell Time Calculation: time_released - time_pressed
    dwells = {}
    for char in TARGET_PASSWORD:
        if char in press_times and char in release_times:
            # Multiply by 1000 to convert seconds to milliseconds
            dwells[char] = (release_times[char] - press_times[char]) * 1000

    # 2. Flight Time Calculation: time_pressed(key2) - time_released(key1)
    flights = {}
    for i in range(len(TARGET_PASSWORD) - 1):
        char1 = TARGET_PASSWORD[i]
        char2 = TARGET_PASSWORD[i+1]
        if char1 in release_times and char2 in press_times:
            flights[f"{char1}-{char2}"] = (press_times[char2] - release_times[char1]) * 1000

    return dwells, flights

def main():
    # Data Structures: dict [str, list[float]]
    raw_dwells = {char: [] for char in TARGET_PASSWORD}
    raw_flights = {f"{TARGET_PASSWORD[i]}-{TARGET_PASSWORD[i+1]}": [] for i in range(len(TARGET_PASSWORD)-1)}

    print(f"--- BEHAVIORAL REGISTRATION ---")
    print(f"We need {N_ATTEMPTS} successful attempts to build your baseline.")
    
    # Prompt the user to type the password N times
    successful_attempts = 0
    while successful_attempts < N_ATTEMPTS:
        events = record_single_attempt()
        
        # Verify they actually typed the right password
        typed_string = "".join([e[1] for e in events if e[0] == 'press'])
        if typed_string == TARGET_PASSWORD:
            dwells, flights = process_timings(events)
            
            # Store the data
            for char, t in dwells.items():
                raw_dwells[char].append(t)
            for transition, t in flights.items():
                raw_flights[transition].append(t)
                
            successful_attempts += 1
            print(f"Success! ({successful_attempts}/{N_ATTEMPTS} attempts recorded)")
        else:
            print(f"You typed '{typed_string}'. Please type exactly '{TARGET_PASSWORD}'.")

    # Compute μ (mean) and σ (standard deviation) for dwell and flight times
    profile = {
        "dwell_means": {k: np.mean(v) for k, v in raw_dwells.items()},
        "dwell_stdevs": {k: np.std(v, ddof=1) for k, v in raw_dwells.items()}, # ddof=1 for sample standard deviation
        "flight_means": {k: np.mean(v) for k, v in raw_flights.items()},
        "flight_stdevs": {k: np.std(v, ddof=1) for k, v in raw_flights.items()}
    }

    # Save the baseline profile to a file for Developer 2
    with open('baseline_profile.json', 'w') as f:
        json.dump(profile, f, indent=4)
        
    print("\nRegistration Complete! 'baseline_profile.json' has been generated.")

if __name__ == "__main__":
    main()