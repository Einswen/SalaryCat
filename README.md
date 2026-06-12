# Salary Cat (Yuexin Miao)

# 我真的特别爱你 月薪喵 小猫 月薪猫
It renders terminal GIF animations such as `cat.gif`, `maltese.gif`, and
`kuromi-1-8.gif`, with smooth ANSI TrueColor playback and optional music.

## Download without Python

Users do not need to install Python if they download the standalone binaries
from GitHub Releases:

[https://github.com/Einswen/SalaryCat/releases/]

### macOS

Apple Silicon Macs:

```bash
curl -L -o /tmp/tban-cat https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-macos-arm64 && chmod +x /tmp/tban-cat && /tmp/tban-cat
```

Intel Macs:

```bash
curl -L -o /tmp/tban-cat https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-macos-intel && chmod +x /tmp/tban-cat && /tmp/tban-cat
```

### Windows

```powershell
irm https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-windows.exe -OutFile $env:TEMP\tban-cat.exe; & $env:TEMP\tban-cat.exe
```

If macOS Gatekeeper or Windows SmartScreen blocks the file, allow the app once
and run the same command again.

One-line examples for different built-in GIFs:

macOS Apple Silicon:

```bash
curl -L -o /tmp/tban-cat https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-macos-arm64 && chmod +x /tmp/tban-cat && /tmp/tban-cat --gif cat.gif
curl -L -o /tmp/tban-cat https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-macos-arm64 && chmod +x /tmp/tban-cat && /tmp/tban-cat --gif maltese.gif
curl -L -o /tmp/tban-cat https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-macos-arm64 && chmod +x /tmp/tban-cat && /tmp/tban-cat --gif kuromi
```

Windows PowerShell:

```powershell
irm https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-windows.exe -OutFile $env:TEMP\tban-cat.exe; & $env:TEMP\tban-cat.exe --gif cat.gif
irm https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-windows.exe -OutFile $env:TEMP\tban-cat.exe; & $env:TEMP\tban-cat.exe --gif maltese.gif
irm https://github.com/Einswen/SalaryCat/releases/download/v0.1.1/tban-cat-windows.exe -OutFile $env:TEMP\tban-cat.exe; & $env:TEMP\tban-cat.exe --gif kuromi
```

The standalone binaries include the bundled `cat.GIF`, `maltese.gif`,
`kuromi-1-8.gif`, and `music.mp3`. You can still place your own GIF or
`music.mp3` in the same folder to override them.

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

Default behavior:

- `cat.gif` / `cat.GIF`: plays `music.mp3` and shows the footer love message
- `maltese.gif`, `kuromi-1-8.gif`, and other GIFs: silent by default and no footer message

This repository also includes a cute Maltese puppy character animation:
```text
maltese.gif
```

And a Kuromi animation:
```text
kuromi-1-8.gif
```

## Usage

```bash
tban-cat
tban-cat --gif maltese.gif
tban-cat --gif kuromi-1-8.gif
tban-cat --gif kuromi
tban-cat --fps
tban-cat --scale 1
tban-cat --margin-rows 1
tban-cat --no-music
tban-cat --message "I love you"
tban-cat --music music.mp3
```

`kuromi` is supported as a short alias for `kuromi-1-8.gif`.

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

Build a standalone binary locally:

```bash
python3 -m pip install ".[build]"
python3 -m PyInstaller --onefile --name tban-cat --add-data "cat.GIF:." --add-data "maltese.gif:." --add-data "kuromi-1-8.gif:." --add-data "music.mp3:." main.py
```

On Windows, use semicolons in `--add-data`:

```powershell
py -m pip install ".[build]"
py -m PyInstaller --onefile --name tban-cat --add-data "cat.GIF;." --add-data "maltese.gif;." --add-data "kuromi-1-8.gif;." --add-data "music.mp3;." main.py
```

Check syntax:

```bash
python3 -m py_compile audio_player.py gif_loader.py renderer.py main.py
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
