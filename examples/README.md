# PSZ Examples

You **always** need both files to unpack:

- `something.psz` – encrypted data
- `something.psz-data.lor` (or `.php` / `.js` / `.html`) – unpacker **with the key**

## Demo archive (folder)

| File | Role |
|------|------|
| `demo.psz` | Encrypted archive |
| `demo.psz-data.lor` | Python unpacker (**required pair**) |
| `demo.psz-data.php` | PHP |
| `demo.psz-data.js` | Node.js |
| `demo.psz-data.html` | Browser |

```bash
# list contents (needs .psz + unpacker)
psz list demo.psz demo.psz-data.lor

# extract everything
python demo.psz-data.lor demo.psz -o out/
psz open demo.psz demo.psz-data.lor -o out/

# extract only one file from inside
psz open demo.psz demo.psz-data.lor -o out/ -m hello.txt

php demo.psz-data.php demo.psz -o out/
node demo.psz-data.js demo.psz -o out/
# HTML: open demo.psz-data.html → select demo.psz
```

## Single file archive

```bash
psz make single-file.txt -o single.psz --lang python
psz open single.psz single.psz-data.lor -o out/
```

## Pack multiple paths

```bash
psz make file1.txt folder/ other.txt -o multi.psz
```
