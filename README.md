# hmdecoding

HyperMesh `.hm` 文件格式解码（差分逆向，以本机 HyperMesh 2019 为 oracle）。

## 已实现（P0–P4 核心）

- **容器层**（122/122 语料证实）：12 字节前缀 `u32 0 + double 5.0` + gzip member @0x0c，解压为二进制数据库；
- **v11.05 双变体完整解码**（`hmdecoder/decoder.py`，已通过 oracle 全量验证）：
  - 节点记录（52B）：`[0][id][0][0][d64 x][d64 y][d64 z][0×12]`，节头 `[d64][1][136][count]`；
  - 变体 A 单元记录（48B）：`[0][0x01680000][行号×4][0][1][0x70241FF5][eid+1][...]`（1d_elements.hm: 400/400 连通性一致）；
  - 变体 B 单元记录（30B）：`[eid][0][0][config+256 u16][行号 u16 交错]`（仓库样本 WS_3.2_3d_tetra_finish.hm: 6408 节点/31843 单元与 oracle 完全一致）；
  - 单元引用 = 节点表行号（行号→id 经节点区映射）；
- **真实 INP 导出**（`hmdecoder/export.py`）：`output/real_inp/`（真实 ID/拓扑/坐标）；
- **语料与 ground truth**：122 教程文件索引（`corpus/corpus_index.json`）+ 123 文件 oracle 批量收割（`output/ground_truth/corpus_gt.json`）；
- **合成差分工具链**：HM2019 可写出 v19.02 .hm，`scripts/gen_synthetic.tcl` 生成受控样本链。

## 用法

```bash
python -c "import sys; sys.path.insert(0,'.'); from hmdecoder import decode; m = decode('WS_3.2_3d_tetra_finish.hm'); print(len(m.nodes), len(m.elements))"
# 6408 31843

python -c "import sys; sys.path.insert(0,'.'); from hmdecoder import decode; from hmdecoder.export import export_inp; export_inp(decode('WS_3.2_3d_tetra_finish.hm'), 'out.inp')"
```

## oracle 工具（需 HyperMesh 2019 安装）

- `scripts/oracle_harvest.tcl` + `scripts/oracle_harvest.py`：批量收割实体计数/命名/配置直方图；
- `scripts/ws_validate.tcl` 等：逐 ID 查询坐标/连通性做验证；
- 运行：`& 'C:/Program Files/Altair/2019/hm/bin/win64/hmbatch.exe' -tcl <script>`（Tcl 内需写文件输出）。

## 语料与版权

- 语料为 Altair 教程文件（`C:/Program Files/Altair/2019/tutorials/hm`，122 个 .hm/.hm10），仓库仅存索引不复制文件；
- 仓库样本 `WS_3.2_3d_tetra_finish.hm`（LFS）为真实业务模型；
- 合规边界：不反汇编 DLL，仅使用 HyperMesh 正常读写与 Tcl API。

## 回归状态（P4 快照）

- 节点解码：56/98 语料文件与 oracle 计数一致；单元解码：6/98（含仓库样本与 1d_elements 全量）；
- 其余为 v11 子变体/其他 DB 版本（v10/v12-13/v14+），见 `docs/PLAN.md` 后续计划。

## 文档

- `docs/format_spec_v1.md`：容器/头部/记录格式规范（置信度分级）；
- `docs/PLAN.md`：现状分析与 P0–P5 开放开发计划（含语料库盘点）。
