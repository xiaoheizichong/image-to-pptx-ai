from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from PIL import Image

from image_to_pptx_ai.colors import dominant_colors, readable_text_color
from image_to_pptx_ai.models import SlideElement, SlideSpec


class ImageAnalyzer:
    def analyze(
        self,
        image_path: Path,
        *,
        title: str | None = None,
        include_source_preview: bool = True,
    ) -> SlideSpec:
        raise NotImplementedError


class LocalImageAnalyzer(ImageAnalyzer):
    def analyze(
        self,
        image_path: Path,
        *,
        title: str | None = None,
        include_source_preview: bool = True,
    ) -> SlideSpec:
        image_path = Path(image_path)
        with Image.open(image_path) as image:
            width, height = image.size

        palette = dominant_colors(image_path)
        background = palette[0] if palette else "#ffffff"
        text_color = readable_text_color(background)
        accent = palette[1] if len(palette) > 1 else "#2563eb"
        generated_title = title or image_path.stem.replace("_", " ").replace("-", " ").title()

        elements: list[SlideElement] = [
            SlideElement(
                kind="shape",
                x=0,
                y=0,
                w=13.333,
                h=7.5,
                shape="rect",
                fill=background,
                outline=background,
            ),
            SlideElement(
                kind="text",
                x=0.75,
                y=0.55,
                w=7.0,
                h=0.8,
                text=generated_title,
                font_size=34,
                color=text_color,
                bold=True,
            ),
            SlideElement(
                kind="shape",
                x=0.75,
                y=1.45,
                w=2.3,
                h=0.08,
                shape="rect",
                fill=accent,
                outline=accent,
            ),
            SlideElement(
                kind="text",
                x=0.78,
                y=5.75,
                w=7.2,
                h=0.85,
                text=f"Source image: {width} x {height}px",
                font_size=16,
                color=text_color,
            ),
        ]

        for index, color in enumerate(palette[:5]):
            elements.append(
                SlideElement(
                    kind="shape",
                    x=0.78 + index * 0.45,
                    y=6.55,
                    w=0.32,
                    h=0.32,
                    shape="ellipse",
                    fill=color,
                    outline=color,
                )
            )

        if include_source_preview:
            elements.extend(
                [
                    SlideElement(
                        kind="shape",
                        x=8.55,
                        y=0.7,
                        w=4.0,
                        h=5.9,
                        shape="round_rect",
                        fill="#ffffff",
                        outline="#e5e7eb",
                    ),
                    SlideElement(
                        kind="image",
                        x=8.8,
                        y=0.95,
                        w=3.5,
                        h=5.4,
                        image_path=str(image_path),
                    ),
                ]
            )

        return SlideSpec(
            title=generated_title,
            background=background,
            elements=elements,
            notes="Generated with local image analysis. Use OpenAI mode for semantic reconstruction.",
        )


class OpenAIImageAnalyzer(ImageAnalyzer):
    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model

    def analyze(
        self,
        image_path: Path,
        *,
        title: str | None = None,
        include_source_preview: bool = True,
    ) -> SlideSpec:
        from openai import OpenAI

        image_path = Path(image_path)
        encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        media_type = _guess_media_type(image_path)

        prompt = _build_openai_prompt(title=title, include_source_preview=include_source_preview)
        client = OpenAI()
        response = client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:{media_type};base64,{encoded}",
                        },
                    ],
                }
            ],
        )

        raw_text = response.output_text.strip()
        data = _extract_json(raw_text)
        spec = SlideSpec.model_validate(data)
        if title:
            spec.title = title
        return spec


def _build_openai_prompt(*, title: str | None, include_source_preview: bool) -> str:
    preview_rule = (
        "Include an image element using image_path='__SOURCE_IMAGE__' only if it helps the slide."
        if include_source_preview
        else "Do not include image elements."
    )
    title_rule = f"Use this title if appropriate: {title!r}." if title else "Choose a concise title."
    return f"""
You are converting an image into an editable PowerPoint slide.
Return only valid JSON matching this schema:
{{
  "title": "string",
  "size": "wide",
  "background": "#RRGGBB",
  "elements": [
    {{
      "kind": "text|shape|image",
      "x": 0.0,
      "y": 0.0,
      "w": 1.0,
      "h": 1.0,
      "text": "optional text",
      "shape": "rect|round_rect|ellipse|line",
      "fill": "#RRGGBB",
      "outline": "#RRGGBB",
      "color": "#RRGGBB",
      "font_size": 18,
      "bold": false,
      "italic": false,
      "bullets": [],
      "image_path": "__SOURCE_IMAGE__"
    }}
  ],
  "notes": "short rendering notes"
}}
Use PowerPoint inches. Wide slides are 13.333 x 7.5.
Create an editable approximation: visible hierarchy, colors, text, major blocks, and simple diagrams.
Keep all coordinates inside the slide.
{title_rule}
{preview_rule}
""".strip()


def _extract_json(raw_text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw_text, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(raw_text[start : end + 1])

    return json.loads(raw_text)


def _guess_media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"
