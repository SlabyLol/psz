# PSZ Examples

Always: **`name.psz`** + **`name.psz-data.lor`** (key lives in the `.lor`).

## Python package + CLI

```bash
pip install -e .
psz make sample-project -o demo.psz
psz list demo.psz demo.psz-data.lor
psz open demo.psz demo.psz-data.lor -o out/
```

### Package API

```python
from pathlib import Path
from psz import open_archive, list_archive_members, create_archive

create_archive(Path("sample-project"), Path("demo.psz"))
open_archive(Path("demo.psz"), Path("demo.psz-data.lor"), Path("out"))
```

## Extractors

| File | Mode |
|------|------|
| `extractors/psz-extractor1.py` | Direct – uses **psz package** |
| `extractors/psz-extractor2.py` | File args – **psz package** |
| `extractors/psz-extractor3.py` | list/open/`-m` – **psz package** |
| `extractors/psz-extractor1.php` | Direct load |
| `extractors/psz-extractor2.php` | Selection / upload |
| `extractors/psz-extractor3.php` | Full CLI |
| `extractors/psz-extractor1.js` | Direct |
| `extractors/psz-extractor2.js` | File args |
| `extractors/psz-extractor2.html` | Browser selection |

```bash
python3 extractors/psz-extractor1.py
php extractors/psz-extractor1.php
node extractors/psz-extractor1.js
```
