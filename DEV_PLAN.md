# hm_gui.py ↔ HyperMesh 2019 对标与 100% 开发规划

日期: 2026-09-05  
对标对象: `C:/Program Files/Altair/2019/hm/bin/win64/hmopengl.exe`  
权威清单:

- 工作区: `help/hm/topics/chapter_heads/workspace_hm_classic_r.htm`
- 面板: `help/hm/topics/panels/panels_r.htm` (**200** 个官方 Panel)
- 浏览器: `help/hm/topics/user_interface/browsers_r.htm` (**14** 个)
- 工具栏: `help/hm/topics/user_interface/toolbars_r.htm` (**8** 组)
- 教程入口: `help/hm/topics/chapter_heads/tutorials_r.htm`

当前代码: `hm_gui.py` (~2800 行) + `hmdecoder` (节点 / 单元 / 显示点 / 几何点)。

---

## 1. 总评

| 指标 | 当前 | 含义 |
|---|---|---|
| **功能完整度 (Coverage)** | **38%** | 官方 UI 条目在界面上有入口（含 NYI 按钮 / 空菜单）的比例 |
| **深度实现 (Depth)** | **14%** | 按官方行为加权后的真实能力（0=无, 1=与 HM 等价） |
| **可用对标完成度** | **≈ 16%** | 用户能真正完成的 HM 工作流占比 |

完整度被「底部 7 页 × ~90 个按钮」和「17 个顶层菜单名」拉高；深度被「14 个浅接线 + 无几何/网格/收集器内核」拉低。  
**100% 对标不是改皮肤，而是补齐解码实体、几何/网格内核、收集器/求解卡片，以及 `.hm` 写回。**

评分规则（深度）:

| 分 | 状态 |
|---|---|
| 0.00 | 缺失 |
| 0.10 | 仅有按钮/菜单，点了报 NYI |
| 0.25 | 对话框或列表，只覆盖一个子面板的一小部分 |
| 0.40 | 核心子面板可用，缺 collector / 预览 / 多实体 |
| 0.60 | 主路径可用，缺边界与求解卡片 |
| 0.80 | 大部分子面板，缺 oracle 级细节 |
| 1.00 | 与 HM 2019 行为等价 |

---

## 2. 分域得分

| 域 | 官方规模 | 入口覆盖 | 深度 | 权重 | 说明 |
|---|---|---|---|---|---|
| 工作区骨架 | 8 区 | 100% | 50% | 8% | 布局已像 HM；缺可停靠工具栏 / 用户配置 |
| 顶层菜单 | 17 | 100% | 18% | 8% | 名字齐，子项大多空或 NYI |
| 菜单叶子（估） | ~180 | 25% | 12% | 6% | File/Edit/View/Help 有内容 |
| 工具栏 | 8 组 | 25% | 20% | 6% | 仅 Standard + 显示/选择条 |
| 浏览器 / Tab | 14 | 29% | 12% | 10% | Model/Mask/Utility/EE 浅层 |
| 官方面板 | 200 | 35% | 6% | 25% | ~70 个有按钮，14 个浅实现 |
| 可视化 / 选择 | ~20 | 40% | 35% | 8% | 拾取/框选/四种显示可用 |
| 几何内核 | ~25 面板 | 20% | 2% | 8% | 无 BREP / 曲面 / 实体 |
| 网格内核 | ~20 面板 | 15% | 1% | 8% | 无 automesh / tetra / hex |
| 收集器 / BC / 求解 | ~25 | 10% | 1% | 7% | decoder 未解析 |
| 文件 I/O | ~15 | 40% | 30% | 6% | 开 .hm、存 .hmj、导出；不写 .hm |

加权完整度 ≈ **38%**，加权深度 ≈ **14%**。

---

## 3. 工作区骨架（8 区）

官方 `workspace_hm_classic_r.htm` 热区:

