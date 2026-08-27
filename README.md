# PSZ – Encrypted Project Archives

AES-256-GCM archives with a paired **`.psz-data.lor`** key file.

Always need **both**:
- `name.psz` – encrypted data
- `name.psz-data.lor` – unpacker / key (same filename for every language)

## Python package + CLI

```bash
pip install -e .
# requires: cryptography
```

### CLI

```bash
psz make ./project -o release.psz
psz make ./project -o release.psz --lang php
psz make file.txt -o one.psz

psz list release.psz release.psz-data.lor
psz open release.psz release.psz-data.lor -o out/
psz open release.psz release.psz-data.lor -o out/ -m path/inside.txt
```

### Package API

```python
from pathlib import Path
from psz import create_archive, open_archive, list_archive_members

create_archive(Path("project"), Path("release.psz"))
list_archive_members(Path("release.psz"), Path("release.psz-data.lor"))
open_archive(Path("release.psz"), Path("release.psz-data.lor"), Path("out"))
```

## Languages for `.psz-data.lor` content

```bash
psz make ./project -o r.psz --lang python   # default
psz make ./project -o r.psz --lang php
psz make ./project -o r.psz --lang js
psz make ./project -o r.psz --lang html
```

Name is always **`r.psz-data.lor`**.

## Examples

See [examples/](examples/).

```bash
python3 examples/extractors/psz-extractor1.py
php examples/extractors/psz-extractor1.php
node examples/extractors/psz-extractor1.js
```

## License

MIT
