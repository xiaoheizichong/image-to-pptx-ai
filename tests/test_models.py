import pytest

from image_to_pptx_ai.models import SlideElement, SlideSpec


def test_slide_spec_requires_elements():
    with pytest.raises(ValueError):
        SlideSpec(elements=[])


def test_text_element_defaults():
    element = SlideElement(kind="text", x=1, y=1, w=2, h=1, text="Hello")

    assert element.font_size == 18
    assert element.color == "#111827"


def test_invalid_color_is_rejected():
    with pytest.raises(ValueError):
        SlideElement(kind="text", x=0, y=0, w=1, h=1, color="black")

