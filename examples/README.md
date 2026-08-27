# PSZ Examples – Load / execute a `.psz`

A `.psz` is **encrypted**. To open it you always need:

1. the **`.psz`** file (data)
2. a matching **`.lor`** unpacker (contains the key)

All unpackers end with **`.lor`**:

| File | Loads `.psz` with |
|------|-------------------|
| `demo.psz-data.lor` | **Python** |
| `demo.psz-data.php.lor` | **PHP** |
| `demo.psz-data.js.lor` | **Node.js** |
| `demo.psz-data.html.lor` | **Browser** |

---

## 1. Python – load `.psz`

```bash
cd examples
python3 demo.psz-data.lor demo.psz -o out-python/
```

```bash
psz open demo.psz demo.psz-data.lor -o out-python/
psz list demo.psz demo.psz-data.lor
```

## 2. PHP – load `.psz`

```bash
php demo.psz-data.php.lor demo.psz -o out-php/
```

## 3. JavaScript (Node) – load `.psz`

```bash
node demo.psz-data.js.lor demo.psz -o out-js/
```

## 4. HTML – load `.psz` in the browser

1. Open `demo.psz-data.html.lor` in the browser
2. Select **`demo.psz`**
3. Download the decrypted `.tar`

---

## Quick scripts (load demo.psz)

```bash
bash scripts/run-python.sh
bash scripts/run-php.sh
bash scripts/run-js.sh
bash scripts/run-all.sh
```
