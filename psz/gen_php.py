"""Unpacker generator."""
from pathlib import Path

def _generate_php_lor(key_hex: str, archive_name: str) -> str:
    """Generate a self-contained PHP unpacker script."""
    stem = Path(archive_name).stem
    return f"""<?php
/**
 * PSZ Unpacker (PHP) - generated for: {archive_name}
 * Requires PHP 7.1+ with OpenSSL
 *   php {stem}.psz-data.php {archive_name} -o extracted/
 */
define('KEY_HEX', '{key_hex}');
define('MAGIC', 'PSZ1');
define('NONCE_SIZE', 12);

function psz_error($msg) {{
    if (PHP_SAPI === 'cli') {{ fwrite(STDERR, "Error: $msg\\n"); exit(1); }}
    header('Content-Type: text/plain'); echo "Error: $msg\\n"; exit(1);
}}

function psz_decrypt($pszPath) {{
    if (!is_file($pszPath)) psz_error("archive not found: $pszPath");
    $data = file_get_contents($pszPath);
    if ($data === false || substr($data, 0, 4) !== MAGIC) psz_error('not a valid PSZ archive');
    $nonce = substr($data, 5, NONCE_SIZE);
    $ciphertext = substr($data, 5 + NONCE_SIZE);
    $key = hex2bin(KEY_HEX);
    $tag = substr($ciphertext, -16);
    $ct = substr($ciphertext, 0, -16);
    $plain = openssl_decrypt($ct, 'aes-256-gcm', $key, OPENSSL_RAW_DATA, $nonce, $tag);
    if ($plain === false) psz_error('decryption failed');
    return $plain;
}}

function psz_extract_tar($data, $dest) {{
    if (!is_dir($dest)) mkdir($dest, 0755, true);
    $offset = 0; $len = strlen($data);
    while ($offset + 512 <= $len) {{
        $header = substr($data, $offset, 512); $offset += 512;
        if (trim($header) === '') break;
        $name = rtrim(substr($header, 0, 100), "\\0");
        $size = octdec(rtrim(substr($header, 124, 12), "\\0 ") ?: '0');
        $type = $header[156] ?? '0';
        if ($name === '' || strpos($name, '..') !== false || ($name[0] ?? '') === '/') {{
            $offset += (int)ceil($size / 512) * 512; continue;
        }}
        $target = $dest . DIRECTORY_SEPARATOR . str_replace(['/', '\\\\'], DIRECTORY_SEPARATOR, $name);
        if ($type === '5' || substr($name, -1) === '/') {{
            if (!is_dir($target)) mkdir($target, 0755, true);
        }} else {{
            $dir = dirname($target);
            if (!is_dir($dir)) mkdir($dir, 0755, true);
            file_put_contents($target, substr($data, $offset, $size));
        }}
        $offset += (int)ceil($size / 512) * 512;
    }}
}}

if (PHP_SAPI === 'cli') {{
    $archive = null; $out = 'extracted';
    for ($i = 1; $i < $argc; $i++) {{
        if (($argv[$i] === '-o' || $argv[$i] === '--output') && isset($argv[$i + 1])) $out = $argv[++$i];
        elseif ($archive === null && isset($argv[$i]) && $argv[$i][0] !== '-') $archive = $argv[$i];
    }}
    if ($archive === null) {{ echo "Usage: php " . basename(__FILE__) . " <archive.psz> [-o output_dir]\\n"; exit(1); }}
    psz_extract_tar(psz_decrypt($archive), $out);
    echo "Successfully extracted to: $out\\n";
    exit(0);
}}
header('Content-Type: text/html; charset=utf-8');
echo '<!DOCTYPE html><html><body><h1>PSZ PHP Unpacker</h1><p>CLI: php ' . htmlspecialchars(basename(__FILE__)) . ' {archive_name} -o extracted/</p></body></html>';
"""
