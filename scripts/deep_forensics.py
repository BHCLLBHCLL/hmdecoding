#!/usr/bin/env python3
"""Deeper forensic analysis of the .hm container and decompressed payload.

Run: python scripts/deep_forensics.py WS_3.2_3d_tetra_finish.hm
"""
from __future__ import annotations

import gzip
import re
import struct
import sys
import zlib
from pathlib import Path

GZIP_MAGIC = b"\x1f\x8b\x08"


def u32le(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def dump(b: bytes, start: int, length: int, label: str) -> None:
    print(f"--- {label} @0x{start:x} ---")
    for i in range(0, length, 16):
        chunk = b[start + i : start + i + 16]
        if not chunk:
            break
        hexs = " ".join(f"{x:02x}" for x in chunk)
        ascii_ = "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)
        print(f"{start + i:08x}  {hexs:<47}  {ascii_}")


def main(path: Path) -> None:
    raw = path.read_bytes()
    print(f"file size: {len(raw)}")

    first_gz = raw.find(GZIP_MAGIC)
    print(f"first gzip magic offset: {first_gz}")
    dump(raw, 0, min(first_gz, 64) if first_gz > 0 else 64, "wrapper prefix")

    members = []
    cursor = 0
    while True:
        off = raw.find(GZIP_MAGIC, cursor)
        if off < 0:
            break
        dec = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            payload = dec.decompress(raw[off:]) + dec.flush()
        except zlib.error as e:
            print(f"member @0x{off:x} failed: {e}")
            break
        consumed = len(raw[off:]) - len(dec.unused_data)
        crc, isize = struct.unpack("<II", raw[off + consumed - 8 : off + consumed])
        members.append((off, consumed, len(payload), crc, isize))
        print(f"gzip member @0x{off:x} compressed={consumed} uncompressed={len(payload)} "
              f"crc=0x{crc:08x} isize={isize}")
        cursor = off + consumed

    payload = gzip.decompress(raw[first_gz:])
    print(f"\ndecompressed payload: {len(payload)} bytes")

    dump(payload, 0, 256, "payload head")

    strings = sorted(set(re.findall(rb"[ -~]{8,}", payload)), key=len, reverse=True)
    interesting = [s.decode() for s in strings if re.search(rb"[A-Za-z]{3}", s)]
    print(f"\nprintable strings (len>=8, {len(interesting)} unique):")
    for s in interesting[:80]:
        print(f"  {s!r}")

    print("\nlength-prefixed ASCII records (pattern u32==u32==len):")
    found = 0
    for m in re.finditer(rb"[ -~]{6,}", payload):
        start = m.start()
        if start >= 8:
            l1 = u32le(payload, start - 8)
            l2 = u32le(payload, start - 4)
            if l1 == l2 == len(m.group()):
                tag = u32le(payload, start - 16)
                print(f"  @0x{start - 16:x} tag=0x{tag:08x} len={l1} text={m.group()[:60]!r}")
                found += 1
    print(f"  total: {found}")

    print("\npotential 'count' header words near file start (first 64 u32):")
    for i in range(0, 256, 4):
        v = u32le(payload, i)
        if 0 < v < 2_000_000:
            print(f"  @0x{i:03x} = {v}")

    dump(payload, max(0, len(payload) - 64), 64, "payload tail")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
