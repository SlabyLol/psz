[![PSZ BANNER](https://github.com/SlabyLol/psz/blob/main/banner.png)](https://slabylol.github.io/psz)
# PSZ – Encrypted Project Archives

**PSZ** is a simple encrypted archive format designed for projects.

Every archive consists of **two files**:

| File | Description |
|------|-------------|
| `something.psz` | The encrypted archive (AES-256-GCM) |
| `something.psz-data.lor` | The matching unpacker that contains the key + code to open it |

You always need **both** files to extract the content.

---

## Quick Start

### Install

```bash
pip install git+https://github.com/SlabyLol/psz.git
# or after cloning:
pip install -e .
```

### Create an archive

```bash
psz make ./my-project -o my-project.psz
```

This creates:

- `my-project.psz`
- `my-project.psz-data.lor`

### Open / extract

```bash
psz open my-project.psz my-project.psz-data.lor -o extracted/
```

Or run the `.lor` file directly (it is a self-contained Python script):

```bash
python my-project.psz-data.lor my-project.psz -o extracted/
```

---

## How it works

1. All files from the source directory are packed into a **tar** archive.
2. The tar is encrypted with **AES-256-GCM** using a fresh random key.
3. The encrypted data is written to the `.psz` file.
4. A small Python script (`.psz-data.lor`) is generated that embeds the key and can decrypt + extract that specific archive.

The `.lor` file is intentionally paired 1:1 with its `.psz`.  
Sharing only the `.psz` is useless without the matching `.lor`.

---

## Docker

```bash
docker build -t psz .
docker run --rm -v $(pwd):/data psz make /data/myfolder -o /data/out.psz
```

---

## GitHub Actions

This repository includes an example workflow (`.github/workflows/example-build.yml`) that:

1. Builds / prepares a `dist/` folder
2. Runs `psz make dist -o release.psz`
3. Uploads both `release.psz` and `release.psz-data.lor` as artifacts

You can copy the workflow into your own projects and adapt the build steps.

---

## Command reference

```text
psz make <source_dir> -o <name.psz> [--lor custom.lor]
psz open <name.psz> <name.psz-data.lor> [-o output_dir]
psz --version
psz --help
```

---

## Security notes

- Uses AES-256-GCM (authenticated encryption).
- A new random key is generated for every archive.
- The key lives **only** inside the matching `.lor` file.
- Do **not** publish the `.lor` file if the content is sensitive and you only want to distribute the encrypted `.psz`.
- Path traversal protection is applied when extracting.

---

## License

MIT – see [LICENSE](LICENSE)

---

## Repository

https://github.com/SlabyLol/psz
