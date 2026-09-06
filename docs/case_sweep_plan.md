# 四案例库遍历分析 + decoder / hm_gui 系统提升规划

日期: 2026-09 · 依据: 280 个 .hm 文件 decoder 全量解码 + hmbatch oracle 逐文件实体计数
(scripts/sweep4_*.py + output/sweep4_oracle.log + output/sweep4_decode.json)

---

## 1. 案例库概况

| 目录 | .hm 文件数 | 其它关键资产 | 体积 |
|---|---|---|---|
| tutorials/hm 官方案例 | 120 | .jt/.fem/.key (CAD 与求解输入) | 325 MB |
| demos/hm 官方 demo | 17 | 6 .res / 1 .h3d (后处理结果) | 13 MB |
| tutorials/hwsolvers 求解器案例 | 101 | 62 .fem / 10 .nas / 9 .rad / .h3d | 238 MB |
| D:/training/hypermesh 练习案例 | 42 | .tcl/.inp/.cdb/.pdf | 399 MB |
| 合计 | 280 | | ~1.1 GB |

### db 版本分布 (decoder 实测)

| db | 9.05 | 10.02 | 11.03 | 11.04 | 11.05 | 12.03 | 12.07 | 13.02 | 13.03 | 14.07 | 17.01 | 19.02 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 文件数 | 13 | 5 | 5 | 34 | 202 | 2 | 6 | 1 | 4 | 4 | 3 | 1 |

### 实体总量 (oracle, 280 文件)

| 实体 | 总量 | 含该实体文件数 | decoder 现状 |
|---|---|---|---|
| nodes | 4,390,128 | 244 | 已解 (部分版本缺) |
| elems | 5,159,696 | 239 | 已解 (部分版本缺) |
| loads | 35,786 | 86 | 0 |
| lines | 17,000 | 91 | 0 |
| points | 10,570 | 78 | 部分 (显示点/几何点) |
| surfs | 6,057 | 78 | 0 |
| sets | 1,680 | 67 | 0 |
| comps | 3,364 | 280 | 仅 ~53 文件 |
| props | 2,054 | 161 | 仅少数文件 |
| mats | 1,129 | 183 | 仅少数文件 |
| loadcols | 1,003 | 97 | 0 |
| systems | 526 | 29 | 0 |
| titles | 299 | 280 | 0 |
| groups | 146 | 26 | 仅 11 文件 |
| solids | 25 | 8 | 0 |

---

## 2. decoder 现状评分 (280 文件, 0 崩溃)

| 指标 | 现状 | 缺口 |
|---|---|---|
| 崩溃 | 0/280 | — |
| 节点完全命中 | 241/280 (86%) | 16 文件 dec=0 + 4 已知 oracle 源差异 |
| 单元完全命中 | 231/280 (83%) | 49 文件 |
| comps 名称+id | ~53/280 | 227 文件 dec=0 (第三格式未破) |
| mats / props / groups | 更少 | 154 / 129 / 15 不匹配 |

按 db 版本命中率:

| db | 文件 | node-ok | elem-ok |
|---|---|---|---|
| 9.05 | 13 | 13 | 7 (54%) |
| 10.02 | 5 | 5 | 5 |
| 11.03 | 5 | 5 | 5 |
| 11.04 | 34 | 31 (91%) | 22 (65%) |
| 11.05 | 202 | 183 (91%) | 169 (84%) |
| 12.03/12.07 | 8 | 8 | 5 (63%) |
| 13.02/13.03 | 5 | 4 | 4 |
| 14.07 | 4 | 1 (25%) | 2 |
| 17.01 | 3 | 2 | 2 |
| 19.02 | 1 | 0 | 0 |

---

## 3. decoder.py 功能提升点 (按优先级)

### P0-1 载荷解码: loads + loadcols (最大单一缺口)
- 证据: 35,786 个 loads / 1,003 个 loadcols, 覆盖 86/97 文件; 练习案例大量含载荷 workshop
  (WS_8.3: 4 loads + 6 loadcols)。
