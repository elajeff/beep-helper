# Beep Helper

Beep Helper is a small Windows desktop utility that plays a synthesized tone at a configurable interval.

## Features

- Set the interval from 0.01 to 86400 seconds, including fractional values.
- Adjust the generated tone volume from 1% to 100%.
- Choose from three tone profiles:
  - Soft Bell: a quieter, decaying 659 Hz tone with a subtle octave harmonic.
  - Rising Chime: two overlapping tones ascending from 440 Hz to about 554 Hz.
  - Double Ping: two short 784 Hz tones separated by a brief pause.
- Start and stop the notifier from the desktop interface.
- Changing the interval while running stops the notifier. Start it again to use the new interval.

## Requirements

- Windows.
- Python 3 with Tkinter available.

The application uses Python's standard library and the Windows `winsound` module. No third-party package is required to run it from source.

## Run from source

Open PowerShell in the repository directory and run:

```powershell
py beep_helper.py
```

## Build the Windows executable

Install PyInstaller:

```powershell
py -m pip install pyinstaller
```

Build using the included specification:

```powershell
py -m PyInstaller --clean --noconfirm beep_helper.spec
```

The executable is created at:

```text
dist\beep_helper.exe
```

## Implementation

The application generates a short WAV audio file with a smooth volume envelope and plays it through Windows audio playback. The volume control adjusts the generated tone's amplitude; it does not change Windows master volume or individual application volumes.

## Limitations

- This is a local Windows utility, not a background service.
- It does not save user preferences between launches.
- Notifications depend on the application running and Windows audio being available.