| # | 区域 | 深度 | 现状 | 100% 缺口 |
|---|---|---|---|---|
| 1 | Title Bar | 70% | `HyperMesh - hmdecoder - file` | 用户配置名、会话 `*.mvw`、多 client |
| 2 | Menu Bar | 60% | 17 个英文顶栏 | 完整子菜单、灰显/快捷键、Find Tools |
| 3 | Toolbars | 25% | 2 条不可停靠 | 8 组可停靠 + View>Toolbars 开关 |
| 4 | Tab Area | 40% | Utility / Mask / Model | 其余 11 个浏览器作 Tab |
| 5 | Modeling Window | 65% | VTK、浅色渐变、Model Info、三联轴 | 多视口、窗体、球面裁剪、透明度 |
| 6 | Entity Editor | 25% | 只读 Name/Value | 可编辑、求解卡片、多实体批量 |
| 7 | Panel Area | 45% | 7 page + 按钮栅格 | 子面板 / return-reject / collector 选择器 |
| 8 | Status Bar | 70% | 页名 / 坐标 / 计数 | 面板说明、当前 collector、进度 |

---

## 4. 菜单栏遍历（17 顶栏）

顺序对齐 2019 截图。

| 菜单 | 官方职责 | 当前入口 | 深度 | 已接线 | 缺失（要到 100%） |
|---|---|---|---|---|---|
| **File** | New/Open/Save/Import/Export/Print/User Profile | Open .hm/.hmj、Save .hmj、Export INP/STEP/IGES/CSV、Exit | 40% | 开模型、工程、4 种导出 | New 空库、写 .hm、Import CAD/FE、Import Browser、Print、Recent、Load User Profile |
| **Edit** | Undo、实体编辑、选择 | Undo/Redo、Translate/Create/Delete/Renumber/Flip、Select by ID/All/Reverse/Clear | 35% | 节点/单元级编辑 | Cut/Copy/Paste、Delete 面板全选项、Card Edit |
| **View** | 显示、标准视图、工具栏、浏览器 | 4 种显示、节点/显示点/几何点、Fit、7 标准视图、背景 | 40% | 可视化主路径 | 工具栏开关、浏览器开关、Thickness、Quality Color、Hidden Line、多视口 |
| **Collectors** | 建/改 comps/mats/props/loads… | 挂到 Analysis 页按钮（NYI） | 8% | — | 全部 collector 面板 + 当前 collector |
| **Geometry** | Geom 页 | 按钮在，几乎 NYI | 6% | nodes/node edit/temp nodes/distance/points 浅 | lines/surfaces/solids 全套、defeature、midsurface |
| **Mesh** | 1D/2D/3D 网格 | 按钮在，几乎 NYI | 5% | elem types 列表 | automesh/smooth/QI/tetramesh/hex/solid map |
| **Connectors** | 焊点/螺栓/胶 | 3 个 NYI | 3% | — | Connector Browser + realize |
| **Materials** | 材料收集器 | 1 条 NYI | 2% | — | 材料卡 +  decod 材料段 |
| **Properties** | 属性收集器 | 1 条 NYI | 2% | — | PSHELL/PSOLID 等 + 厚度显示 |
| **BCs** | 约束/载荷 | 同 Analysis NYI | 4% | — | constraints/forces/… + loadcols |
| **Setup** | User Profile、控制卡 | 说明对话框 | 12% | 提示只读 | 求解模板、control cards、output block |
| **Tools** | 变换/查询/组织 | numbers/find/mask/isolate/renumber/count/translate 浅 | 18% | 选择与显隐 | rotate/reflect/scale/project/organize 全量 |
| **Morphing** | 变形 | 1 条 NYI | 1% | — | domains/handles/morph |
| **Post** | 结果 | 按钮 NYI | 2% | — | contour/vectors/deformed；需结果文件 |
| **XYPlots** | 曲线 | 1 条 NYI | 1% | — | plots/curves 全套 ~15 面板 |
| **Preferences** | 选项 | 深/浅背景 | 12% | 背景 | Options 面板、颜色、拾取容差、单位 |
| **Applications** | 启动其他产品 | 启动 hmopengl | 20% | 调官方 exe | HyperView/HyperGraph/OS/Radioss |
| **Help** | 手册 | 本地 UI/手册/教程/Panels/HWD/About | 70% | 打开官方 HTML | 上下文 F1、面板内 Help |

