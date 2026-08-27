"""Unpacker generator."""
from pathlib import Path

def _generate_html_lor(key_hex: str, archive_name: str) -> str:
    """Generate a self-contained HTML+JS browser unpacker."""
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>PSZ Unpacker - {archive_name}</title>
<style>
body{{margin:0;min-height:100vh;font-family:system-ui,sans-serif;background:#0f1115;color:#e8eaed;display:flex;align-items:center;justify-content:center;padding:1.5rem}}
.card{{background:#1a1d24;border-radius:12px;padding:1.75rem 2rem;max-width:32rem;width:100%}}
h1{{margin:0 0 .25rem;font-size:1.35rem}}
.sub{{color:#9aa0a6;font-size:.9rem;margin-bottom:1.25rem}}
input[type=file]{{width:100%;padding:.6rem;margin-bottom:1rem;background:#12141a;border:1px solid #2a2f3a;border-radius:8px;color:#e8eaed}}
button{{width:100%;padding:.75rem;border:none;border-radius:8px;background:#7c9cff;color:#0a0c10;font-weight:600;cursor:pointer}}
#log{{margin-top:1rem;font-family:monospace;font-size:.8rem;color:#9aa0a6}}
#log.ok{{color:#3dd68c}}#log.err{{color:#ff6b6b}}
a.download{{display:inline-block;margin-top:.75rem;color:#7c9cff}}
</style>
</head>
<body>
<div class=\"card\">
<h1>PSZ Browser Unpacker</h1>
<p class=\"sub\">Paired with <strong>{archive_name}</strong> · AES-256-GCM</p>
<input type=\"file\" id=\"file\" accept=\".psz,application/octet-stream\">
<button id=\"btn\" type=\"button\">Decrypt &amp; download tar</button>
<div id=\"log\"></div>
<a id=\"dl\" class=\"download\" style=\"display:none\" download=\"extracted.tar\">Download extracted.tar</a>
</div>
<script>
const KEY_HEX = \"{key_hex}\";
const MAGIC = [0x50,0x53,0x5a,0x31];
const NONCE_SIZE = 12;
const logEl = document.getElementById(\"log\");
const btn = document.getElementById(\"btn\");
const dl = document.getElementById(\"dl\");
function log(msg, cls) {{ logEl.textContent = msg; logEl.className = cls || \"\"; }}
function hexToBytes(hex) {{
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.substr(i * 2, 2), 16);
  return out;
}}
async function decryptPsz(buf) {{
  const data = new Uint8Array(buf);
  for (let i = 0; i < 4; i++) if (data[i] !== MAGIC[i]) throw new Error(\"Not a valid PSZ archive\");
  if (data[4] !== 1) throw new Error(\"Unsupported version\");
  const nonce = data.slice(5, 5 + NONCE_SIZE);
  const ct = data.slice(5 + NONCE_SIZE);
  const key = await crypto.subtle.importKey(\"raw\", hexToBytes(KEY_HEX), {{ name: \"AES-GCM\" }}, false, [\"decrypt\"]);
  const plain = await crypto.subtle.decrypt({{ name: \"AES-GCM\", iv: nonce, tagLength: 128 }}, key, ct);
  return new Uint8Array(plain);
}}
btn.addEventListener(\"click\", async () => {{
  const input = document.getElementById(\"file\");
  if (!input.files || !input.files[0]) {{ log(\"Select a .psz file first.\", \"err\"); return; }}
  btn.disabled = true; dl.style.display = \"none\"; log(\"Decrypting...\");
  try {{
    const plain = await decryptPsz(await input.files[0].arrayBuffer());
    const url = URL.createObjectURL(new Blob([plain], {{ type: \"application/x-tar\" }}));
    dl.href = url;
    dl.download = (input.files[0].name.replace(/\\.psz$/i, \"\") || \"extracted\") + \".tar\";
    dl.style.display = \"inline-block\";
    log(\"OK - \" + plain.length + \" bytes. Download the .tar.\", \"ok\");
  }} catch (e) {{
    log(\"Error: \" + (e && e.message ? e.message : String(e)), \"err\");
  }} finally {{ btn.disabled = false; }}
}});
</script>
</body>
</html>
"""
