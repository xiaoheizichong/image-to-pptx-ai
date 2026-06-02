from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    output = Path("examples/demo.png")
    output.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (1280, 720), "#0f172a")
    draw = ImageDraw.Draw(image)

    draw.rectangle((80, 80, 1180, 620), outline="#334155", width=3)
    draw.rectangle((80, 80, 1180, 180), fill="#1e293b")
    draw.rectangle((110, 230, 560, 520), fill="#2563eb")
    draw.rectangle((610, 230, 1130, 300), fill="#14b8a6")
    draw.rectangle((610, 335, 980, 395), fill="#f97316")
    draw.rectangle((610, 430, 1060, 490), fill="#a855f7")

    try:
        title_font = ImageFont.truetype("arial.ttf", 54)
        body_font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    draw.text((120, 105), "Image to PPTX AI", fill="#ffffff", font=title_font)
    draw.text((140, 330), "Visual reference", fill="#ffffff", font=body_font)
    draw.text((635, 248), "Detect layout", fill="#ffffff", font=body_font)
    draw.text((635, 348), "Extract colors", fill="#111827", font=body_font)
    draw.text((635, 445), "Render editable PPT", fill="#ffffff", font=body_font)

    image.save(output)
    print(f"Created {output}")


if __name__ == "__main__":
    main()

