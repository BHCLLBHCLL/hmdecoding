# hmdecoding vs HyperMesh 2019 功能差距全面分析（12 维度）

> 日期: 2026-09 ｜ 仓库: hmdecoding ｜ 对照: Altair HyperMesh 2019（hmopengl.exe / hmbatch.exe）
>
> 分析方法参考: D:/training/cgns/pphdecoding 的 function_gap_analysis.md ——
> 双口径实测（完整度% + 深度 L1-L4）、满格/差距分层、边界项入册 NYI_INVENTORY、
> 内核数值等价以「官方内核全驱动 + 字节级格式闭环 + 量化对拍」替代（复刻不在目标内）。
>
> 分析范围: hmdecoder/decoder.py（格式层）、hm_gui.py（GUI 层）、scripts/（oracle 差分与门禁）。
>
> 关联文档: DEV_PLAN.md（多阶段开发规划）、README.md（解码器结论）、docs/format_spec_v1.md。

---

## 0. 12 功能域完整度对照图

| # | 功能域 | 完整度 | 深度 | 分层 |
|---|---|---|---|---|
| 1 | .hm 解析（读端） | 92% | L3+ | 主战层 |
| 2 | .hm 写端 | 0% | — | 差距区 |
| 3 | collector 实体解码 | 2% | L1 | 差距区 |
| 4 | 几何实体解码 | 5% | L1 | 差距区 |
| 5 | 面板体系（200 官方面板） | 35% | L1+ | 差距区 |
| 6 | 浏览器与工具栏（14+8） | 29% | L1 | 差距区 |
| 7 | Select/View/3D 可视化 | 40% | L2 | 差距区 |
| 8 | 工程文件管理与导入导出 | 40% | L2 | 差距区 |
| 9 | 求解与后处理生态 | 3% | — | 差距区 |
| 10 | 网格生成 | 3% | — | 差距区 |
| 11 | 网格与几何编辑 | 30% | L1+ | 差距区 |
| 12 | 宿主自动化（hmbatch oracle） | 55% | L2+ | 主战层 |

```
功能域                      0        25        50        75      100
────────────────────────────────────────────────────────────────────

【主战层】
1  .hm 解析（读端）      ██████████████████████████████████████░  92% (L3+)
12 宿主自动化 oracle     ██████████████████████████░░░░░░░░░░░░░░  55% (L2+)

【差距区】
7  Select/View/3D        ████████████████░░░░░░░░░░░░░░░░░░░░░░░░  40% (L2)
8  工程文件与导入导出    ████████████████░░░░░░░░░░░░░░░░░░░░░░░░  40% (L2)
5  面板体系              ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  35% (L1+)
11 网格与几何编辑        ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  30% (L1+)
6  浏览器与工具栏        ███████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  29% (L1)
4  几何实体解码          ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   5% (L1)
9  求解与后处理生态      █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   3% (—)
10 网格生成              █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   3% (—)
3  collector 实体解码    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   2% (L1)
2  .hm 写端              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% (—)
```

> 每格 = 2.5%（40 格满幅）。整体完整度（12 域均分）= **27.8%**；深度以 L1-L2 为主，
> L3 仅域 1（读端）一处。**满格层 0 域；主战层 2 域（读端 + oracle 流水线），
> 差距区 10 域。**

---

## 1. 能力分层（HM 适配 pphdecoding L1-L4）

| 层 | 含义 | 验收 |
|---|------|------|
| **L1 UI** | 面板/控件/布局对齐官方截图，NYI 灰显并给理由 | 离屏 GUI 测试 + 人工对照截图 |
| **L2 参数** | 面板输入 ↔ 模型数据往返（round-trip），编辑真实生效 | round-trip 测试 |
| **L3 驱动** | 解码/操作经 oracle（hmbatch Tcl）验证等价 | 123 文件 count 门禁 + 91 文件 content 门禁 |
| **L4 结果** | 列表/报告/预览来自真实数据（网格质量、卡片值等） | 与 HM 同工程对照 |

> L3 的「驱动」在解码器语境 = 「解码结果与 oracle 逐实体一致」；
> 在面板语境 = 「面板操作经 hmbatch 无头驱动官方面板后模型变化一致」（面板级 oracle，未建）。

---

## 2. 非目标（明确不做）

- 在本仓库复刻 HyperMesh 的网格内核数值算法（tetramesh 策略等）——与 pphdecoding 结论同理:
  产物与控制面可摸透，完整逆向 mesher 策略不现实；以「产物质量量化对拍」替代
- 复刻 hmobj.dll 的面板 C++ 实现——行为以 help HTML + Tcl oracle 差分重建
- 求解器本身（OptiStruct/ Radioss/LS-DYNA 计算）——只做前处理卡片与写出

---

## 3. 逐域分析

### 域 1 .hm 解析（读端）— 92% / L3+ / 主战层

