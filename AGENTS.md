# AGENTS.md

## Cursor Cloud specific instructions

This is a data/research repository for decoding HyperMesh (`.hm`) file formats. It contains no runnable application code, no build system, no tests, and no linter configuration.

### Repository contents

- `WS_3.2_3d_tetra_finish.hm` — a HyperMesh CAE model file (tracked via Git LFS)
- `.gitattributes` — Git LFS tracking rules for `*.cgns` and `*.hm` files

### Key caveats

- **Git LFS is required.** The `.hm` and `.cgns` files are stored via Git LFS. After cloning or pulling, run `git lfs pull` to fetch actual binary content. Without this, you only get LFS pointer files (~131 bytes).
- There are no dependencies to install, no services to start, and no lint/test/build commands.
- If source code is added in the future, update this file with the relevant setup, lint, test, and run instructions.
