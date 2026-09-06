# NYI_INVENTORY.md — Not-Yet-Implemented 边界项登记

> 依据 `DEV_PLAN.md §7 item 6`：网格内核数值等价豁免 + 求解器广度裁剪 + 各阶段无法在
> 当前交付周期内闭合的边界项，统一入册本文件。每条登记必须给出：
> **触发场景 / 当前行为 / 何时重启 / 已知证据**。

登记规则：

1. 每条 NYI 给出唯一 ID（`NYI-<M##>-<idx>`），按里程碑分段。
2. `触发场景` 写明哪个用户路径/官方面板会触发；当前行为写实际看到的结果（错误码、提示文本）。
3. `何时重启` 必须是可观察的外部条件（oracle 采集完成 / 新格式样本 / 工时到位），不是模糊口号。
4. `已知证据` 给当前已抓到的 oracle 日志、ticket、git commit 锚点，方便后续接手不重做。

---

## M1–M3 已完成（仅记录历史边界，回滚时查）

- **NYI-M3-1** `Analysis page` 全 NYI → 已转入 M6 阶段；当前 100% 灰显由 `_nyi()` 统一处理。
- **NYI-M3-2** `Post page` 全 NYI → 已转入 M8 阶段；同上。
- **NYI-M3-3** `2D/3D mesh generation` 全 NYI → 已转入 M7 阶段；同上。

> 这些条目不在 M4 重启范围内，存档保留以便回归。

---

## M4 — Geometry（进行中）

### NYI-M4-1 几何点 db 11.05 碎片化段（非规整 record 布局）

- **触发场景**：打开 Full_Motion_TV_Mount_Partly_Open、Full_Motion_TV_Mount、molding_*、rubber_* 等
  db 11.05 但点段记录不是连续 48B 规整布局的样本。`HMModel.geo_points` 长度为 0 或远低于 oracle。
- **当前行为**：解析器静默返回空集；`hm_gui` `Geom/points` 面板切换只影响显示开关，无几何点可看；
  `Geom/point edit` 弹出"本模型未解码几何点"。
- **何时重启**：
  (a) oracle 端采集到至少 5 个该家族的样本，每个 ≥ 1000 点的完整覆盖；
  (b) 找到替代的段头签名（magics != 0x8120、check != 256）或发现混合 step（52/56/64）；
  (c) 逆向资产记录到 `scripts/m4_point_scan.py` 的 step-chain 启发式可调阈值后 F1 ≥ 95%。
- **已知证据**：
  - 段头签名 v3 解码器在 frame_assembly_* 上覆盖率 99.8%（535/536）；见 `scripts/m4_point_segment.py`。
  - 跨文件门禁 `scripts/m4_gate_points.py` 总覆盖率仅 3.8%（308/8023），其余家族全 0。
  - 失败家族包括 Full_Motion_TV_Mount_Partly_Open、Full_Motion_TV_Mount、molding_*、rubber_* 等；
    oracle 端 BREP 真值已抓 `output/ground_truth/m4_geom_gt.json`。

### NYI-M4-2 几何 lines 实体级解码（仅端点 oracle，无段解码）

- **触发场景**：打开任意带 line 几何的样本；`HMModel` 当前无 `lines` 字段；
  `Geom/lines`、`Geom/line edit`、`Geom/length` 面板路由命中 `_nyi()`。
- **当前行为**：UI 点击提示 "[NYI] Geom/lines — panel from HyperMesh 2019, not implemented"。
  `points<-by lines` 已通过 oracle 矩阵验证可拉端点（见 `scripts/m4_assoc_matrix.tcl`），
  但**线段本身**的 record 布局未逆向。
- **何时重启**：
  (a) 至少 3 个 line 类型样本（line2 / 圆 / 样条 / arc）oracle 完成；
  (b) 找到 line record 头签名或在已知 48/52/56B 点段基础上的拼接规则；
  (c) `HMModel.lines` 字段就位并能由 `select_geo_point_dialog` 模式衍生 `select_line_dialog`。
- **已知证据**：
  - `points<-by lines` 关联语法工作正常，`scripts/m4_assoc_matrix.tcl` 矩阵已覆盖。
  - `lines<-by surfaces` **不支持**（HM 限制）；反向构造需要 surf→line 矩阵，oracle 已抓。

### NYI-M4-3 几何 surfaces 实体级解码（BREP 拓扑记录）

- **触发场景**：同 NYI-M4-2，但属于 surface 类型；`Geom/surfaces`、`Geom/surface edit`、
  `Geom/defeature`、`Geom/midsurface`、`Geom/dimensioning` 全 NYI。
- **当前行为**：UI 灰显 `_nyi()`。
- **何时重启**：
  (a) 至少 3 个 surface 类型样本（quilt / surface / free-edge）oracle 完成；
  (b) surface record 头签名定位，与 points/lines 联动可推出所属 points 与 lines；
  (c) `HMModel.surfaces` 字段就位。
- **已知证据**：
  - `surfaces<-by lines` 关联语法工作正常，可由 lines 集合反推 surface。
  - oracle `output/ground_truth/m4_geom_gt.json` 65 文件覆盖完整。

### NYI-M4-4 几何 solids 实体级解码

- **触发场景**：`Geom/solids`、`Geom/solid edit`、`Geom/ribs` 面板 NYI。
- **当前行为**：UI 灰显 `_nyi()`。
- **何时重启**：
  (a) 至少 3 个 solid 样本 oracle 完成；
  (b) solid record 头签名定位；
  (c) `HMModel.solids` 字段就位。
