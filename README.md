# PSZ – Encrypted Project Archives

AES-256-GCM encrypted archives with **paired multi-language unpackers**.

**You always need both:** the `.psz` **and** a matching unpacker (`.lor` / `.php` / `.js` / `.html`) that holds the key.

## Install

```bash
pip install -e .
# needs: pip install cryptography
```

## Commands

```bash
# Pack a folder, a single file, or several paths
psz make ./project -o release.psz
psz make readme.txt -o doc.psz
psz make a.txt b.txt src/ -o bundle.psz --lang all

# Languages: --lang python|php|js|html|all  (default: all)

# List (needs unpacker)
psz list release.psz release.psz-data.lor

# Extract all
psz open release.psz release.psz-data.lor -o out/
python release.psz-data.lor release.psz -o out/
php release.psz-data.php release.psz -o out/
node release.psz-data.js release.psz -o out/

# Extract only specific members
psz open release.psz release.psz-data.lor -o out/ -m path/inside.txt
```

See [examples/](examples/) for a full demo.

## License

MIT
