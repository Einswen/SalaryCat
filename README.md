# tban-cat

A TrueColor terminal GIF animation player inspired by classic nyancat.

It renders `cat.gif` / `cat.GIF` in the terminal, loops the animation, and plays
`music.mp3` when available.

## Requirements

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

## Install

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

## Usage

```bash
tban-cat
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

Check syntax:

```bash
python3 -m py_compile audio_player.py gif_loader.py renderer.py main.py
```
