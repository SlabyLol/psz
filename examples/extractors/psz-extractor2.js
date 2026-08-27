#!/usr/bin/env node
/** PSZ Extractor 2 – select files: node psz-extractor2.js <a.psz> <a.psz-data.lor> [-o out] */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

function findKey(lorPath) {
  const text = fs.readFileSync(lorPath, "utf8");
  const m = text.match(/KEY_HEX\s*=\s*["']([0-9a-fA-F]{64})["']/)
    || text.match(/define\(\s*['"]KEY_HEX['"]\s*,\s*['"]([0-9a-fA-F]{64})['"]/);
  if (!m) throw new Error("KEY_HEX not found");
  return Buffer.from(m[1], "hex");
}

function extractTar(buf, dest) {
  fs.mkdirSync(dest, { recursive: true });
  let offset = 0;
  while (offset + 512 <= buf.length) {
    const header = buf.subarray(offset, offset + 512);
    offset += 512;
    if (header.every((b) => b === 0)) break;
    const name = header.subarray(0, 100).toString("utf8").replace(/\0.*$/, "");
    const size = parseInt(header.subarray(124, 136).toString("utf8").replace(/\0| /g, "") || "0", 8) || 0;
    const type = String.fromCharCode(header[156] || 48);
    if (!name || name.includes("..") || name.startsWith("/")) {
      offset += Math.ceil(size / 512) * 512;
      continue;
    }
    const target = path.join(dest, name);
    if (type === "5" || name.endsWith("/")) fs.mkdirSync(target, { recursive: true });
    else {
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.writeFileSync(target, buf.subarray(offset, offset + size));
    }
    offset += Math.ceil(size / 512) * 512;
  }
}

const args = process.argv.slice(2);
let psz = null, lor = null, out = "extracted";
for (let i = 0; i < args.length; i++) {
  if ((args[i] === "-o" || args[i] === "--output") && args[i + 1]) out = args[++i];
  else if (!psz && !args[i].startsWith("-")) psz = args[i];
  else if (!lor && !args[i].startsWith("-")) lor = args[i];
}
if (!psz || !lor) {
  console.error("Usage: node psz-extractor2.js <file.psz> <file.psz-data.lor> [-o out]");
  process.exit(1);
}
const data = fs.readFileSync(psz);
const key = findKey(lor);
const nonce = data.subarray(5, 17);
const ctWithTag = data.subarray(17);
const tag = ctWithTag.subarray(ctWithTag.length - 16);
const ct = ctWithTag.subarray(0, ctWithTag.length - 16);
const d = crypto.createDecipheriv("aes-256-gcm", key, nonce);
d.setAuthTag(tag);
extractTar(Buffer.concat([d.update(ct), d.final()]), out);
console.log("OK → " + path.resolve(out));