叶子级完整度约 **25%**，深度约 **12%**。

---

## 5. 工具栏遍历（8 组）

官方 `View > Toolbars > HyperMesh`:

| 工具栏 | 官方按钮（摘） | 深度 | 现状 |
|---|---|---|---|
| **Standard / File** | New Open Save Print | 40% | Open/Save 图标，无 New/Print |
| **Undo-Redo** | Undo Redo | 70% | 有，命令栈可用 |
| **Display** | 着色/线框/透明、geom/mesh 开关 | 30% | 一个 Display 下拉 |
| **Visualization** | 按组件/属性/材料着色、厚度、质量色 | 15% | 仅按 config 调色 |
| **Collectors** | 当前 comp/mat/prop/loadcol | 0% | 无 |
| **Checks** | Distance Length MassCalc Edges Features CheckElems | 15% | Distance 浅；其余无 |
| **Favorites** | 用户收藏面板 | 0% | 无 |
| **Patch Checker** | 几何补丁检查 | 0% | 无 |

另: Connector Utility Toolbar — 0%。

100% 要求: 可停靠、可开关、图标对齐官方 24px 语义（不必抄 Altair 位图，需同等入口）。

---

## 6. 导航 / 浏览器遍历（14）

官方 `browsers_r.htm` 子页:

| 浏览器 | 深度 | 现状 | 100% 缺口 |
|---|---|---|---|
| **Model Browser** | 30% | Components=config 分组；Nodes/Elements/Geometry/Properties(0)/Titles(1)；勾选显隐 | 官方文件夹: Assemblies, Includes, Materials, Properties, Sets, Groups, Load/System/Vector cols, Multibodies；右键 Create/Edit/Card；拖拽组织 |
| **Entity Editor** | 25% | 只读表 | 可写字段、求解卡片、多选批量、验证 |
| **Mask Browser** | 20% | Isolate/Hide/Show/Reverse（按 config） | 按实体类型/config 矩阵显隐，与官方 Mask Browser 一致 |
| **Utility Menu** | 15% | 搜索框 + 日志 | 按 User Profile 的 Tcl Utility（Abaqus/OS/Radioss/Pam…） |
| Assembly Browser | 0% | — | 装配层次 |
| Part Browser | 0% | — | CAE part 层次 |
| Connector Browser | 0% | — | 连接器状态 / realize |
| Contact Browser | 0% | — | 接触对 |
| Solver Browser | 0% | — | 按求解卡片扁树 |
| Loadsteps Browser | 0% | — | 工况 |
| Reference Browser | 0% | — | 引用关系 |
| Entity State Browser | 0% | — | 激活/导出状态 |
| Mass Trimming Browser | 0% | — | 质量修剪 |
| Matrix Browser | 0% | — | 矩阵查询 |

另见（帮助另页，计入扩展）: Dummy、Mechanism、Link Entity、HyperBeam View — 均为 0%。

---

## 7. 官方 200 面板遍历

来源: `panels_r.htm` TOC，去重后 **200**。  
`hm_gui.py` 的 `HM_PANEL_PAGES` 约 **90** 个按钮名，对应约 **70** 个官方面板；`_on_panel_clicked` 浅接线 **14** 个。

深度标记: `—` 缺失 · `N` 仅 NYI 按钮 · `S` 浅实现 · `P` 部分可用。

### 7.1 已接线（14，平均深度 ~28%）