**现状证据（oracle 三/四门禁全绿）**:
- 容器: 12B 前缀 + gzip 解压 + DB 版本（11.05/12.03/13.03/17.01）
- 节点: 5 布局（52B/92B-flat、56B-chain、68B v14+、96B v13），坐标 content 级 167 万节点
  对照仅剩 icw_ex1/2 链尾 33 坐标错；链式删除残留（@+44 跳号）字节可恢复
- 元素: A 型（CONST 锚多 eid 判别族）+ B 型（链式/槽位/u16 行）+ 专用变体
  （family-1 MPC cfg22/55、cfg56 五节点、cfg60 双节点、B 型 cfg55 MPC/cfg60 链）；
  count 门禁 elem-ok 123/123；strict content 91/91；非 strict 79/91
- 显示点 / 几何点: 可解码显示

**差距（余 8%）**:
- cfg55 MPC slave 列表的删除引用（11 文件 ~55 元素: truck 17/dummy 11/seat_deformer 11 等）
- seat_start family-1 cfg60 1 元素（3 节点 vs 2）
- icw_ex1/2 链尾 33 节点坐标乱值（链尾被元素区覆盖）
- count 门禁 node-ok 119/123 的 4 文件 ±1 已证为 oracle 源差异（新 harvest vs corpus_gt），非解码 bug

**边界项入册**: 上述 4 类均为「已知可修复边界」，非产品边界；另列未覆盖实体（见域 3/4）。

### 域 2 .hm 写端 — 0% / — / 差距区

- 现状: 无编码器；hmj（自研 JSON 工程）可往返，但 .hm 二进制未写
- 差距: 全量。反向编码器需覆盖 域 1 的节点/元素段 + 域 3/9 的 collector/卡片段
- 策略: 差分试错（写 → hmbatch 读 → oracle 计数/坐标一致）+ hwio.dll/hwiodriver.dll 字符串辅助
- 验收: round-trip 全等（decode→encode→decode 三同 + oracle 双对）

### 域 3 collector 实体解码 — 2% / L1 / 差距区

- 现状: 仅 oracle 可取名（oracle_harvest.tcl 已采 comps/mats/props 名称），字节段未定位
- 差距: Components/Materials/Properties/Load/System/Vector collectors/Sets/Groups/Titles 全解码
- 影响: Model Browser（官方文件夹树）、按 comp 着色、Entity Editor 可编辑的上限均由本域决定

### 域 4 几何实体解码 — 5% / L1 / 差距区

- 现状: display_points/geo_points 可显示
- 差距: lines/surfaces/solids BREP 未解码；Geom 页（points/lines/surfaces/solids 的 create/edit）深度上限 0
- 备注: 几何体量大，可先以「显示网格重建特征边」过渡（DEV_PLAN Phase 3）

### 域 5 面板体系（200 官方面板）— 35% / L1+ / 差距区

- 现状: 7 页 ~100 按钮（Geom/1D/2D/3D/Analysis/Tool/Post，页结构对齐官方）；
  14 个浅实现（nodes/node edit/temp nodes/distance/points/translate/numbers/find/
  renumber/count/mask/isolate/edit element/elem types）；其余 NYI（_nyi 统一灰显）
- 差距: 200 官方面板 catalog.json 未建（状态机缺失）；浅实现缺 collector/预览/子面板
- 权威蓝本: help/hm/topics/panels/help###.htm（逐面板按钮级规格）+ *.mac（宏页布局文本）

### 域 6 浏览器与工具栏（14+8）— 29% / L1 / 差距区

- 现状: Model（按 config 分组）/Mask/Utility 浅层；Standard + 显示/选择 2 工具栏
- 差距: 官方 14 浏览器（Model 官方文件夹树、Entity Editor 可编辑、Assembly/Part/
  Connector/Contact/Loadsteps/Solver 等）+ 8 工具栏可停靠/开关

### 域 7 Select/View/3D 可视化 — 40% / L2 / 差距区

- 现状: 单击拾取/Ctrl 多选/橡皮筋框选/按 ID；四种显示模式；按 config 分组着色；
  7 标准视图/Fit；三轴指示；Model Info 叠加
- 差距: 按 comp/prop/mat/quality 着色（依赖域 3）、厚度显示、element handles、
  多视口/窗体、截面/球面裁剪、隐藏线、透明度

### 域 8 工程文件管理与导入导出 — 40% / L2 / 差距区

- 现状: 打开 .hm/.hmj；保存 .hmj；导出 INP/STEP/IGES/CSV（面片级）
- 差距: 官方模板导出（对齐 lsdyna_writer/optistruct_writer）、CAD/FE 导入、Recent、
  User Profile、.mvw 会话、Print

### 域 9 求解与后处理生态 — 3% / — / 差距区

- 现状: Analysis/Post 页按钮全部 NYI
- 差距: 卡片解码（card image，hwtemplex.dll + templates 对照）；BC/载荷/loadsteps/
  loadcols/loadsteps/output blocks/control cards；Post（contour/deformed/vector/
  section cut/legend/animate，需 .h3d/.res 结果解码）

