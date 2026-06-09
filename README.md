# Salary Cat (Yuexin Miao)

# 我真的特别爱你 月薪喵 小猫 月薪猫
It renders `cat.gif` / `cat.GIF` in the terminal, loops the animation, and plays
`music.mp3` when available.

## Download without Python

Users do not need to install Python if they download the standalone binaries
from GitHub Releases:

[https://github.com/Einswen/SalaryCat/releases/]

### macOS

1. Download one file from the latest release:
   - Apple Silicon Macs: `tban-cat-macos-arm64`
   - Intel Macs: `tban-cat-macos-intel`
2. Open Terminal in the download folder.
3. Rename it or run it directly. Example for Apple Silicon:

```bash
chmod +x ./tban-cat-macos-arm64
./tban-cat-macos-arm64
```

If macOS Gatekeeper blocks it, run:

```bash
xattr -d com.apple.quarantine ./tban-cat-macos-arm64
./tban-cat-macos-arm64
```

### Windows

1. Download `tban-cat-windows.exe` from the latest release.
2. Open Windows Terminal or PowerShell in the download folder.
3. Run:

```powershell
.\tban-cat-windows.exe
```

If Windows SmartScreen warns about an unknown app, choose "More info" and then
"Run anyway".

The standalone binaries include the bundled `cat.GIF` and `music.mp3`. You can
still place your own `cat.gif` and `music.mp3` in the same folder to override
them.

## Requirements for Python install

- Python 3.10+
- A modern terminal with ANSI TrueColor support:
  - macOS Terminal
  - iTerm2
  - Windows Terminal
  - modern Linux terminals

Python dependency:

- Pillow

Audio playback uses system tools:

- macOS: `afplay`
- Windows: PowerShell MediaPlayer
- Linux: one of `ffplay`, `mpv`, `mpg123`, `cvlc`, or `play`

If no supported audio player is found, the animation still runs.

## Install with Python

From this project directory:

```bash
python3 -m pip install .
```

Recommended for command-line tools:

```bash
python3 -m pip install pipx
pipx install .
```

After installation, run:

```bash
tban-cat
```

## Assets

Run `tban-cat` in a directory containing:

```text
cat.gif
music.mp3
```

The GIF name is case-tolerant for common variants such as `cat.GIF`.
The music file is optional.

This repository also includes a cute Maltese puppy character animation:
```text
maltese.gif
```

## Usage

```bash
tban-cat
tban-cat --gif maltese.gif
tban-cat --fps
tban-cat --scale 0.8
tban-cat --margin-rows 1
tban-cat --no-music
tban-cat --music music.mp3
```

Sharper pixel-art rendering is the default. For smoother scaling:

```bash
tban-cat --smooth
```

To use half-block rendering:

```bash
tban-cat --half-block
```

Some terminals render half-block characters with visible horizontal seams. The
default solid-block mode avoids that.

## Development

Run directly without installing:

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

Record a short video of the project source code being typed into the terminal:

```bash
python3 code_typewriter.py
```

Useful recording options:

```bash
python3 code_typewriter.py main.py gif_loader.py --speed 120
python3 code_typewriter.py --max-lines 120 --hold 5
python3 code_typewriter.py --plain --no-line-numbers
```

Build a standalone binary locally:

```bash
python3 -m pip install ".[build]"
python3 -m PyInstaller --onefile --name tban-cat --add-data "cat.GIF:." --add-data "maltese.gif:." --add-data "music.mp3:." main.py
```

On Windows, use semicolons in `--add-data`:

```powershell
py -m pip install ".[build]"
py -m PyInstaller --onefile --name tban-cat --add-data "cat.GIF;." --add-data "maltese.gif;." --add-data "music.mp3;." main.py
```

Check syntax:

```bash
python3 -m py_compile audio_player.py gif_loader.py renderer.py main.py code_typewriter.py
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