| 官方面板 | 按钮 | 深 | 实际做了什么 | 距 100% |
|---|---|---|---|---|
| Nodes | nodes | S 35% | 对话框建 1 个节点 | 多节点、on geom、temp、associate |
| Node Edit | node edit | S 30% | 等于 Translate 选中节点 | associate/replace/align 等子面板 |
| Temp Nodes | temp nodes | S 20% | 开关节点云 | HM 临时节点集合语义 |
| Distance | distance | S 25% | 两节点距离 | 三点角度、改距离 |
| Points | points | S 15% | 开关显示点 | 创建/编辑几何点 |
| Translate | translate | S 30% | 节点对话框 | N1/N2、实体多类型、预览 |
| Numbers | numbers | S 20% | 按 ID 选择 | 屏幕标注 ID |
| Find | find | S 20% | 同按 ID | 关联查找（节点→单元） |
| Renumber | renumber | S 40% | 单节点/单元改号 | 范围、offset、按 collector |
| Count | count | S 30% | 打印计数 | 官方分类计数面板 |
| Mask | mask | S 25% | 按 config 隐藏 | 实体级 mask |
| Edit Element | edit element | S 25% | 添加单元对话框 | combine/split/cleanup 子面板 |
| Elem Types | elem types | S 20% | 列出 config | 改类型 / 映射求解 |
| （isolate） | isolate | S 25% | 只显示选中 config | 官方 isolate 实体级 |

### 7.2 有按钮、NYI（约 56，深度 10%）

Geom: lines, line edit, length, surfaces, surface edit, defeature, midsurface, dimensioning, solids, solid edit, ribs, quick edit, edge edit, point edit, autocleanup  

1D: masses, rods, bars, beams, springs, dampers, gaps, plotel, rigids, rigidlinks, rbe3, equations, welds, spotweld, connectors, line mesh, 1D mesh  

2D: automesh, smooth, qualityindex, cleanup, elem offset, shrink, split, combine, replace, order change, ruled, spin, drag, spline, skin, elem cleanup, features  

3D: tetramesh, hex mesh, solid map  

Analysis: loadcols, constraints, forces, moments, pressures, temperatures, velocities, accelerations, systems, vectors, output blocks, loadsteps, control cards, card edit  

Tool: rotate, reflect, scale, project, position, permute, organize, edges, faces  

Post: contour, deformation, isosurfaces, section cut, query, title, legend, animate, transient, derived loadsteps  

### 7.3 官方有、界面无（约 130，深度 0%）

按帮助分类（名称保持官方）:

**几何 / 图元:** Cones, Ellipsoids, Planes, Spheres, Torus, Line Drag, Linear Solid, On Plane, Preserve Node, Quick Edit 的其余子面板  

**网格 / 质量:** Acoustic Cavity Mesh, Automeshing Secondary, CFD Tetramesh, Check Elems, Element Cleanup, Linear 1D, Mesh Edit, Midmesh, Rebuild Mesh, Shrink Wrap, Solid Mesh, Smooth Particle Hydrodynamics, Quality Index（完整准则编辑器）  

**收集器:** Assemblies, Beamsection Collectors, Blocks, Bodies, Component Collectors, Entity Sets, Load Collectors, Material Collectors, Multibody Collectors, Property Collectors, System Collectors, Vector Collectors, Titles, Tags, Super Elems, Sensors, Markers, Contactsurfs, Interfaces, Rigid Walls  

**分析 / 载荷:** Accels, Admas, Flux, Load on Geom, Load Types, Load Steps, NSM, Dependency, Dconstraints, Dequations  

**后处理 / XY:** Apply Result, Animation Secondary, Axis Labels/Scaling, Border, Contour, Curve Attribs, Deformed, Edit/Query/Read/Results Curves, Grid Attribs/Labels, Hidden Line, Integrate, Legend/Legend Edit, Plot Titles, Plots, Simple Math, Transient, Vector Plot, XY Plots, Window, True View, Spherical Clipping, Surface Transparency  

**优化 / 复合材料:** Composite Shuffle/Size, Composites, Desvar Link, Discrete DVS, Free Shape, Free Size, Gauge, Obj Reference, Objective, Opti Control, Optimization, Responses, Shape, Size, Topography, Topology, Table Entries, OSSmooth  

