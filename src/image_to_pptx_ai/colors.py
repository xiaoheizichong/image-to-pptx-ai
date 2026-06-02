from __future__ import annotations

from collections import Counter
from pathlib import Path

from PIL import Image


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Invalid hex color: {value!r}")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def relative_luminance(hex_color: str) -> float:
    r, g, b = [channel / 255 for channel in hex_to_rgb(hex_color)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def readable_text_color(background: str) -> str:
    return "#ffffff" if relative_luminance(background) < 0.45 else "#111827"


def dominant_colors(image_path: Path, count: int = 5) -> list[str]:
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image.thumbnail((160, 160))
        pixels = list(image.getdata())

    quantized = [
        (round(r / 32) * 32, round(g / 32) * 32, round(b / 32) * 32)
        for r, g, b in pixels
    ]
    ranked = Counter(quantized).most_common(count)
    return [rgb_to_hex(tuple(min(255, channel) for channel in color)) for color, _ in ranked]

