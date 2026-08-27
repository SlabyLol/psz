<?php
/** PSZ Extractor 1 – DIRECT load demo.psz + demo.psz-data.lor */
declare(strict_types=1);
$BASE = dirname(__DIR__);
$PSZ = "$BASE/demo.psz"; $LOR = "$BASE/demo.psz-data.lor"; $OUT = "$BASE/out-extractor1";

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

try {
    $files = psz_extract_tar(psz_decrypt($PSZ, psz_find_key($LOR)), $OUT);
    $msg = "OK – loaded $PSZ via $LOR → $OUT (" . count($files) . " items)"; $ok = true;
} catch (Throwable $e) { $msg = "Error: " . $e->getMessage(); $ok = false; $files = []; }
if (PHP_SAPI === 'cli') { echo $msg . "\n"; foreach ($files as $f) echo "  $f\n"; exit($ok ? 0 : 1); }
header('Content-Type: text/html; charset=utf-8');
echo "<!DOCTYPE html><html><body style='font-family:system-ui;background:#111;color:#eee;padding:2rem'>";
echo "<h1>PSZ Extractor 1 – Direct</h1><pre style='color:" . ($ok?'#3dd68c':'#ff6b6b') . "'>" . htmlspecialchars($msg) . "</pre></body></html>";
