import customtkinter as ctk
import tkinter as tk
import time
import json
import numpy as np
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm

# Set theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class KeystrokeAuthUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Biometric Keystroke Authentication Engine")
        self.geometry("800x650")
        
        # Defaults
        self.target_password = "math" 
        self.threshold = 2.0
        self.required_attempts = 10
        self.profile = None
        
        self.load_profile()

        # --- TABS SETUP ---
        self.tabview = ctk.CTkTabview(self, width=750, height=600)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        # Set tab position to left if supported
        try:
            self.tabview._segmented_button.configure(anchor="w", justify="left")
        except Exception:
            pass  # Fallback if not supported in current customtkinter version

        self.tab_enroll = self.tabview.add("Enrollment")
        self.tab_login = self.tabview.add("Login")
        self.tab_viz = self.tabview.add("Visualization")

        self.setup_enrollment_tab()
        self.setup_login_tab()
        self.setup_viz_tab()

    def load_profile(self):
        if os.path.exists("baseline_profile.json"):
            try:
                with open("baseline_profile.json", 'r') as f:
                    self.profile = json.load(f)
                    # Load the saved password if it exists, otherwise keep default
                    self.target_password = self.profile.get("target_password", "math")
            except Exception:
                self.profile = None

    # ==========================================
    # TAB 1: ENROLLMENT
    # ==========================================
    def setup_enrollment_tab(self):
        self.enroll_events = []
        self.successful_attempts = 0
        self.raw_dwells = {char: [] for char in self.target_password}
        self.raw_flights = {f"{self.target_password[i]}-{self.target_password[i+1]}": [] for i in range(len(self.target_password)-1)}

        ctk.CTkLabel(self.tab_enroll, text="Create Your Biometric Baseline", font=("Arial", 24, "bold")).pack(pady=(10,5))
        
        # --- NEW: Dynamic Password Setter ---
        self.pw_setup_frame = ctk.CTkFrame(self.tab_enroll, fg_color="transparent")
        self.pw_setup_frame.pack(pady=10)
        
        ctk.CTkLabel(self.pw_setup_frame, text="Set Target Password:").pack(side="left", padx=5)
        self.pw_entry = ctk.CTkEntry(self.pw_setup_frame, width=150)
        self.pw_entry.insert(0, self.target_password)
        self.pw_entry.pack(side="left", padx=5)
        
        self.pw_btn = ctk.CTkButton(self.pw_setup_frame, text="Update", width=60, command=self.update_target_password)
        self.pw_btn.pack(side="left", padx=5)
        # ------------------------------------

        self.enroll_status = ctk.CTkLabel(self.tab_enroll, text=f"Attempts: {self.successful_attempts} / {self.required_attempts}", font=("Arial", 16))
        self.enroll_status.pack(pady=10)
        
        self.enroll_instruction = ctk.CTkLabel(self.tab_enroll, text=f"Type '{self.target_password}' and press ENTER")
        self.enroll_instruction.pack()
        
        self.enroll_action_entry = ctk.CTkEntry(self.tab_enroll, width=200, show="*")
        self.enroll_action_entry.pack(pady=10)
        self.enroll_action_entry.bind("<KeyPress>", self.on_enroll_press)
        self.enroll_action_entry.bind("<KeyRelease>", self.on_enroll_release)
        self.enroll_action_entry.bind("<Return>", self.process_enroll_attempt)

    def update_target_password(self):
        """Resets the enrollment system for a new password."""
        new_pw = self.pw_entry.get().strip()
        if len(new_pw) < 2:
            return
            
        self.target_password = new_pw
        self.successful_attempts = 0
        self.raw_dwells = {char: [] for char in self.target_password}
        self.raw_flights = {f"{self.target_password[i]}-{self.target_password[i+1]}": [] for i in range(len(self.target_password)-1)}
        
        self.enroll_status.configure(text=f"Attempts: 0 / {self.required_attempts}", text_color="white")
        self.enroll_instruction.configure(text=f"Type '{self.target_password}' and press ENTER")
        self.login_instruction.configure(text=f"Type '{self.target_password}' and press ENTER")

    def on_enroll_press(self, event):
        if len(event.keysym) == 1:
            self.enroll_events.append(('press', event.keysym, time.time()))

    def on_enroll_release(self, event):
        if len(event.keysym) == 1:
            self.enroll_events.append(('release', event.keysym, time.time()))

    def process_enroll_attempt(self, event):
        typed = self.enroll_action_entry.get()
        self.enroll_action_entry.delete(0, 'end')
        
        if typed != self.target_password:
            self.enroll_status.configure(text=f"Typo! Try again. (Attempts: {self.successful_attempts}/{self.required_attempts})", text_color="#ff4444")
            self.enroll_events = []
            return

        dwells, flights = self.extract_timings(self.enroll_events)
        self.enroll_events = []

        if not dwells or not flights:
            return

        for char, t in dwells.items():
            if char in self.raw_dwells:
                self.raw_dwells[char].append(t)
        for transition, t in flights.items():
            if transition in self.raw_flights:
                self.raw_flights[transition].append(t)

        self.successful_attempts += 1
        self.enroll_status.configure(text=f"Attempts: {self.successful_attempts} / {self.required_attempts}", text_color="white")

        if self.successful_attempts >= self.required_attempts:
            self.generate_baseline()

    def generate_baseline(self):
        # --------------------------------------------------------------------------------
        # BLOCK 2: PARAMETER ESTIMATION (BASELINE GENERATION)
        # Purpose: To estimate the population parameters (mu and sigma) that define the 
        # unique typing distribution of the user.
        # Mathematical Operation: Calculating the Sample Mean (x-bar) and Sample Standard 
        # Deviation (s) using n-1 degrees of freedom (Bessel's correction).
        # Expected Result: A stored statistical profile that establishes the "Normal" 
        # center and spread for every keystroke feature.
        # --------------------------------------------------------------------------------
        new_profile = {
            "target_password": self.target_password, # Save the new password to the file!
            "dwell_means": {k: np.mean(v) for k, v in self.raw_dwells.items() if v},
            "dwell_stdevs": {k: float(np.std(v, ddof=1)) if len(v)>1 else 0.0 for k, v in self.raw_dwells.items() if v},
            "flight_means": {k: np.mean(v) for k, v in self.raw_flights.items() if v},
            "flight_stdevs": {k: float(np.std(v, ddof=1)) if len(v)>1 else 0.0 for k, v in self.raw_flights.items() if v}
        }
        with open('baseline_profile.json', 'w') as f:
            json.dump(new_profile, f, indent=4)
        
        self.profile = new_profile
        self.enroll_status.configure(text="Baseline Generated! Proceed to Login Tab.", text_color="#00C851")

    # ==========================================
    # TAB 2: LOGIN
    # ==========================================
    def setup_login_tab(self):
        self.login_events = []
        
        ctk.CTkLabel(self.tab_login, text="Secure Login", font=("Arial", 24, "bold")).pack(pady=(50, 10))
        
        self.login_instruction = ctk.CTkLabel(self.tab_login, text=f"Type '{self.target_password}' and press ENTER")
        self.login_instruction.pack(pady=(0, 20))
        
        self.login_entry = ctk.CTkEntry(self.tab_login, width=200, show="*")
        self.login_entry.pack(pady=10)
        self.login_entry.bind("<KeyPress>", self.on_login_press)
        self.login_entry.bind("<KeyRelease>", self.on_login_release)
        self.login_entry.bind("<Return>", self.process_login_attempt)
        
        self.login_status = ctk.CTkLabel(self.tab_login, text="", font=("Arial", 18, "bold"))
        self.login_status.pack(pady=20)

    def on_login_press(self, event):
        if len(event.keysym) == 1:
            self.login_events.append(('press', event.keysym, time.time()))

    def on_login_release(self, event):
        if len(event.keysym) == 1:
            self.login_events.append(('release', event.keysym, time.time()))

    def process_login_attempt(self, event):
        typed = self.login_entry.get()
        self.login_entry.delete(0, 'end')
        
        if not self.profile:
            self.login_status.configure(text="No baseline found! Please Enroll first.", text_color="#ff4444")
            self.login_events = []
            return
            
        if typed != self.target_password:
            self.login_status.configure(text="Incorrect Password!", text_color="#ff4444")
            self.login_events = []
            return

        dwells, flights = self.extract_timings(self.login_events)
        self.login_events = []

        z_scores_with_labels = []
        z_scores = []
        is_valid = True
        
        # --------------------------------------------------------------------------------
        # BLOCK 3: STANDARDIZATION AND HYPOTHESIS TESTING
        # Purpose: To perform anomaly detection by determining if a new login attempt is 
        # a statistically significant outlier.
        # Mathematical Operation: Standardization (z = |x - mu| / sigma) to transform raw 
        # values into Z-scores, followed by an evaluation against a significance threshold.
        # Expected Result: A binary classification based on the Empirical Rule; scores 
        # within z = 2.0 cover 95% of expected behavior, identifying the genuine user.
        # --------------------------------------------------------------------------------
        for char in self.target_password:
            mean = self.profile["dwell_means"].get(char)
            stdev = self.profile["dwell_stdevs"].get(char)
            val = dwells.get(char)
            if mean is None or stdev is None or val is None or stdev == 0:
                is_valid = False
                break
            z = abs((val - mean) / stdev)
            z_scores.append(z)
            z_scores_with_labels.append((f"Dwell '{char}'", z))
            
        if is_valid:
            for i in range(len(self.target_password) - 1):
                key = f"{self.target_password[i]}-{self.target_password[i+1]}"
                mean = self.profile["flight_means"].get(key)
                stdev = self.profile["flight_stdevs"].get(key)
                val = flights.get(key)
                if mean is None or stdev is None or val is None or stdev == 0:
                    is_valid = False
                    break
                z = abs((val - mean) / stdev)
                z_scores.append(z)
                z_scores_with_labels.append((f"Flight '{key}'", z))

        if not is_valid or not z_scores:
            self.login_status.configure(text="Typing error. Try again.", text_color="#ff4444")
            return

        mean_abs_z = np.mean(z_scores)
        
        if mean_abs_z <= self.threshold:
            self.login_status.configure(text="Access Granted!", text_color="#00C851")
        else:
            self.login_status.configure(text="Intruder Detected!", text_color="#ff4444")

        self.update_visualization(mean_abs_z, z_scores_with_labels)
        self.tabview.set("Visualization")

    # ==========================================
    # TAB 3: VISUALIZATION
    # ==========================================
    def setup_viz_tab(self):
        self.viz_top_frame = ctk.CTkFrame(self.tab_viz)
        self.viz_top_frame.pack(fill="x", pady=10)
        
        self.score_label = ctk.CTkLabel(self.viz_top_frame, text="Awaiting Login Attempt...", font=("Arial", 20, "bold"))
        self.score_label.pack(pady=10)
        
        self.canvas_frame = tk.Frame(self.tab_viz, bg="#2b2b2b")
        self.canvas_frame.pack(fill="both", expand=True)

    def update_visualization(self, mean_z, z_scores_with_labels):
        result_text = f"Mean Absolute Z-Score: {mean_z:.2f}\n"
        result_text += "Verdict: " + ("AUTHORIZED" if mean_z <= self.threshold else "ANOMALY DETECTED")
        color = "#00C851" if mean_z <= self.threshold else "#ff4444"
        self.score_label.configure(text=result_text, text_color=color)

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(7, 4), dpi=100, facecolor='#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')

        # --------------------------------------------------------------------------------
        # BLOCK 4: PROBABILITY DENSITY VISUALIZATION
        # Purpose: To visually map the login attempt's probability relative to the user's 
        # established baseline distribution and identify specific keystroke anomalies.
        # Mathematical Operation: Mapping sample Z-scores as coordinate points (z, f(z)) 
        # onto the Probability Density Function (PDF) of a Standard Normal Distribution.
        # Expected Result: A graphical "Bell Curve" where threshold lines (+/- 2.0) define 
        # the acceptance region, allowing for visual confirmation of the login attempt.
        # --------------------------------------------------------------------------------
        x = np.linspace(-5, 5, 200)
        y = norm.pdf(x, 0, 1)
        ax.plot(x, y, color='#00C851', lw=2, label="Genuine User Range")
        
        ax.axvline(self.threshold, color='#ff4444', linestyle='--', lw=2, label="Threshold (\u00B12.0)")
        ax.axvline(-self.threshold, color='#ff4444', linestyle='--', lw=2)

        y_offset_direction = 1
        for label, z in z_scores_with_labels:
            y_val = norm.pdf(z, 0, 1)
            ax.scatter(z, y_val, color='orange', s=100, zorder=5, alpha=0.9)
            
            ax.annotate(
                label,
                (z, y_val),
                textcoords="offset points",
                xytext=(15, 15 * y_offset_direction), 
                ha='left',
                color='white',
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="#333333", ec="orange", lw=1, alpha=0.8)
            )
            y_offset_direction *= -1 

        ax.set_title("Keystroke Dynamics Distribution", color='white')
        ax.set_xlabel("Z-Score (Standard Deviations from Mean)", color='white')
        ax.legend(loc="upper right")

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ==========================================
    # HELPER MATH FUNCTION
    # ==========================================
    def extract_timings(self, events):
        # --------------------------------------------------------------------------------
        # BLOCK 1: DATA SAMPLING AND FEATURE EXTRACTION
        # Purpose: To convert raw keyboard events into discrete duration-based random 
        # variables for statistical analysis.
        # Mathematical Operation: Calculation of time deltas (delta t = t_end - t_start) 
        # for dwell and flight times.
        # Expected Result: Continuous numerical samples (in milliseconds) that represent 
        # the user's typing cadence for a single session.
        # --------------------------------------------------------------------------------
        press_times = {}
        release_times = {}
        for action, char, timestamp in events:
            if action == 'press' and char not in press_times:
                press_times[char] = timestamp
            elif action == 'release' and char not in release_times:
                release_times[char] = timestamp
                
        dwells, flights = {}, {}
        for char in self.target_password:
            if char in press_times and char in release_times:
                dwells[char] = (release_times[char] - press_times[char]) * 1000
                
        for i in range(len(self.target_password) - 1):
            char1, char2 = self.target_password[i], self.target_password[i+1]
            if char1 in release_times and char2 in press_times:
                flights[f"{char1}-{char2}"] = (press_times[char2] - release_times[char1]) * 1000
                
        return dwells, flights

if __name__ == "__main__":
    app = KeystrokeAuthUI()
    app.mainloop()