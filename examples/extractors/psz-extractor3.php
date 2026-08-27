<?php
/** PSZ Extractor 3 – list / open / -m */
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
function psz_list_tar(string $data): array {
    $names = []; $offset = 0; $len = strlen($data);
    while ($offset + 512 <= $len) {
        $header = substr($data, $offset, 512); $offset += 512;
        if (trim($header) === '') break;
        $name = rtrim(substr($header, 0, 100), "\0");
        $size = octdec(rtrim(substr($header, 124, 12), "\0 ") ?: '0');
        if ($name !== '' && strpos($name, '..') === false && ($name[0] ?? '') !== '/') $names[] = $name;
        $offset += (int) ceil($size / 512) * 512;
    }
    return $names;
}
if (PHP_SAPI !== 'cli') { echo "CLI only.\n  php psz-extractor3.php list a.psz a.psz-data.lor\n  php psz-extractor3.php open a.psz a.psz-data.lor -o out -m file.txt\n"; exit; }
$cmd = $argv[1] ?? null; $psz = $argv[2] ?? null; $lor = $argv[3] ?? null; $out = 'extracted'; $members = [];
for ($i = 1; $i < $argc; $i++) {
    if (($argv[$i] === '-o' || $argv[$i] === '--output') && isset($argv[$i+1])) $out = $argv[++$i];
    elseif (($argv[$i] === '-m' || $argv[$i] === '--member') && isset($argv[$i+1])) $members[] = $argv[++$i];
}
if (!$cmd || !$psz || !$lor) { echo "Usage: list|open <psz> <lor> [-o out] [-m path]\n"; exit(1); }
try {
    $plain = psz_decrypt($psz, psz_find_key($lor));
    if ($cmd === 'list') { foreach (psz_list_tar($plain) as $n) echo "$n\n"; exit(0); }
    if ($cmd === 'open') {
        $files = psz_extract_tar($plain, $out, $members ?: null);
        echo "Extracted " . count($files) . " → $out\n"; foreach ($files as $f) echo "  $f\n"; exit(0);
    }
    throw new RuntimeException("Unknown command: $cmd");
} catch (Throwable $e) { fwrite(STDERR, "Error: {$e->getMessage()}\n"); exit(1); }
