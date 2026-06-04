from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageSequence


@dataclass(frozen=True)
class GifFrame:
    image: Image.Image
    duration: float


def resolve_gif_path(path: str | Path = "cat.gif") -> Path:
    requested = Path(path)
    if requested.exists():
        return requested

    if requested.name == "cat.gif":
        for candidate in ("cat.gif", "cat.GIF", "CAT.GIF"):
            candidate_path = Path(candidate)
            if candidate_path.exists():
                return candidate_path

    raise FileNotFoundError(f"GIF file not found: {requested}")


def load_gif(path: str | Path) -> list[GifFrame]:
    gif_path = Path(path)
    frames: list[GifFrame] = []

    with Image.open(gif_path) as image:
        for frame in ImageSequence.Iterator(image):
            duration_ms = frame.info.get("duration", image.info.get("duration", 100))
            duration = max(float(duration_ms) / 1000.0, 0.02)
            frames.append(GifFrame(frame.convert("RGBA").copy(), duration))

    if not frames:
        raise ValueError(f"No frames found in GIF: {gif_path}")

    return frames


def crop_frames_to_content(frames: Iterable[GifFrame]) -> list[GifFrame]:
    frame_list = list(frames)
    boxes = [frame.image.getchannel("A").getbbox() for frame in frame_list]
    boxes = [box for box in boxes if box is not None]

    if not frame_list or not boxes:
        return frame_list

    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = max(box[2] for box in boxes)
    bottom = max(box[3] for box in boxes)
    source_width, source_height = frame_list[0].image.size

    if (left, top, right, bottom) == (0, 0, source_width, source_height):
        return frame_list

    return [
        GifFrame(frame.image.crop((left, top, right, bottom)), frame.duration)
        for frame in frame_list
    ]


def fit_size(
    source_size: tuple[int, int],
    terminal_size: tuple[int, int],
    reserved_rows: int = 1,
    scale_factor: float = 1.0,
) -> tuple[int, int]:
    source_width, source_height = source_size
    terminal_columns, terminal_rows = terminal_size

    available_width = max(1, terminal_columns)
    available_pixel_height = max(1, (terminal_rows - reserved_rows) * 2)

    fit_scale = min(
        available_width / max(1, source_width),
        available_pixel_height / max(1, source_height),
    )
    scale = fit_scale * max(0.1, min(1.0, float(scale_factor)))

    width = max(1, int(source_width * scale))
    height = max(1, int(source_height * scale))
    return width, height


def prepare_frames(
    frames: Iterable[GifFrame],
    size: tuple[int, int],
    background: tuple[int, int, int] | None = None,
    dither: bool = False,
    dither_levels: int = 32,
    alpha_threshold: int = 200,
    smooth: bool = False,
) -> list[GifFrame]:
    prepared: list[GifFrame] = []
    resample = Image.Resampling.LANCZOS if smooth else Image.Resampling.NEAREST

    for frame in frames:
        resized = frame.image.resize(size, resample=resample)
        if background is None:
            rgba = resized.convert("RGBA")
            rgba.putalpha(clean_alpha(rgba.getchannel("A"), alpha_threshold))

            if dither:
                alpha = rgba.getchannel("A")
                rgb = floyd_steinberg_dither(rgba.convert("RGB"), levels=dither_levels)
                rgba = rgb.convert("RGBA")
                rgba.putalpha(alpha)

            prepared.append(GifFrame(rgba, frame.duration))
        else:
            composed = Image.new("RGBA", resized.size, (*background, 255))
            composed.alpha_composite(resized)
            rgb = composed.convert("RGB")

            if dither:
                rgb = floyd_steinberg_dither(rgb, levels=dither_levels)

            prepared.append(GifFrame(rgb, frame.duration))

    return prepared


def clean_alpha(alpha: Image.Image, threshold: int) -> Image.Image:
    threshold = max(0, min(255, int(threshold)))
    return alpha.point(lambda value: 255 if value >= threshold else 0)


def floyd_steinberg_dither(image: Image.Image, levels: int = 32) -> Image.Image:
    levels = max(2, min(256, int(levels)))
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = [
        [list(rgb.getpixel((x, y))) for x in range(width)]
        for y in range(height)
    ]
    step = 255.0 / (levels - 1)

    def quantize(value: float) -> int:
        return int(round(value / step) * step)

    def add_error(x: int, y: int, error: list[float], factor: float) -> None:
        if 0 <= x < width and 0 <= y < height:
            target = pixels[y][x]
            for channel in range(3):
                target[channel] += error[channel] * factor

    for y in range(height):
        for x in range(width):
            old = pixels[y][x]
            new = [max(0, min(255, quantize(value))) for value in old]
            pixels[y][x] = new
            error = [old[channel] - new[channel] for channel in range(3)]

            add_error(x + 1, y, error, 7 / 16)
            add_error(x - 1, y + 1, error, 3 / 16)
            add_error(x, y + 1, error, 5 / 16)
            add_error(x + 1, y + 1, error, 1 / 16)

    dithered = Image.new("RGB", rgb.size)
    dithered.putdata(
        tuple(max(0, min(255, int(channel))) for channel in pixel)
        for row in pixels
        for pixel in row
    )
    return dithered
