from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from rich.console import Console

from image_to_pptx_ai.analyzer import LocalImageAnalyzer, OpenAIImageAnalyzer
from image_to_pptx_ai.models import SlideSpec
from image_to_pptx_ai.renderer import render_pptx


console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="image-to-pptx",
        description="Generate an editable PowerPoint deck from an input image.",
    )
    parser.add_argument("image", type=Path, help="Path to the source image")
    parser.add_argument("-o", "--output", type=Path, default=Path("output.pptx"))
    parser.add_argument("--mode", choices=["auto", "local", "openai"], default="auto")
    parser.add_argument("--model", default="gpt-4.1-mini", help="OpenAI vision-capable model")
    parser.add_argument("--spec", type=Path, help="Write generated SlideSpec JSON")
    parser.add_argument("--title", help="Override generated slide title")
    parser.add_argument(
        "--no-source-preview",
        action="store_true",
        help="Do not place the original image preview on the generated slide",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    image_path: Path = args.image

    if not image_path.exists():
        console.print(f"[red]Image not found:[/red] {image_path}")
        return 2

    mode = _resolve_mode(args.mode)
    analyzer = OpenAIImageAnalyzer(args.model) if mode == "openai" else LocalImageAnalyzer()

    console.print(f"Analyzing image with [bold]{mode}[/bold] mode...")
    spec = analyzer.analyze(
        image_path,
        title=args.title,
        include_source_preview=not args.no_source_preview,
    )
    spec = _replace_source_image_token(spec, image_path)

    if args.spec:
        args.spec.parent.mkdir(parents=True, exist_ok=True)
        args.spec.write_text(
            json.dumps(spec.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        console.print(f"Saved spec: [green]{args.spec}[/green]")

    output_path = render_pptx(spec, args.output, source_image=image_path)
    console.print(f"Saved PowerPoint: [green]{output_path}[/green]")
    return 0


def _resolve_mode(mode: str) -> str:
    if mode == "auto":
        return "openai" if os.getenv("OPENAI_API_KEY") else "local"
    return mode


def _replace_source_image_token(spec: SlideSpec, image_path: Path) -> SlideSpec:
    for element in spec.elements:
        if element.image_path == "__SOURCE_IMAGE__":
            element.image_path = str(image_path)
    return spec


if __name__ == "__main__":
    raise SystemExit(main())

