# hm_gui.py ↔ HyperMesh 2019 对标与 100% 开发规划（v2）

日期: 2026-09（v2 刷新）
对标对象: C:/Program Files/Altair/2019/hm/bin/win64/hmopengl.exe（oracle 批处理: 同目录 hmbatch.exe）
界面风格参考: D:/training/cgns/pphdecoding（PyQt5 + VTK，浅色 Fusion + 蓝标题条，导航面板/树/属性/绘制/消息五区）

权威清单:
- 工作区: help/hm/topics/chapter_heads/workspace_hm_classic_r.htm
- 面板总表: help/hm/topics/panels/panels_r.htm（200+ 官方 Panel，逐面板规格页 help/hm/topics/panels/help###.htm）
- 浏览器: help/hm/topics/user_interface/browsers_r.htm（14 个）
- 工具栏: help/hm/topics/user_interface/toolbars_r.htm（8 组）
- 教程入口: help/hm/topics/chapter_heads/tutorials_r.htm

当前代码: hm_gui.py（2565 行，8 区骨架）+ hmdecoder/decoder.py（核心差分逆向解码器）。

---

## 0. v2 刷新要点（相对 v1 的变化）

1. 解码器数据层大幅加深（详见 §2）：
   - 节点坐标 content 级对照落地：修复 xoff 错位（idoff==8 布局坐标在 @+20，此前读 @+12，约 150 万节点错误）与 find_node_section 假头误选（frame_assembly 丢 9971 节点）
   - 链式节点删除残留字节可恢复：56B 链 @+44 字段跳号 → 纠正为 prev_raw（SEAT_MODEL/seatbelt 10125 元素节点错 → 0，此前误判为运行时状态未持久化）
   - molding1 相邻节点段重叠去重（344 元素 → 0）
   - cfg60 固定 2 节点特判（3_step_proc_complete）
   - 元素内容级：strict 91/91、非 strict 79/91（剩 cfg55 MPC 11 文件约 55 元素 + seat_start cfg60 1 元素）
2. 新逆向资产发现（详见 §3）：hmmenu.set 二进制菜单、*.mac 文本面板定义、hm/scripts/ 3018 个 Tcl 面板实现、核心 DLL 清单（hmobj/hwio/hwtemplex/tetrameshdll 等）、嵌入式 Tcl/Python、逐面板 HTML 规格。
3. GUI 设计由按钮堆砌升级为「catalog 状态机 + schema 驱动面板引擎 + oracle 差分测试」（参考 pphdecoding 的 nav_panels/option_settings/e2e 结构）。

---

## 1. 总评

| 指标 | v1 | v2 | 含义 |
|---|---|---|---|
| 功能完整度 (Coverage) | 38% | ~42% | 官方 UI 条目在界面上有入口（含 NYI）的比例 |
| 深度实现 (Depth) | 14% | ~20% | 按官方行为加权后的真实能力（0=无, 1=与 HM 等价） |
| 可用对标完成度 | ~16% | ~22% | 用户能真正完成的 HM 工作流占比 |

深度提升主因：解码数据层（节点坐标/链式删除恢复/元素 91 文件内容全对）从能显示跨到数据可信；GUI 控件层面基本未动。

100% 对标不是改皮肤，而是补齐解码实体、几何/网格内核、collector/求解卡片，以及 .hm 写回。深度上限由数据层决定（§2）。

深度评分规则不变:

| 分 | 状态 |
|---|---|
| 0.00 | 缺失 |
| 0.10 | 仅按钮/菜单，点了报 NYI |
| 0.25 | 对话框或列表，只覆盖子面板的一小部分 |
| 0.40 | 核心子面板可用，缺 collector / 预览 / 多实体 |
| 0.60 | 主路径可用，缺边界与求解卡片 |
| 0.80 | 大部分子面板，缺 oracle 级细节 |
| 1.00 | 与 HM 2019 行为等价 |

---

## 2. 数据层现状（深度上限）

hmdecoder.HMModel 当前实体: nodes / elements / display_points / geo_points / db_version / node_count / elem_count。

