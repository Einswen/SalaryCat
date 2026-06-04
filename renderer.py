from __future__ import annotations

import os
import shutil
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import TextIO

from PIL import Image


RESET = "\x1b[0m"
DEFAULT_FG = "\x1b[39m"
DEFAULT_BG = "\x1b[49m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
ALT_SCREEN = "\x1b[?1049h"
MAIN_SCREEN = "\x1b[?1049l"
HOME = "\x1b[H"
CLEAR_SCREEN = "\x1b[2J"


@dataclass
class ColorCache:
    foreground: dict[tuple[int, int, int], str] = field(default_factory=dict)
    background: dict[tuple[int, int, int], str] = field(default_factory=dict)

    def fg(self, color: tuple[int, int, int]) -> str:
        cached = self.foreground.get(color)
        if cached is None:
            cached = f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m"
            self.foreground[color] = cached
        return cached

    def bg(self, color: tuple[int, int, int]) -> str:
        cached = self.background.get(color)
        if cached is None:
            cached = f"\x1b[48;2;{color[0]};{color[1]};{color[2]}m"
            self.background[color] = cached
        return cached


class TerminalRenderer:
    def __init__(
        self,
        stream: TextIO | None = None,
        background: tuple[int, int, int] | None = None,
        block_mode: str = "solid",
    ) -> None:
        self.stream = stream or sys.stdout
        self.background = background
        self.block_mode = block_mode
        self.colors = ColorCache()
        self.previous_buffer: list[str] = []

    def enter(self) -> None:
        enable_virtual_terminal_on_windows()
        self.stream.write(ALT_SCREEN + HIDE_CURSOR + RESET + DEFAULT_FG + DEFAULT_BG + CLEAR_SCREEN + HOME)
        self.stream.flush()

    def exit(self) -> None:
        self.stream.write(RESET + SHOW_CURSOR + MAIN_SCREEN)
        self.stream.flush()

    def clear(self) -> None:
        self.stream.write(RESET + DEFAULT_FG + DEFAULT_BG + CLEAR_SCREEN + HOME)
        self.stream.flush()

    def terminal_size(self) -> tuple[int, int]:
        size = shutil.get_terminal_size(fallback=(80, 24))
        return max(1, size.columns), max(2, size.lines)

    def reset_buffer(self) -> None:
        self.previous_buffer = []

    def render_image_lines(self, image: Image.Image) -> list[str]:
        if self.block_mode == "half":
            return self._render_half_block_lines(image)
        return self._render_solid_block_lines(image)

    def _render_half_block_lines(self, image: Image.Image) -> list[str]:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        pixels = rgba.load()
        lines: list[str] = []

        for y in range(0, height, 2):
            parts: list[str] = []
            last_fg: tuple[int, int, int] | None = None
            last_bg: tuple[int, int, int] | None = None

            for x in range(width):
                top = pixels[x, y]
                bottom = pixels[x, y + 1] if y + 1 < height else (0, 0, 0, 0)
                top_visible = top[3] >= 128
                bottom_visible = bottom[3] >= 128

                if top_visible and bottom_visible:
                    fg = top[:3]
                    bg = bottom[:3]
                    char = "▀"
                elif top_visible:
                    fg = top[:3]
                    bg = None
                    char = "▀"
                elif bottom_visible:
                    fg = bottom[:3]
                    bg = None
                    char = "▄"
                else:
                    fg = None
                    bg = None
                    char = " "

                if fg != last_fg:
                    parts.append(self.colors.fg(fg) if fg is not None else DEFAULT_FG)
                    last_fg = fg
                if bg != last_bg:
                    parts.append(self.colors.bg(bg) if bg is not None else DEFAULT_BG)
                    last_bg = bg

                parts.append(char)

            parts.append(RESET)
            lines.append("".join(parts))

        return lines

    def _render_solid_block_lines(self, image: Image.Image) -> list[str]:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        pixels = rgba.load()
        lines: list[str] = []

        for y in range(0, height, 2):
            parts: list[str] = []
            last_fg: tuple[int, int, int] | None = None

            for x in range(width):
                top = pixels[x, y]
                bottom = pixels[x, y + 1] if y + 1 < height else (0, 0, 0, 0)
                top_visible = top[3] >= 128
                bottom_visible = bottom[3] >= 128

                if top_visible and bottom_visible:
                    fg = top[:3]
                    char = "█"
                elif top_visible:
                    fg = top[:3]
                    char = "█"
                elif bottom_visible:
                    fg = bottom[:3]
                    char = "█"
                else:
                    fg = None
                    char = " "

                if fg != last_fg:
                    parts.append(self.colors.fg(fg) if fg is not None else DEFAULT_FG)
                    parts.append(DEFAULT_BG)
                    last_fg = fg

                parts.append(char)

            parts.append(RESET)
            lines.append("".join(parts))

        return lines

    def compose_screen(
        self,
        image_lines: list[str],
        image_width: int,
        message: str,
        show_fps: bool = False,
        fps: float = 0.0,
        vertical_margin: int = 6,
    ) -> list[str]:
        columns, rows = self.terminal_size()
        animation_rows = max(1, rows - 1)
        background = self.colors.bg(self.background) if self.background is not None else ""
        blank = background + (" " * columns) + RESET
        screen = [blank for _ in range(animation_rows)]

        effective_margin = min(max(0, vertical_margin), max(0, (animation_rows - 1) // 2))
        image_area_rows = max(1, animation_rows - (effective_margin * 2))
        image_rows = min(len(image_lines), image_area_rows)
        top_padding = effective_margin + max(0, (image_area_rows - image_rows) // 2)
        left_padding = max(0, (columns - image_width) // 2)
        right_padding = max(0, columns - left_padding - image_width)

        for index in range(image_rows):
            screen[top_padding + index] = (
                background
                + (" " * left_padding)
                + image_lines[index]
                + background
                + (" " * right_padding)
                + RESET
            )

        screen.append(self._footer_line(message, columns, show_fps, fps))
        return screen

    def draw(self, buffer: list[str], full_redraw: bool = False) -> None:
        updates: list[str] = []
        force = full_redraw or len(self.previous_buffer) != len(buffer)

        for row, line in enumerate(buffer, start=1):
            if force or self.previous_buffer[row - 1] != line:
                updates.append(f"\x1b[{row};1H{line}")

        if updates:
            self.stream.write("".join(updates))
            self.stream.flush()
            self.previous_buffer = buffer

    def _footer_line(
        self,
        message: str,
        columns: int,
        show_fps: bool,
        fps: float,
    ) -> str:
        message = fit_text(message, columns)
        message_width = display_width(message)
        fps_text = f"{fps:5.1f} FPS" if show_fps else ""
        fps_width = display_width(fps_text)
        footer_style = self.colors.fg((32, 32, 32))
        if self.background is not None:
            footer_style = self.colors.bg(self.background) + footer_style

        if fps_text and message_width + fps_width + 2 <= columns:
            left = max(0, (columns - message_width) // 2)
            middle = max(1, columns - left - message_width - fps_width)
            return (
                footer_style
                + (" " * left)
                + message
                + (" " * middle)
                + fps_text
                + RESET
            )

        left = max(0, (columns - message_width) // 2)
        right = max(0, columns - left - message_width)
        return footer_style + (" " * left) + message + (" " * right) + RESET


def display_width(text: str) -> int:
    width = 0
    for char in text:
        if unicodedata.combining(char):
            continue
        if unicodedata.east_asian_width(char) in {"F", "W"}:
            width += 2
        else:
            width += 1
    return width


def fit_text(text: str, max_width: int) -> str:
    if display_width(text) <= max_width:
        return text

    result: list[str] = []
    width = 0
    for char in text:
        char_width = 0 if unicodedata.combining(char) else (
            2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1
        )
        if width + char_width > max_width:
            break
        result.append(char)
        width += char_width
    return "".join(result)


def enable_virtual_terminal_on_windows() -> None:
    if os.name != "nt":
        return

    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_uint32()

    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
