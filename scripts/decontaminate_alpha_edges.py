#!/usr/bin/env python3
"""Create a non-generative, non-trimming alpha-edge derivative.

This script preserves every alpha value from an upstream segmentation result.
It only unmixed known background colour from partially transparent edge pixels,
so it cannot be used to erode, crop, redraw, or otherwise reshape a subject.
"""

import argparse
from pathlib import Path

from PIL import Image


def parse_rgb(value):
    channels = [int(channel) for channel in value.split(",")]
    if len(channels) != 3 or any(channel < 0 or channel > 255 for channel in channels):
        raise argparse.ArgumentTypeError("background rgb must be three values in 0–255")
    return tuple(channels)


def decontaminate(source_path, alpha_path, output_path, background):
    source = Image.open(source_path).convert("RGB")
    matte = Image.open(alpha_path).convert("RGBA")
    if source.size != matte.size:
        raise ValueError("source image and alpha matte must have identical dimensions")
    source_pixels = source.load()
    alpha_pixels = matte.load()
    for y in range(matte.height):
        for x in range(matte.width):
            alpha = alpha_pixels[x, y][3]
            if 0 < alpha < 255:
                opacity = alpha / 255
                rgb = source_pixels[x, y]
                cleaned = tuple(max(0, min(255, round((rgb[channel] - (1 - opacity) * background[channel]) / opacity))) for channel in range(3))
                alpha_pixels[x, y] = (*cleaned, alpha)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matte.save(output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--alpha", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--background-rgb", type=parse_rgb, required=True)
    args = parser.parse_args()
    decontaminate(args.source, args.alpha, args.output, args.background_rgb)


if __name__ == "__main__":
    main()
