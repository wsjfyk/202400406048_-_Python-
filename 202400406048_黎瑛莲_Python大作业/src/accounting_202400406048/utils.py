"""
utils: helper utilities such as logo generation.
"""

from PIL import Image, ImageDraw, ImageFont


def make_logo_image(text, size=(64, 64), bg_color=(30, 144, 255), text_color="white"):
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    draw.rectangle([0, 0, size[0], size[1]], fill=bg_color)
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, font=font, fill=text_color)
    return img