| 数据能力 | 深度 | 现状与缺口 |
|---|---|---|
| 读 .hm 节点 | 92% | 52/92/56B-chain/68/96B 五布局；坐标 content 级 167 万节点对照仅剩 icw_ex1/2 链尾 33 坐标错；count 门禁 node-ok 119/123（4 文件 ±1 为 oracle 源差异，非解码 bug）；链式删除残留字节恢复 |
| 读 .hm 元素 | 93% | elem-ok 123/123；strict content 91/91（eid/config/节点全对）；非 strict 79/91。剩: cfg55 MPC slave 列表删除引用（11 文件约 55 元素，truck 17/dummy 11/seat_deformer 11 等）+ seat_start family-1 cfg60（1 元素） |
| 显示点 / 几何点 | 60% | 能显示，几乎不能编辑 |
| 组件 / 材料 / 属性 | 0% | 未解析 —— Model Browser 上限约 0 |
| loads / systems / vectors / groups / sets / titles | 0% | 未解析 —— Analysis 页上限约 0 |
| 几何 BREP（线/面/体） | 5% | 仅点；无线/面/体 |
| 求解卡片（card image） | 0% | 未解析（hwtemplex.dll + templates 在 HM 侧） |
| 写 .hm | 0% | 只读逆向；写回 = 反向编码器 |
| .hmj 工程 | 70% | 节点单元可往返 |
| 导出 INP/STEP/IGES/CSV | 40% | 面片级，非官方模板 |

结论: 14%→100% 的主瓶颈是未解码实体（collectors/几何/卡片），不是 GUI 控件数量。每补一个实体类，对应的官方面板/浏览器/工具栏才获得真实深度。

---

## 3. 逆向资产清单与利用策略（v2 新增）

HyperMesh 2019 安装目录提供四个层次的逆向素材，按可直接利用度排序：

### 3.1 权威文档（HTML，最易）
- help/hm/topics/panels/help###.htm：每个官方面板的按钮级规格（布局、输入、行为描述）——面板引擎的直接蓝本
- browsers_r.htm / toolbars_r.htm / tutorials_r.htm：浏览器/工具栏/工作流规格
- 策略: 爬取 → 生成 catalog.json（面板→按钮→语义），逐面板建状态机（missing/nyi/shallow/partial/done）

