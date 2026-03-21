#!/usr/bin/env python3
"""Heuristic reverse parser for Altair HyperMesh .hm containers.

The sample file in this repository is not a plain ZIP archive. It contains a
12-byte proprietary prefix followed by a gzip member whose decompressed payload
is another proprietary binary database. This script focuses on:

1. locating and unpacking the gzip member,
2. summarising the private wrapper,
3. scanning the decompressed payload for a few repeatable record patterns, and
4. exporting a JSON report plus optional raw payload / hexdump artifacts.

The binary database format is still largely unknown, so every parser in this
file is heuristic and intentionally conservative.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import struct
import sys
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

GZIP_MAGIC = b"\x1f\x8b\x08"
ASCII_TOKEN_RE = re.compile(rb"[A-Za-z0-9_./:-]{4,}")
NAME_TOKEN_RE = re.compile(rb"[A-Za-z_][A-Za-z0-9_]{2,31}")


def u32le(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def hexdump(data: bytes, start: int = 0, width: int = 16) -> list[str]:
    lines: list[str] = []
    for line_start in range(0, len(data), width):
        chunk = data[line_start : line_start + width]
        hex_part = " ".join(f"{byte:02x}" for byte in chunk)
        ascii_part = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in chunk)
        lines.append(f"{start + line_start:08x}  {hex_part:<47}  {ascii_part}")
    return lines


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class GzipMember:
    offset: int
    compressed_size: int
    uncompressed_size: int
    trailer_crc32: int
    trailer_isize: int
    payload: bytes = field(repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "offset": self.offset,
            "compressed_size": self.compressed_size,
            "uncompressed_size": self.uncompressed_size,
            "trailer_crc32": f"0x{self.trailer_crc32:08x}",
            "trailer_isize": self.trailer_isize,
            "sha256": sha256_hex(self.payload),
        }


def locate_gzip_members(data: bytes) -> list[GzipMember]:
    members: list[GzipMember] = []
    cursor = 0

    while True:
        offset = data.find(GZIP_MAGIC, cursor)
        if offset < 0:
            break

        inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            payload = inflater.decompress(data[offset:]) + inflater.flush()
        except zlib.error:
            cursor = offset + 1
            continue

        consumed = len(data[offset:]) - len(inflater.unused_data)
        if consumed < 8:
            cursor = offset + 1
            continue

        trailer = data[offset + consumed - 8 : offset + consumed]
        crc32_value, isize = struct.unpack("<II", trailer)
        members.append(
            GzipMember(
                offset=offset,
                compressed_size=consumed,
                uncompressed_size=len(payload),
                trailer_crc32=crc32_value,
                trailer_isize=isize,
                payload=payload,
            )
        )
        cursor = offset + consumed

    return members


def parse_wrapper_prefix(prefix: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {
        "size": len(prefix),
        "hex": prefix.hex(),
    }

    if len(prefix) >= 4:
        result["u32_le_words"] = [
            u32le(prefix, offset) for offset in range(0, len(prefix) - (len(prefix) % 4), 4)
        ]
        result["u32_be_words"] = [
            struct.unpack_from(">I", prefix, offset)[0]
            for offset in range(0, len(prefix) - (len(prefix) % 4), 4)
        ]

    if len(prefix) >= 4:
        tail4 = prefix[-4:]
        result["tail_float32_le"] = struct.unpack("<f", tail4)[0]
        result["tail_float32_be"] = struct.unpack(">f", tail4)[0]

    return result


def parse_text_record(payload: bytes, start: int) -> dict[str, Any] | None:
    if start < 0 or start + 8 > len(payload):
        return None

    tag = u32le(payload, start)
    payload_len = u32le(payload, start + 4)
    end = start + 8 + payload_len
    if payload_len == 0 or end > len(payload):
        return None

    fields: list[dict[str, Any]] = []
    cursor = start + 8
    while cursor < end:
        remaining = end - cursor
        if remaining >= 8:
            length_a = u32le(payload, cursor)
            length_b = u32le(payload, cursor + 4)
            if (
                0 < length_a == length_b <= end - (cursor + 8)
                and cursor + 8 + length_a <= end
            ):
                raw = payload[cursor + 8 : cursor + 8 + length_a]
                if raw and all(32 <= byte < 127 for byte in raw):
                    recovered = raw
                    probe = cursor + 8 + length_a
                    probe_limit = min(len(payload), end + 64)
                    while (
                        probe < probe_limit
                        and payload[probe] != 0
                        and 32 <= payload[probe] < 127
                        and (probe - (cursor + 8)) < length_a + 64
                    ):
                        probe += 1
                    if (
                        probe < probe_limit
                        and payload[probe] == 0
                        and probe > cursor + 8 + length_a
                    ):
                        recovered = payload[cursor + 8 : probe]

                    fields.append(
                        {
                            "kind": "ascii_text",
                            "declared_length": length_a,
                            "recovered_length": len(recovered),
                            "text": recovered.decode("ascii"),
                        }
                    )
                    cursor += 8 + length_a
                    continue

        if remaining >= 4:
            value = u32le(payload, cursor)
            fields.append({"kind": "u32", "value": value})
            cursor += 4
            continue

        fields.append({"kind": "tail_bytes", "hex": payload[cursor:end].hex()})
        break

    if not fields:
        return None

    return {
        "offset": start,
        "tag": f"0x{tag:08x}",
        "payload_length": payload_len,
        "fields": fields,
    }


def find_text_records(payload: bytes) -> list[dict[str, Any]]:
    starts: set[int] = set()
    for match in ASCII_TOKEN_RE.finditer(payload):
        start = match.start()
        if start < 16:
            continue
        text_len = len(match.group())
        if u32le(payload, start - 8) == text_len and u32le(payload, start - 4) == text_len:
            starts.add(start - 16)

    records: list[dict[str, Any]] = []
    for record_start in sorted(starts):
        parsed = parse_text_record(payload, record_start)
        if parsed is not None:
            records.append(parsed)
    return records


def choose_trailer_candidates(payload: bytes, string_offset: int, string_len: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    base = string_offset + string_len + 1

    for shift in range(0, 8):
        start = base + shift
        values: list[int] = []
        small_count = 0
        for step in range(6):
            word_offset = start + (step * 4)
            if word_offset + 4 > len(payload):
                break
            value = u32le(payload, word_offset)
            values.append(value)
            if value <= 100_000:
                small_count += 1

        if values:
            candidates.append(
                {
                    "relative_shift": shift,
                    "u32_values": values,
                    "small_value_count": small_count,
                }
            )

    candidates.sort(key=lambda item: (-item["small_value_count"], item["relative_shift"]))
    return candidates[:3]


def find_named_blocks(payload: bytes) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for match in NAME_TOKEN_RE.finditer(payload):
        start = match.start()
        if start < 12:
            continue

        name = match.group().decode("ascii")
        name_capacity = u32le(payload, start - 12)
        zero_word = u32le(payload, start - 8)
        class_id = u32le(payload, start - 4)
        if not (4 <= name_capacity <= 64 and zero_word == 0 and 0 < class_id <= 64):
            continue

        trailer_candidates = choose_trailer_candidates(payload, start, len(name))
        blocks.append(
            {
                "offset": start - 12,
                "name": name,
                "name_capacity": name_capacity,
                "class_id": class_id,
                "trailer_candidates": trailer_candidates,
            }
        )

    seen: set[tuple[int, str]] = set()
    deduped: list[dict[str, Any]] = []
    for block in blocks:
        key = (block["offset"], block["name"])
        if key not in seen:
            seen.add(key)
            deduped.append(block)
    return deduped


def extract_printable_tokens(payload: bytes, limit: int = 40) -> list[dict[str, Any]]:
    tokens: list[dict[str, Any]] = []
    for match in ASCII_TOKEN_RE.finditer(payload):
        text = match.group().decode("ascii")
        if len(text) < 8:
            continue
        tokens.append(
            {
                "offset": match.start(),
                "length": len(text),
                "text": text,
            }
        )

    tokens.sort(key=lambda item: (item["offset"], -item["length"]))
    return tokens[:limit]


def build_report(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    gzip_members = locate_gzip_members(data)
    if not gzip_members:
        raise ValueError("No gzip member found in the .hm file")

    primary = gzip_members[0]
    payload = primary.payload
    wrapper_prefix = parse_wrapper_prefix(data[: primary.offset])
    text_records = find_text_records(payload)
    named_blocks = find_named_blocks(payload)
    metadata_offsets = [
        record["offset"] for record in text_records
    ] + [block["offset"] for block in named_blocks]
    metadata_window = None
    if metadata_offsets:
        start = max(0, min(metadata_offsets) - 32)
        stop = min(len(payload), max(metadata_offsets) + 192)
        metadata_window = {
            "start": start,
            "stop": stop,
            "hexdump": hexdump(payload[start:stop], start=start),
        }

    report = {
        "input_file": str(path),
        "file_size": len(data),
        "file_sha256": sha256_hex(data),
        "gzip_members": [member.to_dict() for member in gzip_members],
        "wrapper_prefix": wrapper_prefix,
        "primary_payload": {
            "size": len(payload),
            "sha256": sha256_hex(payload),
            "head_hexdump": hexdump(payload[:256]),
        },
        "inferred_records": {
            "text_records": text_records,
            "named_blocks": named_blocks,
            "printable_tokens": extract_printable_tokens(payload),
            "metadata_window": metadata_window,
        },
    }
    return report, payload


def write_outputs(report: dict[str, Any], payload: bytes, output_dir: Path, dump_payload: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    metadata = report["inferred_records"].get("metadata_window")
    if metadata:
        (output_dir / "metadata_window.txt").write_text(
            "\n".join(metadata["hexdump"]) + "\n",
            encoding="utf-8",
        )

    if dump_payload:
        (output_dir / "payload.bin").write_bytes(payload)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Heuristically unpack and reverse-parse a HyperMesh .hm sample."
    )
    parser.add_argument("hm_file", type=Path, help="Path to the .hm sample")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("analysis_output"),
        help="Directory for JSON summary and optional extracted payload",
    )
    parser.add_argument(
        "--dump-payload",
        action="store_true",
        help="Also write the decompressed binary payload to payload.bin",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the JSON summary to stdout in addition to writing it to disk",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.hm_file.exists():
        print(f"error: input file not found: {args.hm_file}", file=sys.stderr)
        return 1

    try:
        report, payload = build_report(args.hm_file)
    except Exception as exc:  # pragma: no cover - used for CLI diagnostics.
        print(f"error: {exc}", file=sys.stderr)
        return 1

    write_outputs(report, payload, args.output_dir, dump_payload=args.dump_payload)

    if args.stdout:
        json.dump(report, sys.stdout, indent=2, ensure_ascii=True)
        sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
