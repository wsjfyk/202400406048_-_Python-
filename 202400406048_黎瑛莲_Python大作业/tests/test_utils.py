import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from accounting_202400406048.utils import make_logo_image, make_icon_set


def test_make_logo_and_icons(tmp_path):
    img = make_logo_image("记账", size=(64,64))
    out = tmp_path / "logo.png"
    img.save(out)
    assert out.exists() and out.stat().st_size > 0

    icons_dir = tmp_path / "icons"
    files = make_icon_set('test_icon', out_dir=icons_dir)
    assert files
    for f in files:
        assert f.exists()