**多体 / 安全:** Dummy, FE Joints, Joints, MBS Joints/Planes, Seatbelt, ALE Setup  

**系统 / 杂项:** Build Menu, Card Editor, Card Image, Color, Config Edit, Constr Screen, Control Vol, Delete, Detach, Faces, Features, Fatigue, Global, HyperBeam, Mass Calc, Normals, Options, Organize, Penetration, Perturbations, Rename, Reorder, Solver, Summary, OptiStruct, Radioss  

---

## 8. 数据层对标（决定深度上限）

`hmdecoder.HMModel` 当前只有:

```
nodes, elements, display_points, geo_points, db_version, element_variant
```

HyperMesh 2019 模型浏览器还要:

Assemblies · Includes · Components · Materials · Properties · Entity Sets · Groups ·
Load cols · System cols · Vector cols · Beamsections · Multibodies · Titles ·
Connectors · Contacts · Loadsteps · Control cards · Geometry (points/lines/surfs/solids)

**未解码的实体，对应面板深度上限 ≈ 0。**  
这是 14% → 100% 的主瓶颈，不是 GUI 控件数量。

| 数据能力 | 深度 | 备注 |
|---|---|---|
| 读 .hm 节点/单元 | 85% | oracle 验证过的核心 |
| 显示点 / 几何点 | 60% | 能显示，几乎不能编辑 |
| 组件 / 材料 / 属性 | 0% | 未解析 |
| 几何 BREP | 5% | 仅点；无线/面/体 |
| 载荷 / 约束 / 系统 | 0% | 未解析 |
| 写 .hm | 0% | 只读逆向 |
| .hmj 工程 | 70% | 节点单元可往返 |
| 导出 INP/STEP/IGES/CSV | 40% | 面片级，非官方模板 |

---

## 9. 可视化 / 交互对标

| 能力 | 深度 | 现状 |
|---|---|---|
| 轨迹球旋转 / 平移 / 缩放 | 80% | VTK Trackball |
| 单击拾取单元/节点 | 75% | Qt 层绕开 VTK GrabFocus |
| Ctrl 多选 | 80% | 已测 |
| 框选 | 70% | Qt 层 AreaPick + frustum |
| 按 ID / 全选 / 反选 | 60% | 无 by collector / by config 过滤器 UI |
| 表面+边 / 实体 / 线框 / 点 | 70% | 无透明、无 HID |
| 按 config 着色 | 50% | 官方按 comp/prop/mat/quality |
| 坐标轴 | 80% | Orientation marker |
| 标准视图 / Fit | 75% | 7 向 |
| Model Info 叠加 | 80% | 右上角路径 |
| 多视口 / 窗体 | 0% | — |
| 截面 / 球裁剪 | 0% | — |

---

## 10. 到 100% 的分期规划

原则: **先解码、再内核、再面板深度、最后求解生态。**  
GUI 按钮可以提前铺齐（完整度），但深度必须跟数据走。

### Phase 0 — 对标基线冻结（1–2 周）· 目标深度 16%

- 本文件作为范围基线；每个官方面板建 `status: missing|nyi|shallow|partial|done`
- 自动化: 菜单/按钮清单测试，防止入口回退
- 交互回归: `scripts/gui_pick_final.py` + smoke 保持 ALL PASS

**完成定义:** 200 面板状态表可机读（建议 `hm_gui/catalog.json`）。

### Phase 1 — 网格编辑工具闭环（6–8 周）· 目标深度 28%

不依赖新解码，只吃现有 nodes/elements。

1. 把 Tool 页做实: Translate / Rotate / Reflect / Scale / Project / Position / Permute（多实体、预览、命令栈）
2. Organize（单元改 config/伪组件）、Delete 面板、Detach、Replace、Split/Combine（2D）
3. Numbers（屏幕 ID）、Find（节点↔单元）、Count 官方分类、Edges/Faces/Features 查询
4. Check Elems + Quality Index 只读（长宽比、歪斜、雅可比）
5. Normals / Reverse（已有 flip 升级为面板）
6. 框选/选择过滤器: by config / by ID range / displayed only

