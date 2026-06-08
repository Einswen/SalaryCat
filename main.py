from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from audio_player import AudioPlayer
from gif_loader import (
    GifFrame,
    crop_frames_to_content,
    fit_size,
    load_gif,
    prepare_frames,
    resolve_gif_path,
)
from renderer import TerminalRenderer


LOVE_MESSAGE = "我真的特别爱你"
BACKGROUND = None
VERTICAL_MARGIN_ROWS = 1
DEFAULT_SCALE = 0.85


@dataclass(frozen=True)
class RenderedFrame:
    lines: list[str]
    duration: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render cat.gif as smooth ANSI TrueColor half-block terminal animation."
    )
    parser.add_argument(
        "--gif",
        default="cat.gif",
        help="GIF path. Defaults to ./cat.gif and also accepts ./cat.GIF.",
    )
    parser.add_argument(
        "--fps",
        action="store_true",
        help="Show live FPS on the bottom line.",
    )
    parser.add_argument(
        "--dither",
        action="store_true",
        help="Enable Floyd-Steinberg dithering after scaling. Smoother playback usually means leaving this off.",
    )
    parser.add_argument(
        "--dither-levels",
        type=int,
        default=32,
        help="Color levels per channel for dithering, from 2 to 256. Default: 32.",
    )
    parser.add_argument(
        "--margin-rows",
        type=int,
        default=VERTICAL_MARGIN_ROWS,
        help="Blank terminal rows above and below the animation. Default: 1.",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=DEFAULT_SCALE,
        help="Animation scale from 0.1 to 1.0. Smaller values make block pixels feel finer. Default: 0.85.",
    )
    parser.add_argument(
        "--no-trim",
        action="store_true",
        help="Keep transparent GIF padding instead of cropping it before scaling.",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=200,
        help="Transparent pixel cutoff from 0 to 255. Higher removes more edge ghosts. Default: 200.",
    )
    parser.add_argument(
        "--half-block",
        action="store_true",
        help="Use higher-resolution half-block rendering. May show horizontal stripes in some terminals.",
    )
    parser.add_argument(
        "--smooth",
        action="store_true",
        help="Use antialiased scaling. Default is sharp nearest-neighbor pixel-art scaling.",
    )
    parser.add_argument(
        "--music",
        default="music.mp3",
        help="MP3 file to play when the animation starts. Default: ./music.mp3.",
    )
    parser.add_argument(
        "--no-music",
        action="store_true",
        help="Disable music playback.",
    )
    return parser.parse_args()


def prerender_for_terminal(
    frames: list[GifFrame],
    renderer: TerminalRenderer,
    terminal_size: tuple[int, int],
    dither: bool,
    dither_levels: int,
    margin_rows: int,
    alpha_threshold: int,
    smooth: bool,
    scale: float,
) -> tuple[list[RenderedFrame], int]:
    reserved_rows = 1 + (max(0, margin_rows) * 2)
    target_size = fit_size(
        frames[0].image.size,
        terminal_size,
        reserved_rows=reserved_rows,
        scale_factor=scale,
    )
    prepared = prepare_frames(
        frames,
        target_size,
        background=renderer.background,
        dither=dither,
        dither_levels=dither_levels,
        alpha_threshold=alpha_threshold,
        smooth=smooth,
    )
    rendered = [
        RenderedFrame(renderer.render_image_lines(frame.image), frame.duration)
        for frame in prepared
    ]
    return rendered, target_size[0]


def sleep_until(target_time: float) -> None:
    while True:
        remaining = target_time - time.perf_counter()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 0.02))


def bundled_asset_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def resolve_optional_asset(path: str | Path, extra_dirs: tuple[Path, ...]) -> Path:
    requested = Path(path)
    if requested.exists():
        return requested

    for directory in (Path.cwd(), *extra_dirs):
        candidate = directory / requested.name
        if candidate.exists():
            return candidate

    return requested


def run() -> int:
    args = parse_args()
    asset_dir = bundled_asset_dir()
    gif_path = resolve_gif_path(Path(args.gif), extra_dirs=(asset_dir,))
    frames = load_gif(gif_path)
    if not args.no_trim:
        frames = crop_frames_to_content(frames)
    renderer = TerminalRenderer(
        background=BACKGROUND,
        block_mode="half" if args.half_block else "solid",
    )

    rendered_frames: list[RenderedFrame] = []
    image_width = 0
    cached_terminal_size: tuple[int, int] | None = None
    frame_index = 0
    next_frame_at = time.perf_counter()
    timestamps: deque[float] = deque(maxlen=120)
    music_path = resolve_optional_asset(args.music, extra_dirs=(asset_dir,))
    audio = None if args.no_music else AudioPlayer(music_path)

    try:
        if audio is not None:
            audio.start()
        renderer.enter()

        while True:
            terminal_size = renderer.terminal_size()
            if terminal_size != cached_terminal_size:
                cached_terminal_size = terminal_size
                renderer.clear()
                rendered_frames, image_width = prerender_for_terminal(
                    frames,
                    renderer,
                    terminal_size,
                    dither=args.dither,
                    dither_levels=args.dither_levels,
                    margin_rows=args.margin_rows,
                    alpha_threshold=args.alpha_threshold,
                    smooth=args.smooth,
                    scale=args.scale,
                )
                renderer.reset_buffer()
                frame_index %= len(rendered_frames)
                next_frame_at = time.perf_counter()

            now = time.perf_counter()
            timestamps.append(now)
            while timestamps and now - timestamps[0] > 1.0:
                timestamps.popleft()
            fps = len(timestamps) / max(0.001, now - timestamps[0]) if len(timestamps) > 1 else 0.0

            frame = rendered_frames[frame_index]
            screen = renderer.compose_screen(
                frame.lines,
                image_width,
                LOVE_MESSAGE,
                show_fps=args.fps,
                fps=fps,
                vertical_margin=args.margin_rows,
            )
            renderer.draw(screen, full_redraw=True)

            frame_index = (frame_index + 1) % len(rendered_frames)
            next_frame_at += frame.duration

            if next_frame_at < time.perf_counter() - 0.1:
                next_frame_at = time.perf_counter()
            sleep_until(next_frame_at)

    except KeyboardInterrupt:
        return 0
    finally:
        if audio is not None:
            audio.stop()
        renderer.exit()


if __name__ == "__main__":
    sys.exit(run())