- 实测: WS_8.3_finish (db 11.05) 的 collector 记录**不是** [19][0][name_len] 格式,
  属第三格式 (与 truck 同族), 需先破第三格式段结构。
- 任务: 1) loadcol collector 段定位与解码; 2) load 实体记录解码 (FORCE/SPC/PRESSURE/
  MOMENT 卡片 + 节点/单元引用); 3) 载荷到 loadcol 的归属。
- 产出: model.loadcols (id->name), model.loads (id->type+card), 与 oracle
  (*createmark loads/loadcols) 逐文件对照门禁。

### P0-2 collector 格式泛化 (comps/mats/props/groups 全文件覆盖)
- 证据: 227 文件 comps dec=0。frame_assembly 家族已破 ([19][0][name_len] + id=u16(off-16)),
  但 truck/WS 等大模型用第三格式: 段头 [7277][0][count][0][X][0][char][0] 中 X=0/char='{',
  组件 id 达 9 位数 (u16 装不下, 需 u32/u64 或独立 id 表)。
- 任务: 1) 破解大 id 编码; 2) 段头 char 字段语义 ('C'/'{' 及 mat/prop 段的类型标记);
  3) 非标准命名 mat/prop 分类 (frame_assembly_3 的 mat 'CE_Locations_Dup' 现被误归 others)。
- 产出: comps/mats/props/groups 280 文件与 oracle 全对。

### P0-3 几何实体解码: lines / surfs / points / solids
- 证据: 17,000 lines / 6,057 surfs / 10,570 points / 25 solids, 覆盖 91/78/78/8 文件
  (几何类教程: 2_holes/Insert_planes/bottle/arm2D 等)。
- 任务: 1) 几何段定位与拓扑记录解码 (line 端点/类型, surf 边环/面类型, point 坐标,
  solid B-rep); 2) 与 oracle (*createmark points/lines/surfs/solids) 计数+拓扑对照。
- 产出: model.points/lines/surfs/solids, 供 GUI 线框/着色面渲染与 Geom 页面板 (M4)。

### P0-4 sets / systems / titles 解码
- 证据: sets 1,680 (67 文件) / systems 526 (29 文件) / titles 299 (280 文件)。
- 任务: 1) set 记录 (节点/单元成员列表); 2) 局部坐标系 (origin + axes); 3) 模型标题
  (纯文本, 最简单, 先做)。
- 产出: model.sets/systems/titles, 浏览器 Set/System 文件夹 + 标题栏显示。

### P1-1 高版本格式: db 14.07 / 17.01 / 19.02
- 证据: 14.07 节点命中仅 25% (WS_2.1_Geo/WS_6.1_bracket_cradle/Pretension),
  17.01 finite_sliding 节点 0, 19.02 abaqus3_0tutorial 全 0。
- 任务: 1) 逐文件 dump 头部 (19.02 头部已见计数块 01000000 03000000..., 与 11.x 异);
  2) 节点段/单元段结构差异定位; 3) db 19.02 单独格式分支。
- 产出: 这些文件节点/单元与 oracle 全对。

### P1-2 低版本格式: db 9.05 / 12.07
- 证据: 9.05 单元仅 54% (channel/bracket_size/bracket_transient 等 13 文件),
  12.07 单元 63% (bumper/fullcar/Radioss_Sample_Run)。
- 任务: 1) 9.05 元素记录布局差异 (B 型/变长族); 2) 12.07 与 12.03 的段差异。
- 产出: 9.05/12.07 单元 elem-ok 100%。

### P1-3 db 11.05 零节点变体
- 证据: 16 文件 dec=0 但 oracle 有节点: WS_4.2_morphing_2/WS_5.2_pipe/Half_car/
  plate_hole/bezel/channel 等 (多为 morphing/pipe 特征模型)。