**完成定义:** 对 `WS_3.2_3d_tetra_finish.hm` 能完成「选-变-查-删-撤销」而不开 HyperMesh。

### Phase 2 — 解码收集器与浏览器（8–12 周）· 目标深度 40%

扩展 `hmdecoder`（对 hmopengl Tcl oracle）:

1. Component / Property / Material 段
2. Titles、Sets、Includes（若库中有）
3. Load / System / Vector collectors（能列出即可先不建）
4. Model Browser 换成官方文件夹 + 勾选显隐 + 右键
5. Entity Editor 可编辑名称/ID/颜色；组件颜色驱动 VTK
6. Visualization toolbar: color by component / config

**完成定义:** 卡车/教程模型的组件数、名称与 HM Model Browser 一致（oracle 对比脚本）。

### Phase 3 — 几何显示与 Geom 页（10–14 周）· 目标深度 52%

1. 解码 points / lines / surfaces / solids（或从显示网格重建特征边）
2. Geom 页: nodes（on geometry）、points、lines、surfaces、solids 的 create/edit 子集
3. Distance / Length / Mass Calc 对几何+网格
4. Edges / Features 画在视口
5. Autocleanup / Defeature / Midsurface: 先做检测，再做修复（修复可二期）

**完成定义:** 教程 `WS_3.2` 同时显示网格 + 特征边；Geom/nodes 可关联到点。

### Phase 4 — 2D/3D 网格生成（14–20 周）· 目标深度 65%

自研或调用开源内核（不依赖 hmopengl 许可）:

1. 2D: automesh（trimesh）、smooth、elem offset、ruled/spin/drag
2. 3D: tetramesh（表面封闭体）、elem types 转换
3. QI 准则编辑 + 颜色图例（对齐 View Element Quality）
4. 1D: masses/rods/bars/rigids/rbe3 创建（有节点即可）

Hex / solid map / shrink wrap / cavity 放 Phase 4b。

**完成定义:** 从一个封闭壳网格生成 tetra，单元质量可在 QI 面板看。

### Phase 5 — 分析设置（8–12 周）· 目标深度 74%

1. Loadcols、Constraints、Forces、Moments、Pressures、Temperatures
2. Systems / Vectors
3. Loadsteps、Output blocks、Card edit（通用卡，不求全求解器）
4. Loadsteps Browser + Solver Browser 扁树
5. 导出: 用官方 `templates/feoutput` 对齐的 INP/Nastran 子集

**完成定义:** 能给现有网格加 SPC+力，导出可被 Abaqus/Nastran 读入的最小 deck。

### Phase 6 — 连接器 / 装配 / Part（8–10 周）· 目标深度 80%

1. Connector Browser + spotweld/rigid 实现（节点耦合）
2. Assembly / Part Browser（层次可先只读）
3. Organize 跨 include
4. Mask Browser 实体类型矩阵

### Phase 7 — 后处理 / XY / 选项（6–8 周）· 目标深度 86%

1. 读 HM 结果或外部 ODB/OP2 的一条路径（可先 CSV/VTK）
2. Contour / Vectors / Deformed / Section cut / Legend / Transient
3. XY 基础: 读曲线、画一图
4. Options 面板、颜色、拾取容差
5. 多视口、窗体、球面裁剪

### Phase 8 — 求解生态与 Utility（10–16 周）· 目标深度 93%

1. User Profile: 先 Abaqus + OptiStruct 两套卡片子集
2. Utility Menu 按 profile 加载（可用 Tcl 子集或 Python 重写常用宏）
3. Control cards、复合材料、优化面板: 按模板逐张
4. Morphing / Dummy / MBS: 单独评估，非核心可保持 NYI 并在帮助中声明范围

### Phase 9 — `.hm` 写回与 oracle 100%（12–20 周）· 目标深度 100%

