"""
utils: helper utilities such as logo and icon generation, and helpers to load icons at runtime.
"""

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def _find_assets_dir() -> Path:
    """Return project-level assets/icons directory when running from source tree.

    Location resolution (when package is in src/... structure):
    src/accounting_202400406048/utils.py -> parents[2] points to the project subdirectory
    so assets are expected at <project_subdir>/assets/icons
    """
    this = Path(__file__).resolve()
    # parents: 0=utils.py,1=accounting_202400406048,2=src,3=<project dir>
    # But depending on where package is, try several candidates
    candidates = [
        this.parents[2] / "assets" / "icons",
        this.parents[3] / "assets" / "icons",
        this.parents[1] / "assets" / "icons",
    ]
    for p in candidates:
        if p.exists():
            return p
    # default to first candidate (may be created later)
    return candidates[0]


def _choose_font(size: int = 18) -> ImageFont.ImageFont:
    """Try some common fonts for better CJK/Text support and fall back to default."""
    # list of font names / files to try (order matters)
    prefs = [
        "arial.ttf",
        "NotoSansCJK-Regular.ttc",
        "NotoSansCJK-Regular.otf",
        "SourceHanSansSC-Regular.otf",
        "SourceHanSansSC-Regular.ttf",
    ]
    for name in prefs:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_logo_image(text: str, size: Tuple[int, int] = (64, 64), bg_color=(30, 144, 255), text_color="white") -> Image.Image:
    """Create a simple square logo image with centered text.

    Returns a PIL.Image. This function does not depend on tkinter and is safe to use in tests.
    """
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = _choose_font(size=min(max(12, int(size[1] * 0.28)), 40))
    except Exception:
        font = ImageFont.load_default()
    draw.rectangle([0, 0, size[0], size[1]], fill=bg_color)
    # textsize deprecated in some pillow versions; use textbbox when available
    try:
        box = draw.textbbox((0, 0), text, font=font)
        w = box[2] - box[0]
        h = box[3] - box[1]
    except Exception:
        w, h = draw.textsize(text, font=font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, font=font, fill=text_color)
    return img


def save_image_png(img: Image.Image, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")


def make_icon_set(text: str, base_color=(30, 144, 255), out_dir: Path = None):
    """Generate a set of PNG icons in multiple sizes.

    Sizes generated: 16, 24, 32, 48, 64
    The function returns list of generated file paths.
    """
    sizes = [16, 24, 32, 48, 64]
    if out_dir is None:
        out_dir = _find_assets_dir()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for s in sizes:
        img = make_logo_image(text, size=(s, s), bg_color=base_color)
        p = out_dir / f"{text}_{s}.png"
        save_image_png(img, p)
        files.append(p)
    return files


def load_icon_image(name: str, prefer_size: int = 24):
    """Try to locate an icon PNG under assets/icons and return the file path (Path) if found, else None.

    The UI layer can use ImageTk.PhotoImage on the returned path.
    """
    assets = _find_assets_dir()
    if not assets.exists():
        return None
    # look for exact name.png or name_<size>.png with nearest size
    cand = assets / f"{name}.png"
    if cand.exists():
        return cand
    # find name_size variants
    variants = list(assets.glob(f"{name}_*.png"))
    if not variants:
        # try icon prefixes
        variants = list(assets.glob(f"*{name}*.png"))
    if not variants:
        return None
    # pick closest size to prefer_size if possible
    def size_of(p: Path):
        stem = p.stem
        parts = stem.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0

    variants.sort(key=lambda p: abs(size_of(p) - prefer_size))
    return variants[0]


# keep backward-compatible name
__all__ = ["make_logo_image", "make_icon_set", "load_icon_image", "save_image_png"]
