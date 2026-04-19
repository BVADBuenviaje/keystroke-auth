import customtkinter as ctk
import time

# Set the overall theme and appearance
ctk.set_appearance_mode("dark")  # "light", "dark", or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", or "dark-blue"


class KeystrokeAuthUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Biometric Keystroke Authentication")
        self.geometry("400x500")

        # Variables to store our timing data
        self.events = []
        self.target_password = "math"


        # --- Centering Frame ---
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.pack(expand=True, fill="both")

        # --- UI Elements ---
        self.content_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.content_frame.pack(expand=True)

        # Center all widgets in content_frame
        self.content_inner = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.content_inner.pack(expand=True)

        self.title_label = ctk.CTkLabel(self.content_inner, text="Secure Login", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=(50, 20))

        self.instruction_label = ctk.CTkLabel(self.content_inner, text=f"Type the password: '{self.target_password}'")
        self.instruction_label.pack(pady=(0, 20))

        self.password_entry = ctk.CTkEntry(self.content_inner, placeholder_text="Password", width=200, show="*")
        self.password_entry.pack(pady=10)

        # THE MAGIC: Bind the invisible stopwatch directly to the text box
        self.password_entry.bind("<KeyPress>", self.on_key_press)
        self.password_entry.bind("<KeyRelease>", self.on_key_release)

        self.login_button = ctk.CTkButton(self.content_inner, text="Authenticate", command=self.attempt_login)
        self.login_button.pack(pady=30)

        self.status_label = ctk.CTkLabel(self.content_inner, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_label.pack(pady=10)

        # Optional: Add fullscreen toggle with F11
        self.bind("<F11>", self.toggle_fullscreen)
        self.fullscreen = False

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def on_key_press(self, event):
        # Ignore special keys like Shift, Enter, CapsLock (len > 1)
        if len(event.keysym) == 1:
            self.events.append(('press', event.keysym, time.time()))

    def on_key_release(self, event):
        if len(event.keysym) == 1:
            self.events.append(('release', event.keysym, time.time()))

    def attempt_login(self):
        typed_password = self.password_entry.get()
        
        # 1. Check if they typed the right word first
        if typed_password != self.target_password:
            self.status_label.configure(text="Incorrect Password!", text_color="#ff4444")
            self.reset_box()
            return

        self.status_label.configure(text="Analyzing Biometrics...", text_color="#ffbb33")
        self.update() # Force the UI to update the text immediately
        time.sleep(0.5) # Fake a loading delay just for dramatic effect
        
        # --- THIS IS WHERE YOUR PARTNER'S MATH GOES ---
        # Right now, we are just pretending the math ran and returned "True"
        print("Raw events captured ready for backend:", self.events)
        is_real_user = True 
        
        if is_real_user:
            self.status_label.configure(text="Access Granted!", text_color="#00C851")
        else:
            self.status_label.configure(text="Intruder Detected!", text_color="#ff4444")
            
        self.reset_box()

    def reset_box(self):
        # Clear everything for the next attempt
        self.events = []
        self.password_entry.delete(0, 'end')

if __name__ == "__main__":
    app = KeystrokeAuthUI()
    app.mainloop()