1. 在 Phase 2–5 实体都可解码的前提下设计写回
2. 每个实体 roundtrip: 写临时 .hm → hmopengl Tcl 导出 → diff
3. 不能合法写回的专有块保持只读并在 EE 标记
4. 官方 200 面板: 每个至少「主路径 + 1 个失败态 + 撤销」测试
5. 剩余长尾（Fatigue、SPH、ALE、OSSmooth…）按模板做最小可用或明确 Won't-do

**100% 定义（本合同）:**

- 完整度: 200 面板 + 14 浏览器 + 8 工具栏 + 17 菜单 **均有入口**（允许少量标注为 Out of scope 的专有求解器宏）
- 深度: 加权深度 **≥ 95%**；核心网格编辑 / 浏览器 / Geom+Mesh 主路径 **≥ 90%**
- Oracle: 节点、单元、组件、属性、材料、1D 刚性、基本载荷 与 HM 2019 导出一致
- `.hm` 写回: 上述实体 roundtrip 通过；其余只读

---

## 11. 建议里程碑与人力

按 1 名熟悉本仓库的全职开发估（含 oracle 脚本）:

| 阶段 | 深度 | 累计日历 |
|---|---|---|
| P0 基线 | 16% | 2 周 |
| P1 网格编辑 | 28% | 2.5 月 |
| P2 收集器+浏览器 | 40% | 5 月 |
| P3 几何 | 52% | 8 月 |
| P4 网格生成 | 65% | 12 月 |
| P5 分析 | 74% | 14 月 |
| P6 连接器/装配 | 80% | 16 月 |
| P7 后处理 | 86% | 18 月 |
| P8 求解生态 | 93% | 22 月 |
| P9 写回 + 100% | 100% | 26–28 月 |

并行（解码 + GUI）可压到约 **18–20 月**。  
若 **不写 .hm、不做求解器 Utility、不做 Morph/Opti/XY 全量**，务实产品线停在 **P5（~74% 深度）**，完整度仍可靠 NYI 铺到 **>90%**。

---

## 12. 风险与范围边界

1. **解码未知段** 是最大风险。没有 collector/geometry 字节级格式，P2–P3 会停。继续用 hmopengl Tcl oracle，不要猜。
2. **Altair 专有 IP**: 求解模板、部分 Utility Tcl、官方图标位图不能原样拷贝。对标的是**行为与信息架构**，资源自己画。
3. **几何内核**: 完整 CAD boolean / midsurface 等于再做一套 CAD。P3 应先「显示 + 点线面创建」，修复类放后。
4. **许可**: 可调用本机 `hmopengl.exe` 做对照，不能把 GUI 做成官方壳。
5. **Won't-do 候选（写入 100% 合同需甲方签字）:** ALE、SPH、Fatigue、Dummy 定位、完整 Radioss Utility、HyperBeam 截面图形编辑、Morph 全套。这些约占官方面板 **12–15%**；若剔除，其余域 100% 日历可减约一个 Phase。

---

## 13. 近期 30 天执行单（从 14% 走向 20%+）

1. 抽出 `hm_gui/catalog.json`（200 面板状态）+ 本文件同步  
2. 实现 Tool: Rotate / Reflect / Scale（节点+单元节点，命令栈）  
3. Numbers 屏幕标注、Find 关联、Check Elems 只读三项  
4. Model Browser 右键: Show/Hide/Isolate/Select  
5. Entity Editor: 节点坐标可写回 `CmdMoveNodes`  
6. Display toolbar: 按组件色 / 线框 / 透明 三个按钮  
7. 保持 `gui_pick_final.py` ALL PASS  

---

## 14. 一句话

当前 `hm_gui.py` 是 **HyperMesh 2019 经典工作区的可用外壳 + 网格查看/点选编辑器**。  
完整度 **38%**（入口多），深度 **14%**（内核少）。  
要 100% 对标，主线是 **扩 decoder → 收集器/几何 → 网格与变换面板做深 → 分析卡片 → `.hm` 写回**，而不是继续堆 NYI 按钮。