### 3.2 文本宏（Tcl，直接可读）
- hm/bin/win64/*.mac（hm.mac/globalpage/disppage/geommeshpage/qamodelpage/userpage）：*createbutton(page,标签,row,col,size,BUTTON,tooltip,handler) —— 官方页/按钮布局与工具提示的权威文本
- hm/scripts/ 3018 个 .tcl：宏菜单与求解工具的面板实现（abaqus/ansys/optistruct/radioss/UserProfiles/browser/connectors/... 60+ 目录）——可直接读懂官方交互逻辑
- 策略: 解析 .mac → 我们的页/按钮布局 100% 对齐官方宏菜单；Tcl 脚本作为面板行为规格

### 3.3 二进制（DLL/EXE，需工具）

| 资产 | 大小 | 作用 | 逆向方法 |
|---|---|---|---|
| hmmenu.set | 2.0MB | 菜单定义二进制（含 view/options/global/disp/card 等面板名与按钮串） | strings 提取 + 与 .mac 交叉对照，还原页↔按钮映射 |
| hmobj.dll | 139.6MB | 核心对象库（200 官方面板的 C++ 实现、实体数据库） | 导出表 + 字符串 + Ghidra 定位面板类；行为只能靠 Tcl oracle 差分验证 |
| hmopengl.exe | 139.7MB | 主 GUI（含 OpenGL 渲染） | 同上 |
| hwio.dll / hwiodriver.dll / FileExporter.dll / hm3dwriter.dll / h3dreader.dll / hwimport.dll | 各 0.1-0.5MB | .hm 读写与导入导出 | 差分逆向（当前主力）+ 字符串；写回格式在此层 |
| hwtemplex.dll + templates | 2.0MB | 求解卡片模板（card image） | 卡片解码必查 |
| tetrameshdll.dll | 11.5MB | 四面体网格内核 | 网格生成可调用/移植 |
| xtgraphics.dll | 9.6MB | 图形渲染 | 参考 |
| lsdyna_writer.dll / optistruct_writer.dll / radioss_writer.dll | ~0 | 求解器写出 | 导出对齐官方模板 |
| feconfig.cfg / stdbeamsections.cfg / hyperlaminate.cfg | ~0 | FE config 与梁截面表 | 直接读取 |
| tcl85t.dll / tk85t.dll / hwtclinterp.dll | — | HM 内嵌 Tcl/Tk 8.5 | Tcl 宏即为原生宏语言 |
| python35.dll / hwpybridge.dll / tclpython2x.dll | — | HM 内嵌 Python 3.5 桥 | 官方 Py 脚本可参考 |

### 3.4 Oracle（hmbatch.exe，行为权威）
- 已建立的差分流水线: hmbatch Tcl（*readfile/*createmark/hm_getvalue 等）导出逐实体真值 → 与解码器对照（count 门禁 123 文件、content 91 文件、节点坐标 167 万节点）
- 可扩展: 面板级 oracle —— 用 hmbatch 无头驱动官方面板录制「输入→模型变化」，作为我们面板实现的验收测试（对齐 pphdecoding 的 vbs/e2e 自动化思路）
- 采集脚本已有: oracle_harvest.tcl（实体计数/组件名）、nc_all.tcl（节点坐标全量）、elem_nodes.tcl 系列（元素列表）

---

## 4. GUI 全面设计（对标 100%）

技术栈（与现状/参考一致）: PyQt5 + VTK 9；浅色 Fusion 风格 + 蓝色标题条（照 pphdecoding）。

### 4.1 工作区 8 区（现有骨架 → 100%）

| # | 区域 | 现状 | 100% 目标 |
|---|---|---|---|
| 1 | Title Bar | 70% | 用户配置名、会话 .mvw、多 client |
| 2 | Menu Bar | 60% | 17 顶栏完整子菜单、灰显/快捷键、Find Tools |
| 3 | Toolbars | 25% | 8 组可停靠 + View>Toolbars 开关（布局对齐 .mac/官方截图） |
| 4 | Tab Area | 40% | 14 浏览器全部可作 Tab（Model/Mask/Utility 先行） |
| 5 | Modeling Window | 65% | 多视口、窗体、球面裁剪、透明度、按 comp/prop/mat/quality 着色、厚度 |
| 6 | Entity Editor | 25% | 可写字段、求解卡片、多选批量、验证 |
| 7 | Panel Area | 45% | 子面板、return/reject、collector 选择器、7 页全量按钮 |
| 8 | Status Bar | 70% | 面板说明、当前 collector、进度 |

### 4.2 面板引擎（核心工程）

1. catalog.json 状态机（机器可读）：
   - 来源合并: panels_r.htm/help###.htm（规格）+ .mac（宏页按钮）+ hmmenu.set 字符串（交叉校验）
   - 每面板记录: 官方名/页/按钮列表/输入类型/状态（missing|nyi|shallow|partial|done）/深度分
   - 面板入口覆盖率可自动回归测试（防入口回退）
2. schema 驱动面板（照 pphdecoding 的 nav_panels.py + option_settings.py 模式）：
   - 面板 = schema（字段类型: 实体选择器/数值/下拉/开关）+ 布局模板 + 命令绑定
   - 实体选择器 = collector 组件（支持 nodes/elems/comps/lines/surfs/solids/loadcols 多实体、扩展选择、by id/window/config/displayed）
   - return/reject/redo 面板切换栈与 HM 一致
3. 命令栈: 所有编辑走命令模式（undo/redo），面板操作可回放（为 e2e 测试服务）
4. 宏菜单: 解析 .mac 直接生成官方 Macro 页（Disp/QA-Model/Geom-Mesh/User），tooltip 与官方一致

### 4.3 浏览器（14 → 分层实现）

- 第一梯队（有数据即可）: Model Browser（官方文件夹: Assemblies/Components/Materials/Properties/Sets/Groups/Load/System/Vector cols）、Entity Editor（可编辑）、Mask、Utility
- 第二梯队（解码后）: Assembly/Part/Connector/Contact/Loadsteps/Solver/Reference/Entity State
- 第三梯队: Mass Trimming/Matrix（后处理）

### 4.4 菜单/工具栏/面板分域目标（与 v1 表合并执行）

- File: 写 .hm（Phase 5）、Import CAD/FE、Recent、User Profile
- Geom/Mesh/Analysis 页: 按钮铺齐（catalog 全量），深度跟随数据层（§2）
- Collectors: comps/mats/props/loads/systems 创建/编辑/当前 collector
- 可视化: by comp/prop/mat/quality 着色、厚度、element handles、HID、多视口
- 选择: 拾取/框选/by collector/by config/displayed、隐藏线

### 4.5 测试与回归（照 pphdecoding e2e）

- scripts/gui_pick_final.py 冒烟保持 ALL PASS
- 面板级 oracle 差分: hmbatch 驱动官方面板（Tcl）→ 记录模型变化 → 断言我们的面板等价
- 解码门禁: count 123/123、content strict 91/91、非 strict 79/91（目标 91/91）、节点坐标 167 万

---

## 5. 到 100% 的分期路线图

原则: 先解码、再内核、再面板深度、最后求解生态与写回。GUI 按钮可提前铺齐（完整度），深度必须跟数据走。

### Phase 0 — 基线冻结与 catalog（1–2 周）· 目标深度 ~22%
- 本文件为范围基线；爬 help###.htm + 解析 .mac + hmmenu.set strings → 生成 hm_gui/catalog.json
- 入口自动回归测试（菜单/按钮清单，防回退）
- 完成定义: 200+ 面板 + 宏页按钮的机器可读状态表（含深度分）

### Phase 1 — 网格编辑工具闭环（6–8 周）· 目标深度 ~30%
- Tool 页做实: Translate/Rotate/Reflect/Scale/Project/Position/Permute（多实体、预览、命令栈）
- Organize（改 config/伪组件）、Delete 面板、Detach、Replace、Split/Combine（2D）
- Numbers（屏幕 ID）、Find（节点↔单元）、Count 官方分类、Edges/Faces/Features 查询
- Check Elems + Quality Index 只读（长宽比/歪斜/雅可比）
- Normals/Reverse；选择过滤器（by config/by ID/displayed）
- 完成定义: 对 WS_3.2 完成「选-变-查-删-撤销」全流程不开 HyperMesh

### Phase 2 — collector 解码与浏览器（8–12 周）· 目标深度 ~42%
- 解码 Component/Material/Property/Load/System/Vector/Set/Title 段（对 hmbatch Tcl oracle）
- Model Browser 官方文件夹 + 勾选显隐 + 右键 Create/Edit/Card
- Entity Editor 可编辑（名称/ID/颜色），组件颜色驱动 VTK
- Visualization: color by component/config
- 收尾 cfg55 MPC 非 strict（79→91/91）
- 完成定义: 教程模型的组件数/名称与 HM Model Browser 一致（oracle 对照脚本）

### Phase 3 — 几何显示与 Geom 页（10–14 周）· 目标深度 ~55%
- 解码 points/lines/surfaces/solids（或从显示网格重建特征边）
- Geom 页: nodes(on geom)/points/lines/surfaces/solids 的 create/edit 子集
- Distance/Length/Mass Calc 对几何+网格
- 完成定义: 打开含几何教程模型，Geom 页与 HM 显示一致

### Phase 4 — 求解生态（12–16 周）· 目标深度 ~70%
- 卡片解码（hwtemplex 对照 + templates）: card image、config edit
- Analysis 页: constraints/forces/moments/pressures/temperatures/velocities/accelerations + loadcols/systems/loadsteps/output blocks/control cards
- Solver Browser/Loadsteps Browser
- 导出对齐官方 writer（INP/K 用官方模板）
- 完成定义: 建一个带 BC/载荷/卡片的小模型，导出文件与 HM 官方模板 diff 通过

### Phase 5 — .hm 写回（8–12 周）· 目标深度 ~80%
- 反向编码器: nodes/elements/collectors/cards 段写回（差分验证: 写→hmbatch 读→oracle 计数一致）
- round-trip 测试: decode→encode→decode 全等
- 完成定义: 任意教程模型 decode→改一处→encode，hmbatch 打开后 oracle 计数/坐标全对

### Phase 6 — 网格生成（16–24 周）· 目标深度 ~88%
- 2D automesh（advancing front/paving 自研或移植）、smooth、QI 修复
- 3D tetramesh（自研或调用 tetrameshdll.dll 导出接口）、hex/solid map
- Shrink wrap、midsurface 派生
- 完成定义: 对几何面生成与 HM 同量级质量的 2D/3D 网格

### Phase 7 — 后处理与收尾（8–12 周）· 目标深度 ~100%
- Post 页: contour/deformed/vector/isosurfaces/section cut/legend/animate（需结果文件解码: .h3d/.res）
- XYPlots、多视口、裁剪、隐藏线
- Morphing/Connectors 按教程收尾
- 完成定义: 打开结果文件完成 contour 工作流

---

## 6. 指标追踪（每阶段汇报）

| 门禁 | 基线(v2) | 目标 |
|---|---|---|
| count 门禁（123 文件） | node 119/123 · elem 123/123 | node 123/123 |
| 元素内容级 strict | 91/91 | 91/91（不回退） |
| 元素内容级非 strict | 79/91 | 91/91（Phase 2 收尾） |
| 节点坐标 content | 167 万节点，剩 icw 尾 33 | 全对 |
| catalog 面板状态 | 待建 | 200+ 面板全建 + 深度分 |
| 写回 round-trip | 0% | Phase 5 100% |

## 7. 风险与依赖

1. 核心 200 面板行为在 hmobj.dll（C++ 二进制）——无源码；行为规格只能靠 help HTML + Tcl oracle 差分重建，深度 1.0 的验收成本高（每面板需 oracle 场景）。
2. 网格生成算法体量大（automesh/tetra 是工业级内核）——自研只能达可用级，1.0 等价需大量调参或调用官方 DLL（许可风险）。
3. 卡片/模板生态广（每求解器一套 templates）——Phase 4 需按求解器优先级裁剪（Abaqus/OptiStruct 先行）。
4. 写回格式未验证——目前只验证过读；写回需从 hwio 层逆向或差分试错。
5. 人力: 每 Phase 的完成定义以 oracle 对照脚本为准，不以主观感受为准。

---

附: v1 的逐面板/逐菜单/逐工具栏明细表继续有效（菜单 17 顶栏、8 工具栏、14 浏览器、200 面板的按钮级现状见 v1 §4-§7），本 v2 以其为清单基础，不再重复罗列。
