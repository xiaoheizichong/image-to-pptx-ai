# Image to PPTX AI

Image to PPTX AI is a command-line project that recreates presentation slides from an input image. It can use:

- **Local mode**: extracts image size, dominant colors, and a simple visual composition.
- **OpenAI mode**: asks a vision model to describe the image as a structured slide specification, then renders it as PowerPoint.

The output is a real `.pptx` file generated with `python-pptx`, ready for PowerPoint, Keynote, WPS, or Google Slides import.

## Features

- Generate PowerPoint slides from screenshots, posters, diagrams, or visual references.
- Preserve the source image palette as slide theme colors.
- Render titles, text blocks, bullets, simple shapes, and optional source-image previews.
- Export the intermediate JSON slide specification for editing or debugging.
- Works without an API key in local fallback mode.
- Designed as a clean GitHub project with tests, packaging, and a CLI entry point.

## Quick Start

```bash
git clone https://github.com/your-name/image-to-pptx-ai.git
cd image-to-pptx-ai
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Generate a PPTX locally:

```bash
python scripts/create_demo_image.py
image-to-pptx examples/demo.png -o output/demo.pptx --mode local
```

Generate with OpenAI vision:

```bash
set OPENAI_API_KEY=your_api_key
image-to-pptx examples/demo.png -o output/demo.pptx --mode openai
```

Save the slide specification too:

```bash
image-to-pptx examples/demo.png -o output/demo.pptx --spec output/demo.json
```

## How It Works

1. The analyzer reads the source image.
2. It creates a `SlideSpec` JSON object describing background, text, shapes, and layout.
3. The renderer converts the spec into a PowerPoint deck.

The project intentionally separates **analysis** from **rendering**, so you can replace the analyzer with another model or use your own JSON specification.

## CLI

```bash
image-to-pptx IMAGE_PATH [options]
```

Options:

```text
-o, --output PATH       Output PPTX path. Default: output.pptx
--mode MODE             local, openai, or auto. Default: auto
--model MODEL           OpenAI model name. Default: gpt-4.1-mini
--spec PATH             Save generated SlideSpec JSON to this path
--no-source-preview     Do not include the original image preview on the slide
--title TEXT            Override the generated title
```

## JSON Slide Specification

The renderer accepts a structured model internally:

```json
{
  "title": "Generated Slide",
  "size": "wide",
  "background": "#111827",
  "elements": [
    {
      "kind": "text",
      "x": 0.8,
      "y": 0.7,
      "w": 5.4,
      "h": 0.7,
      "text": "Main idea",
      "font_size": 30,
      "color": "#ffffff",
      "bold": true
    }
  ]
}
```

Coordinates are in PowerPoint inches. The default wide slide is `13.333 x 7.5`.

## Development

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Generate the demo image:

```bash
python scripts/create_demo_image.py
```

## Notes

This project does not magically recover every exact font, asset, or hidden layer from an image. It creates an editable approximation in PowerPoint. OpenAI mode is usually better for semantic layouts, while local mode is useful for fast offline prototypes.

## License

MIT