- **已知证据**：
  - `solids` 类型在 corpus 中样本较少（≤ 5 个），需扩展采集。

### NYI-M4-5 其他 db 版本（13.x / 14.x / 15.x / 16.x / 17.x / 19.x）的几何点段

- **触发场景**：db ≥ 13.x 的样本（db_version 字段读取即知）。
- **当前行为**：v3 解码器只针对 db 11.05 规整段签名（0x8120 / 256）有效，其他版本静默返回空集。
- **何时重启**：
  (a) 每个目标 db 版本至少 2 个样本 oracle 完成；
  (b) 找到对应版本的段头签名或确认 layout 兼容；
  (c) `parse_geo_points_v3` 派生出 `parse_geo_points_v{db_major}()`。
- **已知证据**：
  - 当前 corpus 中 db ≥ 13.x 样本极少（合成测试 `corpus/synthetic/v1913_*` 是 db 19.02 简单测试样本）。
  - 真实工业样本集中在 db 11.05。

---

## M5 — 写端 / 逆向编码（部分落地）

### NYI-M5-1 完整 .hm 二进制写端 (collector 段 / 92B 节点 / B 型元素段 / 多版本)

- **触发场景**：调用 `hmdecoder.hm_writer.encode_minimal_db11_05()` 之外的写端能力。
- **当前行为**：`hmdecoder.hm_writer` v0 已能写出 52B 布局 A 节点段 + 元素段 A 型锚；
  自家 `decode()` 能 round-trip 节点坐标全等（如 WS_3.2_3d_tetra_finish.hm 6408/6408 PASS）。
  但 collector (comps/mats/props/groups)、几何点、92B/56B 节点布局、元素段 B 型（链式 eid）、
  db ≥ 13 多版本兼容均未实现。`scripts/m5_roundtrip.py` JSON 路径全等。
- **何时重启**：
  (a) collector 段逆向完成（HM 内部标签名格式未知，需 oracle）；
  (b) 92B 节点布局样本 ≥ 3 个 oracle；
  (c) 元素段 B 型样本 ≥ 3 个 oracle；
  (d) hmbatch 端到端验证：encode → hmbatch 读 → 计数/坐标/单元内容三同。
- **已知证据**：
  - `hmdecoder/hm_writer.py:encode_minimal_db11_05` v0 实现；
  - `scripts/m5_roundtrip.py` JSON 三同门禁脚本；
  - 当前覆盖: WS_3.2_3d_tetra_finish.hm 节点段 6408/6408 全等。

### NYI-M5-2 编辑保存链路 (GUI → .hm 直写 → hmbatch 重开验证)

- **触发场景**：GUI 改一处（移动节点/改组件名）→ `Save Project (.hmj)` 落盘 → hmbatch 读回比对。
- **当前行为**：GUI Save 路径是 `.hmj` JSON，不直接写 .hm 二进制；
  `hmdecoder/hm_writer.py` v0 不被 GUI 调用。
- **何时重启**：
  (a) NYI-M5-1 collector 段写端完成；
  (b) M3.4 Entity Editor 可写字段完成；
  (c) GUI `Save Project (.hmj)` 菜单额外提供 "Save .hm (v0)" 子项；
  (d) hmbatch 端到端回归: GUI 编辑 → 落盘 → hmbatch 重开比对 oracle 一致。
- **已知证据**：
  - 现有 `save_hmj` (HMModel → JSON) 路径 OK；
  - `EditableModel.apply(cmd)` 命令栈已支持 undo/redo (M3.3)。

---

## M6 — Solver 生态 / Card Image（待启动）

- **NYI-M6-1** Card image 解码（domain 9, 3%）。
- **NYI-M6-2** Analysis page constraints / loads 接线。
- **NYI-M6-3** Solver Browser（除 LS-DYNA 已就位）。

> 重启条件待 M5 收尾后评估。

---

## M7 — Mesh Generation（待启动）

- **NYI-M7-1** 2D automesh（domain 7, 0%）。
- **NYI-M7-2** Laplacian smooth。
- **NYI-M7-3** Delaunay tetra。

> 重启条件待 M6 收尾后评估。

---

## M8 — Post-processing（待启动）

- **NYI-M8-1** `.h3d` / `.res` 解码。
- **NYI-M8-2** Contour / deformed / section cut。
- **NYI-M8-3** Multi-viewport。

> 重启条件待 M7 收尾后评估。

---

## 变更记录

- 2026-09-06 创建本文件（M4.1 收尾 + M4.2 Geom 页接线），按 DEV_PLAN.md §7 item 6 入册
  M4 全家族 NYI（NYI-M4-1..5）+ M1-M3 历史边界 + M5-M8 待启动占位。
- 2026-09-06 M4.3 落地（Geom/length 长度汇总）；NYI-M4-1..5 维持登记。
- 2026-09-06 M5 部分落地：hm_writer.py v0 (节点段 52B + 元素段 A 型锚) + m5_roundtrip.py 三同门禁。
  NYI-M5-1/2 从"待启动"转为"部分落地"：节点段 round-trip 全等，collector/几何/B型元素 NYI 维持。
- 后续每次重启 NYI 项目，需在变更记录追加 commit hash / oracle 增量 / 覆盖率。