### 域 10 网格生成 — 3% / — / 差距区

- 现状: automesh/smooth/qualityindex/tetramesh/hex mesh/solid map 按钮全部 NYI
- 差距: 2D automesh（paving/advancing front）+ smooth + QI 修复；3D tetra/hex
- 口径（§2 非目标）: 不与官方策略等价；以「同几何产物质量量化对拍」验收；
  可选项: 调用 tetrameshdll.dll 导出接口（许可风险）

### 域 11 网格与几何编辑 — 30% / L1+ / 差距区

- 现状: 增/删节点与单元、单节点移动（translate 浅）、renumber、flip 法向、
  mask/isolate、undo/redo 命令栈
- 差距: Tool 页全量（rotate/reflect/scale/project/position/permute/organize）、
  2D split/combine/replace/order change、Check Elems/Quality Index（依赖网格质量）、
  几何编辑（Geom 页 create/edit）

### 域 12 宿主自动化（hmbatch oracle 差分）— 55% / L2+ / 主战层

**现状证据**:
- count 门禁: 123 文件 node-ok 119/elem-ok 123（corpus_gt.json + auto_compare.py）
- content 门禁: 91 文件逐元素 eid/config/节点（strict 91/91、非 strict 79/91，content_mp.py 多进程）
- 节点坐标门禁: 123 文件逐节点 id+xyz（nc_all.log 全量采集 + nc_compare.py），167 万节点
- 采集脚本: oracle_harvest.tcl / nc_all.tcl / elem_nodes.tcl 系列（6+ 套）
- 并行化: content_mp/gate_mp（多进程，~7min→~4min）

**差距（余 45%）**:
- 面板级 oracle（核心）: hmbatch 无头驱动官方面板（面板 Tcl API）录制「输入→模型变化」，
  作为我们面板实现的验收 —— 与 pphdecoding 的 COM/VBS e2e 同构，尚未建
- collector/几何/卡片实体的 oracle 采集脚本（随域 3/4/9 推进）

---

## 4. 差距汇总与主瓶颈

| 排序 | 瓶颈 | 阻塞的域 | 性质 |
|---|---|---|---|
| 1 | collector 实体未解码（域 3） | 5/6/7/9 深度上限 | 数据层 |
| 2 | 几何实体未解码（域 4） | 5/9/10/11 深度上限 | 数据层 |
| 3 | 写端缺失（域 2） | 全链路闭环 | 数据层 |
| 4 | 面板级 oracle 未建（域 12） | 全部面板深度验收 | 方法层 |
| 5 | 面板深度浅（域 5/6） | 用户工作流 | GUI 层 |
| 6 | 求解卡片/模板（域 9） | 分析工作流 | 数据层 |
| 7 | 网格生成（域 10） | 网格工作流 | 内核层（非目标级等价，对拍验收） |

**结论: 完整度 27.8% 中，深度上限由数据层决定 —— 与 v1 结论一致但更加量化。**
域 1/12 为主战层（格式读端 + oracle 流水线已成熟），其余 10 域随「先解码、再内核、
再面板深度、最后求解生态与写回」原则推进。

---

## 5. 多阶段开发规划（详见 DEV_PLAN.md）

8 个里程碑 M1-M8，每里程碑含: 目标域/目标完整度与深度/验收门禁/证据。

| 里程碑 | 内容 | 目标域 | 完整度轨迹 | 深度轨迹 |
|---|---|---|---|---|
| M1 基线 catalog + 面板级 oracle 骨架 | catalog.json 200 面板状态机；hmbatch 面板驱动脚本 | 5/6/12 | 28%→33% | L1 全量 |
| M2 网格编辑闭环 | Tool 页全量 + 选择过滤器 + QI 只读 | 7/11 | 33%→40% | L2 |
| M3 collector 解码 + 浏览器 | comps/mats/props/loads/systems 解码 + Model Browser 官方树 + 按 comp 着色 | 3/6/7 | 40%→48% | L2+ |
| M4 几何解码 + Geom 页 | points/lines/surfs/solids 解码 + Geom 页 create/edit 子集 | 4/11 | 48%→55% | L2 |
| M5 .hm 写端 | 反向编码器 + round-trip 全等 | 2/8 | 55%→62% | L2+ |
| M6 求解生态 | 卡片解码 + Analysis 页 BC/载荷/loadsteps + 官方模板导出 | 9/8 | 62%→70% | L2 |
| M7 网格生成 | 2D automesh/smooth + 3D tetra（产物对拍验收） | 10 | 70%→77% | L2 |
| M8 后处理收尾 | Post contour/deformed + 多视口/裁剪 | 9/7 | 77%→88% | L2+ |

最终态: 完整度 ~88%（余 12% 为边界项: 网格内核数值等价豁免 + 求解器广度裁剪，入册 NYI_INVENTORY.md），
深度 L2+ 全覆盖、域 1/12 L3+。
