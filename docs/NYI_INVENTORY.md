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

## M7 — Mesh Generation（部分落地）

### NYI-M7-1 2D automesh (paving / advancing front)

- **触发场景**：点击 `2D / automesh` 面板；当前面板未在路由表 (NYI 灰显)。
- **当前行为**：`_nyi()` 灰显。
- **何时重启**：
  (a) 几何 record 解码完成 (NYI-M4-2/3/4 收尾)；
  (b) paving / advancing front 自研实现, 或 tetrameshdll.dll 导出接口 (许可风险备选);
  (c) 单元数 / 质量分布对拍与 HM 同量级 (按 DEV_PLAN.md §5 M7.5)。
- **已知证据**：
  - `hmdecoder/mesher.py:laplacian_smooth_2d` M7.2 已落地 (boundary 不动 + 内部节点 Laplacian 平均);
  - 5×5 规则 quad 单元测试: 边界 16/16 不动, 中心节点 (2,2) 位移 0。

### NYI-M7-3 3D tetramesh (Delaunay + 质量优化)

- **触发场景**：`3D / tetramesh` 面板；当前 NYI 灰显。
- **当前行为**：`_nyi()` 灰显。
- **何时重启**：
  (a) Delaunay 自研基础版 + 质量优化 (边界保护 / sliver 消除);
  (b) 或 tetrameshdll.dll 导出 (许可风险);
  (c) 至少 1 个样本 (bottle / arm2D) 产物对拍通过。
- **已知证据**：无；登记占位。

### NYI-M7-4 hex / solid map (映射法拉伸)

- **触发场景**：`3D / hex mesh` / `solid map` 面板。
- **当前行为**：`_nyi()` 灰显。
- **何时重启**：
  (a) 至少 1 个 hex-friendly 几何样本 (棱柱 / 长方体) oracle 完成；
  (b) 映射法自研实现。
- **已知证据**：无。

---

## M8 — Post-processing（部分落地）

### NYI-M8-1 结果解码 (.h3d / .res)

- **触发场景**：打开 .h3d / .res 结果文件；HM 求解器导出文件二进制格式逆向。
- **当前行为**：当前不识别 .h3d / .res；Post 页全部面板 NYI 灰显,
  除 contour 已落地伪场演示 (`hm_post.pseudo_contour_field`)。
- **何时重启**：
  (a) .h3d 二进制格式逆向 (HDF5-based, 见 H5py 已加入依赖);
  (b) 或 .res 文本格式 (LS-DYNA) 解析;
  (c) 至少 1 个真实结果文件 round-trip (oracle vs decode) PASS。
- **已知证据**：
  - `hmdecoder/hm_post.py:pseudo_contour_field` M8.2 占位已落地 (节点距离派生伪场);
  - `hm_gui.py:_show_pseudo_contour` 路由 `Post / contour` 面板;
  - WS_3.2_3d_tetra_finish.hm 伪 contour distance_to_centroid: min=72.7 max=290 avg=176 n=6408。

### NYI-M8-2 contour / deformed / section cut (真场量)

- **触发场景**：`Post / contour` 真场量版本 / `deformation` / `section cut` / `isosurfaces` 面板。
- **当前行为**：当前仅 contour 占位 (伪场), 其余 NYI 灰显。
- **何时重启**：
  (a) NYI-M8-1 解决;
  (b) VTK 标量映射器接入 contour (vtkColorTransferFunction + LookupTable);
  (c) deformed = 节点原坐标 + scale_factor * 位移场;
  (d) section cut = vtkCutter + implicit plane。
- **已知证据**：占位 `pseudo_contour_field` 4 模式 (distance_to_centroid / distance_to_origin / z_height / id_modulo)。

### NYI-M8-3 XYPlots (时间历程曲线)

- **触发场景**：`Post / XYPlots` 面板 (HM 2019 在 Post 第二列, 当前 HM_PANEL_PAGES 未注册)。
- **当前行为**：完全未在 UI 暴露。
- **何时重启**：
  (a) NYI-M8-1 解决 (结果时序数据);
  (b) XY 数据结构 + matplotlib / VTK 渲染层。
- **已知证据**：无。

### NYI-M8-4 多视口 / 窗体 / 球面裁剪 / 隐藏线

- **触发场景**：`View` 菜单多视口子项 / 窗体面板。
- **当前行为**：当前单视口 + Orientation Marker, 多视口未实现。
- **何时重启**：
  (a) vtkRenderer 多视口管理 (vtkRenderWindow.SetNumberOfers);
  (b) 球面裁剪 (vtkSphere with implicit function);
  (c) 隐藏线 (vtkHardwareSelector / PolygonOffset)。
- **已知证据**：无。

### NYI-M8-5 Morphing / Connectors

- **触发场景**：`Tool / Morphing` / Analysis / Connectors 面板。
- **当前行为**：当前 NYI 灰显。
- **何时重启**：
  (a) Morphing 域 decoder 闭环 (HM 内部 morphing constraint 段逆向);
  (b) Connectors 已在 M3.3 收尾 (comps 313/313 含 connectors 178), 但 connector 几何 record 解码 NYI。
- **已知证据**：connectors 名称 oracle 在 FA3 已抓 (178 条, 见 M3.3 门禁报告)。

---

## 变更记录

- 2026-09-06 创建本文件（M4.1 收尾 + M4.2 Geom 页接线），按 DEV_PLAN.md §7 item 6 入册
  M4 全家族 NYI（NYI-M4-1..5）+ M1-M3 历史边界 + M5-M8 待启动占位。
- 2026-09-06 M4.3 落地（Geom/length 长度汇总）；NYI-M4-1..5 维持登记。
- 2026-09-06 M5 部分落地：hm_writer.py v0 (节点段 52B + 元素段 A 型锚) + m5_roundtrip.py 三同门禁。
  NYI-M5-1/2 从"待启动"转为"部分落地"：节点段 round-trip 全等，collector/几何/B型元素 NYI 维持。
- 2026-09-06 M6.1 部分落地：hm_card.py 4 张卡片骨架 (PSHELL/PSOLID/MAT1/CQUAD4) + Analysis/card edit 面板接线。
  NYI-M6-1/2/3 维持：真实卡数据/Analysis page 接线/Solver Browser 仍 NYI。
- 2026-09-06 M7.2 部分落地：hm_mesher.py Laplacian smooth (5×5 quad 边界不动验证通过) + 2D/smooth 面板接线。
  NYI-M7-1/3/4 维持：automesh/tetramesh/hex map 仍未启动。
- 2026-09-06 M8.2 部分落地：hm_post.py pseudo_contour_field 4 模式 (distance_to_centroid/origin/z_height/id_modulo) + Post/contour 面板接线。
  NYI-M8-1/2/3/4/5 维持：.h3d/.res 解码/真场量/XYPlots/多视口/Morphing 仍 NYI。
- 后续每次重启 NYI 项目，需在变更记录追加 commit hash / oracle 增量 / 覆盖率。