# icon generation/readme
This folder is intended to hold small PNG icons used by the UI (icon_add, icon_edit, icon_delete, icon_chart, icon_export, icon_search).

If icons are not present, the UI will fall back to text-only buttons. You can generate a set of icons locally by running:

python -c "from accounting_202400406048.utils import make_icon_set; print(make_icon_set('icon_add', out_dir=__import__('pathlib').Path('assets/icons')) )"

Alternatively, in Python code:

from accounting_202400406048.utils import make_icon_set
from pathlib import Path
make_icon_set('icon_add', base_color=(40,160,200), out_dir=Path('assets/icons'))
