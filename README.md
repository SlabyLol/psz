# PSZ – Encrypted Project Archives

AES-256-GCM encrypted archives with **paired multi-language unpackers**.

**You always need both:** the `.psz` **and** a matching **`.lor`** unpacker (key inside).

All languages use the **`.lor`** extension:
- Python: `name.psz-data.lor`
- PHP: `name.psz-data.php.lor`
- JS: `name.psz-data.js.lor`
- HTML: `name.psz-data.html.lor`

## Install

```bash
pip install -e .
# needs: pip install cryptography
```

## Commands

```bash
# Pack folder / single file / multiple paths
psz make ./project -o release.psz
psz make readme.txt -o doc.psz
psz make a.txt b.txt src/ -o bundle.psz --lang all

# List (needs .psz + .lor)
psz list release.psz release.psz-data.lor

# Load / extract (the .lor loads the .psz)
python release.psz-data.lor release.psz -o out/
php release.psz-data.php.lor release.psz -o out/
node release.psz-data.js.lor release.psz -o out/
psz open release.psz release.psz-data.lor -o out/

# Extract only specific members
psz open release.psz release.psz-data.lor -o out/ -m path/inside.txt
```

See [examples/](examples/) for runnable demos that **load** `demo.psz`.

## License

MIT
