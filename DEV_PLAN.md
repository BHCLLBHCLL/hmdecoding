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

12 维度功能完整度与深度分析见 docs/gap_analysis.md（双口径实测: 完整度% + 深度 L1-L4，整体 27.8%，主战层 = 读端 + oracle 流水线）。

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
| 组件 / 材料 / 属性 | 20%（db 11.x 局部） | db 11.x 已解码（M3.2）: comp/mat/prop/group 名称+精确 id（含删除跳号）,
  记录 [u32 19][u32 0][u32 name_len] + 名称, id=u32(off-16); truck 大 id 第三种格式已破（段头 char='{', 名称允许 TAB 填充）,
  非标准命名 mat/prop（CE_Locations_Dup）仍漏归类（前缀启发式），Sets 记录已扫入 others 未分列 |
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

## 5. 到 100% 的详细多阶段开发规划（M1–M8，12 域对齐）

原则: 先解码、再内核、再面板深度、最后求解生态与写回。GUI 按钮可提前铺齐（完整度），深度必须跟数据走。
每个里程碑含: 目标域/任务清单/验收门禁（证据）/预估周期。完整度与深度轨迹引自 docs/gap_analysis.md §5。

### M1 — 基线 catalog + 面板级 oracle 骨架（2 周）· 域 5/6/12 · 完整度 28%→33%

