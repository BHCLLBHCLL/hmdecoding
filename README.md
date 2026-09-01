# hmdecoding

HyperMesh `.hm` 文件格式解码（差分逆向，以本机 HyperMesh 2019 为 oracle）。

## 已实现（P0–P4 核心）

- **容器层**（122/122 语料证实）：12 字节前缀 `u32 0 + double 5.0` + gzip member @0x0c，解压为二进制数据库；
- **v11.05 双变体完整解码**（`hmdecoder/decoder.py`，已通过 oracle 全量验证）：
  - 节点记录（52B）：`[0][id][0][0][d64 x][d64 y][d64 z][0×12]`，节头 `[d64][1][136][count]`；
  - 变体 A 单元记录（48B）：`[0][0x01680000][行号×4][0][1][0x70241FF5][eid+1][...]`（1d_elements.hm: 400/400 连通性一致）；
  - 变体 B 单元记录（30B）：`[eid][0][0][config+256 u16][行号 u16 交错]`（仓库样本 WS_3.2_3d_tetra_finish.hm: 6408 节点/31843 单元与 oracle 完全一致）；
  - 单元引用 = 节点表行号（行号→id 经节点区映射）；
- **真实 INP/STEP/IGES 导出**（`hmdecoder/export.py` + `export_step.py` + `export_iges.py`）：`output/real_inp/`（真实 ID/拓扑/坐标；STEP 为 AP203 面片网格；IGES 5.3 点/线几何）；
- **几何点解码**：变体 A 点记录 `[u32 0][d64 xyz]`（4/4 oracle 验证）；变体 B 点块 `[id][1]` + 5 类偏移候选 + 评分（z 整数/52B 家族）——133/157 真点、0 纯误报；
- **语料与 ground truth**：122 教程文件索引（`corpus/corpus_index.json`）+ 123 文件 oracle 批量收割（`output/ground_truth/corpus_gt.json`）；
- **合成差分工具链**：HM2019 可写出 v19.02 .hm，`scripts/gen_synthetic.tcl` 生成受控样本链。

## 用法

```bash
python -c "import sys; sys.path.insert(0,'.'); from hmdecoder import decode; m = decode('WS_3.2_3d_tetra_finish.hm'); print(len(m.nodes), len(m.elements))"
# 6408 31843

python -c "import sys; sys.path.insert(0,'.'); from hmdecoder import decode; from hmdecoder.export import export_inp; export_inp(decode('WS_3.2_3d_tetra_finish.hm'), 'out.inp')"

python -c "import sys; sys.path.insert(0,'.'); from hmdecoder import decode; from hmdecoder.export_step import export_step; export_step(decode('WS_3.2_3d_tetra_finish.hm'), 'out.step')"
```

## oracle 工具（需 HyperMesh 2019 安装）

- `scripts/oracle_harvest.tcl` + `scripts/oracle_harvest.py`：批量收割实体计数/命名/配置直方图；
- `scripts/ws_validate.tcl` 等：逐 ID 查询坐标/连通性做验证；
- 运行：`& 'C:/Program Files/Altair/2019/hm/bin/win64/hmbatch.exe' -tcl <script>`（Tcl 内需写文件输出）。

## 语料与版权

- 语料为 Altair 教程文件（`C:/Program Files/Altair/2019/tutorials/hm`，122 个 .hm/.hm10），仓库仅存索引不复制文件；
- 仓库样本 `WS_3.2_3d_tetra_finish.hm`（LFS）为真实业务模型；
- 合规边界：不反汇编 DLL，仅使用 HyperMesh 正常读写与 Tcl API。

## 回归状态（2026-08 深入解析后）

- **oracle 对照（123 文件）**：node-ok 116/123 (94%)，elem-ok 120/123 (98%) — crash_tubes/abaqus3_0/truck/abaqus_contactManager_2D/seat_2/seat_start/hook 全解（family-1 MPC config 22/55 变长记录 v11/v12 双布局）；wing_section_complete 1001/1001、hm-ansys wizard_2d 202/202 全解（此前基线 node 66/98、elem 6/98）；v17 (17.01) 全解 dummy_positioner/seat_deformer 354174+585546；wing/wizard_2d/body_side_assembly/car_section/chapter2_2/manager_2d/abaqus_3D/hm-ansys_3d 全解；
- **元素段统一模型**：段头 [997][seg][175][count][X][Y]；A 型（CONST 锚 0x70??1FF5 家族）/ B 型（链式 eid）/ v12-13 u16 槽位型（58B）/ B 型 u16 槽位型（34B）/ 元素分块存储 + 断链重连；
- **节点段统一模型**：52B-flat / 92B-flat（+40B 附加）/ 56B-chain（v13）/ 68B（v14+）；[136] 头字节定位 + 结构扫描 fallback；
- 关键验证：body_side 7510+7182、housing 8690、fe_only 17264、quality_index 2216、truck 212139+204762、SEAT_MODEL 34295+27503、car_section 26697+27854、dummy_positioner(17.01) 116734+44062；
- 待解：v17 节点分块/元素全量、truck 非元素段排除、0D 元素段、chapter2_2(13.03) 节点布局；
- class_id 关联结论与 leg_geom 几何区初步定位见 `docs/format_spec_v1.md` §9–10。

## 文档

- `docs/format_spec_v1.md`：容器/头部/记录格式规范（置信度分级）；
- `docs/PLAN.md`：现状分析与 P0–P5 开放开发计划（含语料库盘点）。