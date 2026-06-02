from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


HEX_COLOR_PATTERN = r"^#[0-9a-fA-F]{6}$"


class SlideElement(BaseModel):
    kind: Literal["text", "shape", "image"] = "text"
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    w: float = Field(gt=0)
    h: float = Field(gt=0)
    text: str | None = None
    shape: Literal["rect", "round_rect", "ellipse", "line"] | None = None
    fill: str | None = Field(default=None, pattern=HEX_COLOR_PATTERN)
    outline: str | None = Field(default=None, pattern=HEX_COLOR_PATTERN)
    color: str = Field(default="#111827", pattern=HEX_COLOR_PATTERN)
    font_size: int = Field(default=18, ge=6, le=96)
    bold: bool = False
    italic: bool = False
    bullets: list[str] = Field(default_factory=list)
    image_path: str | None = None


class SlideSpec(BaseModel):
    title: str = "Generated Slide"
    size: Literal["wide", "standard"] = "wide"
    background: str = Field(default="#ffffff", pattern=HEX_COLOR_PATTERN)
    elements: list[SlideElement] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("elements")
    @classmethod
    def require_elements(cls, elements: list[SlideElement]) -> list[SlideElement]:
        if not elements:
            raise ValueError("SlideSpec must contain at least one element")
        return elements

