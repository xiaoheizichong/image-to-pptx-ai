from image_to_pptx_ai.colors import hex_to_rgb, readable_text_color, rgb_to_hex


def test_hex_round_trip():
    assert rgb_to_hex((17, 24, 39)) == "#111827"
    assert hex_to_rgb("#111827") == (17, 24, 39)


def test_readable_text_color():
    assert readable_text_color("#111827") == "#ffffff"
    assert readable_text_color("#ffffff") == "#111827"

