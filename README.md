[![PSZ BANNER](https://github.com/SlabyLol/psz/blob/main/banner.png)](https://slabylol.github.io/psz)

# PSZ – Encrypted Project Archives

**PSZ** is a simple encrypted archive format designed for projects.

Every archive consists of **one encrypted file** plus **one or more paired unpackers**:

| File | Description |
|------|-------------|
| `something.psz` | The encrypted archive (AES-256-GCM) |
| `something.psz-data.lor` | **Python** unpacker (key + code) |
| `something.psz-data.php` | **PHP** unpacker (CLI + optional web form) |
| `something.psz-data.html` | **Browser** unpacker (HTML + Web Crypto) |

You always need the `.psz` **and** at least one matching unpacker to extract the content.

---

## Quick Start

### Install

```bash
pip install git+https://github.com/SlabyLol/psz.git
# or after cloning:
pip install -e .
```

### Create an archive (all languages by default)

```bash
psz make ./my-project -o my-project.psz
```

This creates:

- `my-project.psz`
- `my-project.psz-data.lor`   (Python)
- `my-project.psz-data.php`   (PHP)
- `my-project.psz-data.html`  (Browser)

### Language selection

```bash
# Only Python
psz make ./my-project -o out.psz --lang python

# PHP + HTML
psz make ./my-project -o out.psz --lang php --lang html

# Explicit all
psz make ./my-project -o out.psz --lang all
```

### Open / extract

**With the psz CLI** (works with any unpacker that embeds `KEY_HEX`):

```bash
psz open my-project.psz my-project.psz-data.lor -o extracted/
```

**Python:**

```bash
python my-project.psz-data.lor my-project.psz -o extracted/
```

**PHP** (CLI, needs OpenSSL):

```bash
php my-project.psz-data.php my-project.psz -o extracted/
```

**Browser:**

1. Open `my-project.psz-data.html` in any modern browser  
2. Select the `.psz` file  
3. Download the decrypted `.tar` and extract it locally  

---

## How it works

1. All files from the source directory are packed into a **tar** archive.
2. The tar is encrypted with **AES-256-GCM** using a fresh random key.
3. The encrypted data is written to the `.psz` file.
4. One or more self-contained unpackers are generated; each embeds the key for that archive.

Sharing only the `.psz` is useless without a matching unpacker.

---

## Docker

```bash
docker build -t psz .
docker run --rm -v $(pwd):/data psz make /data/myfolder -o /data/out.psz
```

---

## GitHub Actions

This repository includes example workflows under `.github/workflows/` that build a project, run `psz make`, and upload the `.psz` plus unpackers as artifacts.

---

## Command reference

```text
psz make <source_dir> -o <name.psz> [--lang python|php|html|all] [--lor custom.path]
psz open <name.psz> <unpacker> [-o output_dir]
psz --version
psz --help
```

---

## Security notes

- Uses AES-256-GCM (authenticated encryption).
- A new random key is generated for every archive.
- The key lives **only** inside the matching unpacker file(s).
- Do **not** publish unpackers if the content is sensitive and you only want to distribute the encrypted `.psz`.
- Path traversal protection is applied when extracting (Python / PHP).
- Browser unpacker decrypts client-side; the key is still visible in the HTML source.

---

## License

MIT – see [LICENSE](LICENSE)

---

## Repository

https://github.com/SlabyLol/psz