- 任务: 对比这些文件与正常 11.05 文件的节点段头差异, 补节点段变体。
- 产出: 上述文件 node-ok。

### P2-1 卡片数据语义解码
- MAT/PROP 记录尾部 float 卡数据到 E/G/NU/RHO/厚度 等语义 (oracle 卡片导出对照)。

### P2-2 元素到 mat/prop 归属映射
- 元素记录中的 mat/prop 引用字段 (类似 M3.1 的 segid 到 comp)。

### P2-3 loads 卡片值解码
- FORCE 大小方向 / SPC DOF / PRESSURE 值 (随 P0-1)。

---

## 4. hm_gui.py 功能提升点 (依赖关系标注)

| # | 功能 | 依赖 | 现状 |
|---|---|---|---|
| G1 | Model Browser 接入 mats/props/groups 文件夹 | 已有数据 (db 11.x) | _collector_folders 有叶子图标, 数据未接 |
| G2 | 按 comp/mat/prop 着色 (M3.3) | G1 + 元素到 mat/prop (P2-2) | 色彩模式菜单有占位, 未驱动 VTK |
| G3 | loads/loadcols/sets/systems/titles 浏览器文件夹 | P0-1/P0-4 | NYI |
| G4 | 几何渲染: lines 线框 + surfs 着色面 + points | P0-3 | 仅节点/单元/显示点 |
| G5 | 载荷可视化 (FORCE 箭头 / SPC 标记 / PRESSURE 面) | P0-1 | NYI |
| G6 | Entity Editor 编辑 collector (名称/ID/颜色) | P0-2 | _on_tree_item_changed 仅 comp |
| G7 | 真实卡片浏览器 (替换 BDF 文本占位 NYI-M6-1) | P2-1 | 占位 |
| G8 | 后处理: .h3d/.res 读取 + contour (demos 有 6 .res) | 结果格式逆向 | 伪 contour 占位 (NYI-M8-1) |
| G9 | 案例库快捷入口 (4 目录树 + 最近文件) | 无 | 仅 File 打开 |
| G10 | 模型信息/标题显示 (titles) | P0-4 | 部分 |

实施顺序: G1 到 G2 (数据已有, 最快见效) -> P0-1+P0-2 (最大数据缺口) ->
P0-3+G4 (几何) -> P1 系列 (版本覆盖) -> P2+G7 (卡片) -> G5/G8。

---

## 5. 里程碑与验收门禁 (更新 DEV_PLAN M3 系)

| 里程碑 | 内容 | 门禁 |
|---|---|---|
| M3.2a | P0-2 collector 泛化 (第三格式) | comps/mats/props/groups 280 文件与 oracle 全对 |
| M3.2b | P0-1 loads/loadcols | loads/loadcols 计数+名称 86/97 文件全对 |
| M3.4a | P0-3 几何 + G4 渲染 | points/lines/surfs/solids 计数全对 + GUI 线面显示 |
| M3.4b | P0-4 sets/systems/titles + G3 | sets/systems 计数全对 + 浏览器文件夹 |
| M3.5 | P1-1/P1-2/P1-3 版本覆盖 | 节点/单元 280 文件命中 100% (除 oracle 源差异 4 文件) |
| M6a | P2-1/P2-2 + G2/G7 | 按 mat/prop 着色 + 卡片值 oracle 对照 |

回归门禁不变: count 123 文件快照 + 新增四目录 sweep 门禁 (scripts/sweep4_merge.py,
崩溃 0 + 各实体计数命中率单调不减)。

---

## 附: 关键证据文件
- scripts/sweep4_list.py / sweep4_decode.py / sweep4_oracle.tcl / sweep4_merge.py /
  sweep4_gaps.py / sweep4_oracle_stats.py / sweep4_probe2.py
- output/sweep4_files.txt / sweep4_oracle.log / sweep4_decode.json / sweep4_decode.log
