<?php
/** PSZ Extractor 2 – file selection (CLI + web upload) */
declare(strict_types=1);

function psz_find_key(string $lorPath): string {
    $text = file_get_contents($lorPath);
    if ($text === false) throw new RuntimeException("Cannot read: $lorPath");
    foreach (['/KEY_HEX\s*=\s*["\']([0-9a-fA-F]{64})["\']/', '/define\(\s*[\'"]KEY_HEX[\'"]\s*,\s*[\'"]([0-9a-fA-F]{64})[\'"]/'] as $re) {
        if (preg_match($re, $text, $m)) return $m[1];
    }
    throw new RuntimeException('KEY_HEX not found in .psz-data.lor');
}
function psz_decrypt(string $pszPath, string $keyHex): string {
    $data = file_get_contents($pszPath);
    if ($data === false || substr($data, 0, 4) !== 'PSZ1') throw new RuntimeException('Not a valid PSZ archive');
    $nonce = substr($data, 5, 12); $ct = substr($data, 17);
    $plain = openssl_decrypt(substr($ct, 0, -16), 'aes-256-gcm', hex2bin($keyHex), OPENSSL_RAW_DATA, $nonce, substr($ct, -16));
    if ($plain === false) throw new RuntimeException('Decryption failed');
    return $plain;
}
function psz_extract_tar(string $data, string $dest, ?array $only = null): array {
    if (!is_dir($dest)) mkdir($dest, 0755, true);
    $extracted = []; $wanted = $only ? array_flip($only) : null; $offset = 0; $len = strlen($data);
    while ($offset + 512 <= $len) {
        $header = substr($data, $offset, 512); $offset += 512;
        if (trim($header) === '') break;
        $name = rtrim(substr($header, 0, 100), "\0");
        $size = octdec(rtrim(substr($header, 124, 12), "\0 ") ?: '0');
        $type = $header[156] ?? '0';
        $skip = ($name === '' || strpos($name, '..') !== false || ($name[0] ?? '') === '/');
        $match = $wanted === null || isset($wanted[$name]);
        if (!$skip && $match) {
            $target = $dest . DIRECTORY_SEPARATOR . str_replace(['/', '\\'], DIRECTORY_SEPARATOR, $name);
            if ($type === '5' || substr($name, -1) === '/') { if (!is_dir($target)) mkdir($target, 0755, true); }
            else { $dir = dirname($target); if (!is_dir($dir)) mkdir($dir, 0755, true); file_put_contents($target, substr($data, $offset, $size)); }
            $extracted[] = $name;
        }
        $offset += (int) ceil($size / 512) * 512;
    }
    return $extracted;
}

if (PHP_SAPI === 'cli') {
    $psz = $argv[1] ?? null; $lor = $argv[2] ?? null; $out = 'extracted';
    for ($i = 1; $i < $argc; $i++) if (($argv[$i] === '-o' || $argv[$i] === '--output') && isset($argv[$i+1])) $out = $argv[++$i];
    if (!$psz || !$lor) { fwrite(STDERR, "Usage: php psz-extractor2.php <a.psz> <a.psz-data.lor> [-o out]\n"); exit(1); }
    try { $files = psz_extract_tar(psz_decrypt($psz, psz_find_key($lor)), $out); echo "OK → $out (" . count($files) . " items)\n"; foreach ($files as $f) echo "  $f\n"; exit(0); }
    catch (Throwable $e) { fwrite(STDERR, "Error: {$e->getMessage()}\n"); exit(1); }
}
$msg = ''; $ok = null; $files = [];
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['psz'], $_FILES['lor'])) {
    try {
        if ($_FILES['psz']['error'] !== UPLOAD_ERR_OK || $_FILES['lor']['error'] !== UPLOAD_ERR_OK) throw new RuntimeException('Upload failed');
        $out = sys_get_temp_dir() . '/psz_' . bin2hex(random_bytes(4));
        $files = psz_extract_tar(psz_decrypt($_FILES['psz']['tmp_name'], psz_find_key($_FILES['lor']['tmp_name'])), $out);
        $msg = "OK – " . count($files) . " items → $out"; $ok = true;
    } catch (Throwable $e) { $msg = 'Error: ' . $e->getMessage(); $ok = false; }
}
header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html><html><head><meta charset="utf-8"><title>PSZ Extractor 2</title>
<style>body{font-family:system-ui;background:#0f1115;color:#e8eaed;padding:2rem;max-width:28rem;margin:0 auto}
.card{background:#1a1d24;padding:1.5rem;border-radius:12px}label{display:block;margin:.75rem 0 .25rem;color:#9aa0a6}
button{width:100%;padding:.75rem;border:0;border-radius:8px;background:#7c9cff;color:#0a0c10;font-weight:600;margin-top:1rem}
.ok{color:#3dd68c}.err{color:#ff6b6b}</style></head><body><div class="card">
<h1>PSZ Extractor 2</h1><p>Select <strong>.psz</strong> + <strong>.psz-data.lor</strong></p>
<form method="post" enctype="multipart/form-data">
<label>.psz</label><input type="file" name="psz" accept=".psz" required>
<label>.psz-data.lor</label><input type="file" name="lor" accept=".lor,text/plain" required>
<button type="submit">Decrypt</button></form>
<?php if ($msg !== ''): ?><pre class="<?= $ok?'ok':'err' ?>"><?= htmlspecialchars($msg) ?></pre><?php endif; ?>
</div></body></html>
