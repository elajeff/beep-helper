import array
import math
import os
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import wave
import winsound

def _resource_path(relative_path):
    """Locate an asset in source runs and PyInstaller bundles."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Palette Design Tokens
BG_COLOR = "#121212"
CARD_BG = "#1E1E1E"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A0A0A0"
ACCENT_GREEN = "#10B981"
ACCENT_GREEN_HOVER = "#059669"
ACCENT_RED = "#EF4444"
ACCENT_RED_HOVER = "#DC2626"
BORDER_COLOR = "#2D2D2D"


class RefinedBeeperApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Beep Helper")
        self.root.geometry("380x520")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)
        self.root.iconbitmap(_resource_path(os.path.join("assets", "beep_helper.ico")))

        self.is_running = False
        self.loop_thread = None
        self.temp_wav_path = os.path.join(
            tempfile.gettempdir(), "beep_helper_sound.wav"
        )

        self.setup_styles()
        self.build_ui()

        # Handle app closure cleanly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Custom Dark Palette for TTK widgets
        style.configure(".", background=BG_COLOR, foreground=TEXT_PRIMARY)
        style.configure("TLabel", background=CARD_BG, foreground=TEXT_PRIMARY)
        style.configure(
            "TLabelframe",
            background=CARD_BG,
            bordercolor=BORDER_COLOR,
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "TLabelframe.Label",
            background=CARD_BG,
            foreground=TEXT_SECONDARY,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "TRadiobutton",
            background=CARD_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 9),
            focuscolor=CARD_BG,
        )
        style.map(
            "TRadiobutton",
            foreground=[("selected", TEXT_PRIMARY)],
            background=[("active", CARD_BG)],
        )

    def build_ui(self):
        # Main Container
        container = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        # Header Title
        title = tk.Label(
            container,
            text="BEEP HELPER",
            font=("Segoe UI", 16, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_COLOR,
        )
        title.pack(anchor="w", pady=(0, 2))

        subtitle = tk.Label(
            container,
            text="Play a sound at regular intervals",
            font=("Segoe UI", 9),
            fg=TEXT_SECONDARY,
            bg=BG_COLOR,
        )
        subtitle.pack(anchor="w", pady=(0, 20))

        # Card Container
        card = tk.Frame(
            container,
            bg=CARD_BG,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        card.pack(fill="x", pady=(0, 20))

        # 1. Interval Setting
        interval_label = ttk.Label(
            card, text="INTERVAL (SECONDS)", font=("Segoe UI", 8, "bold")
        )
        interval_label.pack(anchor="w", pady=(0, 6))

        interval_frame = tk.Frame(card, bg=CARD_BG)
        interval_frame.pack(fill="x", pady=(0, 16))

        self.interval_var = tk.StringVar(value="10")
        self.interval_var.trace_add("write", self.on_interval_changed)

        self.interval_entry = tk.Entry(
            interval_frame,
            textvariable=self.interval_var,
            font=("Segoe UI", 11),
            bg="#2A2A2A",
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            bd=5,
            width=8,
        )
        self.interval_entry.pack(side="left")

        unit_label = tk.Label(
            interval_frame,
            text="seconds",
            font=("Segoe UI", 9),
            fg=TEXT_SECONDARY,
            bg=CARD_BG,
        )
        unit_label.pack(side="left", padx=(10, 0))

        # 2. Volume Setting
        vol_label = ttk.Label(
            card, text="VOLUME", font=("Segoe UI", 8, "bold")
        )
        vol_label.pack(anchor="w", pady=(0, 6))

        self.vol_var = tk.IntVar(value=35)
        self.vol_slider = ttk.Scale(
            card,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.vol_var,
            command=self.update_vol_label,
        )
        self.vol_slider.pack(fill="x")

        self.vol_display = tk.Label(
            card,
            text=f"{self.vol_var.get()}%",
            font=("Segoe UI", 9),
            fg=TEXT_SECONDARY,
            bg=CARD_BG,
        )
        self.vol_display.pack(anchor="e", pady=(2, 16))

        # 3. Tone Profiles
        tone_label = ttk.Label(
            card, text="TONE PROFILE", font=("Segoe UI", 8, "bold")
        )
        tone_label.pack(anchor="w", pady=(0, 6))

        self.tone_var = tk.IntVar(value=1)
        r1 = ttk.Radiobutton(
            card,
            text="Soft Bell (659 Hz)",
            value=1,
            variable=self.tone_var,
        )
        r2 = ttk.Radiobutton(
            card,
            text="Rising Chime (440 to 554 Hz)",
            value=2,
            variable=self.tone_var,
        )
        r3 = ttk.Radiobutton(
            card,
            text="Double Ping (784 Hz)",
            value=3,
            variable=self.tone_var,
        )
        r1.pack(anchor="w", pady=3)
        r2.pack(anchor="w", pady=3)
        r3.pack(anchor="w", pady=3)

        # Start / Stop Action Button
        self.action_btn = tk.Button(
            container,
            text="START NOTIFIER",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_GREEN,
            fg="white",
            activebackground=ACCENT_GREEN_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.toggle_beeper,
            height=2,
        )
        self.action_btn.pack(fill="x")

        # Status Footer
        self.status_label = tk.Label(
            container,
            text="Status: Idle",
            font=("Segoe UI", 9),
            fg=TEXT_SECONDARY,
            bg=BG_COLOR,
        )
        self.status_label.pack(pady=(12, 0))

    def update_vol_label(self, val):
        self.vol_display.config(text=f"{int(float(val))}%")

    def on_interval_changed(self, *args):
        # Automatically stop loop if interval changes while running
        if self.is_running:
            self.stop_beeper()
            self.status_label.config(
                text="Status: Stopped (Interval changed)", fg=ACCENT_RED
            )

    def create_wav_file(self, profile_id=1, volume_pct=35):
        """Generate short, click-free synthesized tones for the selected profile."""
        sample_rate = 44100

        if profile_id == 1:
            # Soft Bell: quieter 659 Hz note with a subtle octave harmonic.
            events = [(0.0, 0.32, 659.25, 0.92, 0.18)]
            profile_gain = 0.36
        elif profile_id == 2:
            # Rising Chime: two overlapping notes, from A4 up to C#5.
            events = [
                (0.0, 0.25, 440.0, 0.56, 0.14),
                (0.11, 0.30, 554.37, 0.50, 0.10),
            ]
            profile_gain = 0.62
        else:
            # Double Ping: two short 784 Hz notes separated by a pause.
            events = [
                (0.0, 0.12, 783.99, 0.95, 0.06),
                (0.20, 0.15, 783.99, 0.78, 0.06),
            ]
            profile_gain = 0.56

        total_duration = max(start + duration for start, duration, *_ in events)
        num_samples = int(sample_rate * total_duration)
        volume = max(1, min(100, int(volume_pct)))
        amplitude = (volume / 100.0) ** 1.8 * 32767.0 * 0.82 * profile_gain
        raw_pcm = array.array("h")

        for i in range(num_samples):
            t = i / sample_rate
            mixed = 0.0

            for start, duration, frequency, level, harmonic in events:
                elapsed = t - start
                if not 0.0 <= elapsed < duration:
                    continue

                attack = min(1.0, elapsed / 0.008)
                release = min(1.0, (duration - elapsed) / 0.025)
                decay = math.exp(-4.2 * elapsed / duration)
                envelope = attack * release * decay

                phase = 2.0 * math.pi * frequency * elapsed
                tone = math.sin(phase) + harmonic * math.sin(2.0 * phase)
                mixed += level * envelope * tone

            sample = int(max(-32768, min(32767, mixed * amplitude)))
            raw_pcm.append(sample)

        with wave.open(self.temp_wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(raw_pcm.tobytes())

    def play_sound(self):
        profile_id = self.tone_var.get()
        vol = self.vol_var.get()
        self.create_wav_file(profile_id=profile_id, volume_pct=vol)
        winsound.PlaySound(
            self.temp_wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC
        )

    def beeper_loop(self, interval_seconds):
        while self.is_running:
            self.play_sound()
            # Step in 100ms slices for instantaneous stop responsiveness
            steps = int(interval_seconds * 10)
            for _ in range(steps):
                if not self.is_running:
                    break
                time.sleep(0.1)

    def stop_beeper(self):
        self.is_running = False
        self.action_btn.config(
            text="START NOTIFIER",
            bg=ACCENT_GREEN,
            activebackground=ACCENT_GREEN_HOVER,
        )

    def toggle_beeper(self):
        if not self.is_running:
            # Validate Interval Input
            try:
                interval = float(self.interval_var.get())
                if interval <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid Interval",
                    "Please enter a valid positive number for the interval.",
                )
                return

            self.is_running = True
            self.action_btn.config(
                text="STOP NOTIFIER",
                bg=ACCENT_RED,
                activebackground=ACCENT_RED_HOVER,
            )
            self.status_label.config(
                text=f"Status: Active ({interval}s interval)", fg=ACCENT_GREEN
            )

            self.loop_thread = threading.Thread(
                target=self.beeper_loop, args=(interval,), daemon=True
            )
            self.loop_thread.start()
        else:
            self.stop_beeper()
            self.status_label.config(text="Status: Idle", fg=TEXT_SECONDARY)

    def on_close(self):
        self.is_running = False
        try:
            if os.path.exists(self.temp_wav_path):
                os.remove(self.temp_wav_path)
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RefinedBeeperApp(root)
    root.mainloop()