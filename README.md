# hmdecoding

Heuristic reverse parsing for a HyperMesh `.hm` sample.

## Current findings from `WS_3.2_3d_tetra_finish.hm`

- The file is not a plain ZIP archive.
- The first 12 bytes are a proprietary wrapper/prefix.
- A single gzip member starts at byte offset `12` (`0x0c`).
- Decompressing that member yields a `1,976,207` byte proprietary binary payload.
- The payload contains at least two identifiable text records:
  - `.ALTAIR.HW.IGES.FILE_NAME` -> `D:/4Ezhuanxiangjia6-7/4e.igsf`
  - `.ALTAIR.HW.IGES.DRAFTING_STANDARD`
- The same metadata window also exposes two named blocks:
  - `base` with inferred class id `5`
  - `tetras` with inferred class id `7`

## Script

Run the reverse parser with:

`python3 scripts/hm_reverse_parse.py WS_3.2_3d_tetra_finish.hm -o analysis_output --dump-payload --stdout`

The script writes:

- `analysis_output/summary.json`: container and inferred record summary
- `analysis_output/metadata_window.txt`: hexdump around the inferred metadata block
- `analysis_output/payload.bin`: decompressed binary payload when `--dump-payload` is used

The parser is intentionally heuristic. It does not claim full format coverage; it only extracts the repeatable structures that can be justified from the sample.