- [ ] 1.1 爬 help/hm/topics/panels/help###.htm（200+ 面板按钮级规格）→ 生成 hm_gui/catalog.json（面板名/页/按钮/输入类型/状态: missing|nyi|shallow|partial|done）
- [ ] 1.2 解析 hm/bin/win64/*.mac（*createbutton 文本）→ 宏菜单页/按钮/工具提示入 catalog
- [ ] 1.3 hmmenu.set strings 提取 → 与 catalog 交叉校验（页↔按钮映射）
- [ ] 1.4 入口自动回归测试: 遍历 catalog 断言每按钮有接线或灰显 NYI（防入口回退），并入 gui_pick_final 冒烟
- [ ] 1.5 面板级 oracle 骨架: hmbatch Tcl 无头驱动 3 个示范面板（nodes/translate/renumber），录制「输入→模型变化」快照（脚本 scripts/panel_oracle.tcl + 比对器）
- 验收门禁: catalog.json 覆盖 200+ 面板与 5 宏页；冒烟 ALL PASS；3 面板 oracle 快照可重放

### M2 — 网格编辑工具闭环（6 周）· 域 7/11 · 完整度 33%→40% · 深度 L2

- [ ] 2.1 Tool 页全量: rotate/reflect/scale/project/position/permute（多实体、N1/N2 预览、命令栈可撤销）
- [ ] 2.2 organize（改 config/伪组件）、delete 面板（by id/window/collector）、detach、replace
- [ ] 2.3 2D 编辑: split/combine/order change（四/三边形）
- [ ] 2.4 numbers（屏幕 ID 标注）、find（节点↔单元关联）、count 官方分类、edges/faces/features 查询
- [ ] 2.5 质量只读: check elems + qualityindex（长宽比/歪斜/雅可比/翘曲），报告进 Entity Editor
- [ ] 2.6 选择过滤器: by config/by ID range/displayed only + 隐藏线拾取
- 验收门禁: WS_3.2 全流程「选-变-查-删-撤销」不开 HyperMesh 完成；每面板 M1.5 的 oracle 快照比对 PASS

### M3 — collector 解码与浏览器（10 周）· 域 3/6/7 · 完整度 40%→48% · 深度 L2+

- [x] 3.1(部分) 解码 collector 段: db 11.x comp/mat/prop/group 名称+精确 id（M3.2 落地, bb8ae7e; truck 大 id 第三格式已破, id=u32(off-16) + TAB 填充名称, comps 313/313 on oracle）; load/system/vector 待分类（XtraNodes type 516/517 暂归 others）
- [ ] 3.1 卡片引用/颜色解码（MAT/PROP 记录尾部 float 卡数据, 未对齐语义未解）
- [x] 3.2(部分) 解码 Groups（C_Spotweld_1, type=1538 记录）；元素↔组件归属映射=M3.1 segid 已落地；Sets/Titles 待破
- [x] 3.3 Model Browser 官方文件夹树（Assemblies/Components/Materials/Properties/Sets/Groups/Load/System/Vector）+ 组件勾选显隐（渲染按 comp 分组, comps 全量含无元素） + 右键 Create/Edit/Card（内存级; Card 为占位对话框, 卡数据 M6.1 未解码; System/Vector 空文件夹占位）
- [x] 3.3(门禁) HM 侧逐文件夹 oracle 对照（scripts/m33_folder_oracle.py + m33_gate_check.py, hmbatch 探针）: FA1 7/7 文件夹全对（comps 17/mats 5/props 5/groups 1/sets 2/load 0/asm 5）; truck comps 313/313、groups 2/2、sets 587/587、loadcols 2/2+2 残影; FA3 comps 27/27、props 13/13、sets 2/2、asm 5/5, 仅 mats 13/14（mat 12 CE_Locations_Dup 非 M_ 前缀, type 字段未破）。收获: others 改 list 防跨类型 id 覆盖（HM 各类型 id 空间独立, 曾丢 assem_1/2/Model Info/Set_2000002-9）; XtraNodes type516 37 条为删除残影（活/残字节级无差异, 纯解析不可分）。未解码家族: connectors 178 (FA3)、blocks 2、curves 19、tags 3、titles 1 (truck/FA)
- [ ] 3.4 Entity Editor 可编辑（名称/ID/颜色）；组件颜色驱动 VTK
- [ ] 3.5 可视化: color by component/config；toolbar Collectors 组（当前 comp/mat/prop/loadcol）
- [ ] 3.6 收尾元素解码边界: cfg55 MPC 非 strict 79→91/91、seat_start cfg60、icw 链尾 33 坐标
- 验收门禁: 教程模型组件数/名称与 HM Model Browser oracle 对照一致；非 strict content 91/91；节点坐标全对

### M4 — 几何解码与 Geom 页（10 周）· 域 4/11 · 完整度 48%→55% · 深度 L2

- [ ] 4.1 解码几何实体: points/lines/surfaces/solids（段结构 + oracle 计数/拓扑对照）
- [ ] 4.2 几何可视化: 线框/着色面/边特征显示；与网格叠加显隐
- [ ] 4.3 Geom 页 create 子集: nodes(on geometry)/points/lines（两节点/on surface）/circles/arcs
- [ ] 4.4 Geom 页 edit 子集: line edit（combine/split/trim 基础）、point edit、edge edit
- [ ] 4.5 distance/length/mass calc 对几何+网格
- 验收门禁: 含几何教程模型（bottle/arm2D 等）解码几何与 HM 计数一致；Geom 页创建线/面并导出 STEP 重开验证

### M5 — .hm 写端（10 周）· 域 2/8 · 完整度 55%→62% · 深度 L2+

- [ ] 5.1 反向编码器最小集: 节点段（5 布局）+ 元素段（A/B 型）写回
- [ ] 5.2 差分验证环: 写 → hmbatch 读 → oracle 计数/坐标/元素内容一致（count+content+coords 三门禁复用）
- [ ] 5.3 collector/几何段写回（随 M3/M4 结构）
- [ ] 5.4 round-trip 测试: decode→encode→decode 三同（任意 123 文件样本）
- [ ] 5.5 编辑保存链路: GUI 改一处（移动节点/改组件）→ 存 .hm → hmbatch 重开验证
- 验收门禁: 20 个代表文件 round-trip 全等；三门禁写后 PASS

### M6 — 求解生态（12 周）· 域 9/8 · 完整度 62%→70% · 深度 L2

- [ ] 6.1 卡片解码: card image（hwtemplex.dll + templates 对照）: PSHELL/PSOLID/MAT1/CQUAD4 等先 4 张
- [ ] 6.2 Analysis 页: constraints/forces/moments/pressures/temperatures/velocities/accelerations + loadcols/systems/loadsteps/output blocks/control cards
- [ ] 6.3 Solver Browser + Loadsteps Browser
- [ ] 6.4 导出对齐官方模板: INP（Abaqus）先一个求解器，diff 官方 lsdyna/optistruct writer 的输出风格
- 验收门禁: 建带 BC/载荷/卡片的小模型，导出 INP 与 HM 导出逐行 diff（关键卡片）通过

### M7 — 网格生成（14 周）· 域 10 · 完整度 70%→77% · 深度 L2（产物对拍口径）

- [ ] 7.1 2D automesh: paving/advancing front 自研基础版 + 尺寸/偏置控制
- [ ] 7.2 smooth（Laplacian 基础）+ QI 修复（长宽比/歪斜局部翻边）
- [ ] 7.3 3D tetramesh: Delaunay + 质量优化基础版（或调用 tetrameshdll.dll 导出接口，许可风险备选）
- [ ] 7.4 hex/solid map 基础（映射法拉伸）
- [ ] 7.5 产物量化对拍: 同几何同尺寸下与 HM 产物比较单元数/质量分布直方图（对拍报告脚本）
- 验收门禁: 对 bottle/arm2D 几何生成网格，质量分布与 HM 同量级（非数值等价，见 gap_analysis §2 口径）

### M8 — 后处理与收尾（8 周）· 域 9/7 · 完整度 77%→88% · 深度 L2+

- [ ] 8.1 结果解码: .h3d/.res（先位移/应力两个场量）
- [ ] 8.2 Post 页: contour/deformed/vector/isosurfaces/section cut/legend/animate
- [ ] 8.3 XYPlots: curves/plots（时间历程）
- [ ] 8.4 多视口/窗体/球面裁剪/隐藏线（域 7 收尾）
- [ ] 8.5 Morphing/Connectors 按教程收尾（浅层）
- 验收门禁: 打开 HM 导出的结果文件完成 contour 工作流，与 HM Post 同工程截图对照

**最终态: 完整度 ~88%（余 12% = 边界项: 网格内核数值等价豁免 + 求解器广度裁剪，入册 docs/NYI_INVENTORY.md），深度 L2+ 全覆盖、域 1/12 达 L3+。**

---

## 6. 指标追踪（每里程碑汇报，12 域口径）

完整度/深度逐域轨迹见 docs/gap_analysis.md §0/§3；里程碑门禁:

| 门禁 | 基线 | M3 | M5 | M8 |
|---|---|---|---|---|
| 12 域完整度均分 | 27.8% | 48% | 62% | 88% |
| count 门禁（123 文件） | node 119/123 · elem 123/123 | 不变 | 写后 PASS | 写后 PASS |
| 元素内容级 strict | 91/91 | 91/91 | 91/91 | 91/91 |
| 元素内容级非 strict | 79/91 | 91/91（M3.6） | 91/91 | 91/91 |
| 节点坐标 content | 剩 icw 尾 33 | 全对（M3.6） | 全对 | 全对 |
| catalog 面板状态 | 待建 | 200+ 全建 | 全建+深度分 | 全建+深度分 |
| 面板级 oracle | 未建 | 全量接线（M3 起） | 全量 | 全量 |
| 写回 round-trip | 0% | — | 20 文件全等 | 全等 |

## 7. 风险与依赖

1. 核心 200 面板行为在 hmobj.dll（C++ 二进制）——无源码；行为规格只能靠 help HTML + Tcl oracle 差分重建，深度 1.0 的验收成本高（每面板需 oracle 场景）。
2. 网格生成算法体量大（automesh/tetra 是工业级内核）——自研只能达可用级；与官方数值等价不在目标内（gap_analysis §2 口径: 产物量化对拍）。
3. 卡片/模板生态广（每求解器一套 templates）——M6 按求解器优先级裁剪（Abaqus 先行）。
4. 写回格式未验证——目前只验证过读；写回需从 hwio 层逆向或差分试错。
5. 人力: 每里程碑的验收门禁以 oracle 对照脚本为准，不以主观感受为准。
6. 边界项（求解器广度、CATIA 类导入、网格内核数值等价豁免）统一入册 docs/NYI_INVENTORY.md，随里程碑扫描再生，不丢账。

---

附: v1 的逐面板/逐菜单/逐工具栏明细表继续有效（菜单 17 顶栏、8 工具栏、14 浏览器、200 面板的按钮级现状见 v1 §4-§7），本 v2 以其为清单基础，不再重复罗列。
