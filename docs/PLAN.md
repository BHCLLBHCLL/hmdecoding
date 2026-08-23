# HyperMesh .hm 格式解码 — 现状完整性/深度分析与开放开发计划

> 更新日期：本会话（v2，含 tutorials/hm 语料库分析）
> 关键新信息：(1) HyperMesh 2019 安装可用（'C:\Program Files\Altair\2019\hm\bin\win64\hmopengl.exe' + hmbatch.exe + Tcl API，license 实测可用）；(2) .hm 是压缩包，解压后为二进制数据库；(3) 教程语料库 'C:\Program Files\Altair\2019\tutorials\hm' 含 **122 个真实 .hm/.hm10 文件**，全部可用 oracle 打开。

---

## 一、现状分析：完整性与深度

### 1. 仓库资产盘点

| 文件 | 角色 | 状态评估 |
|---|---|---|
| scripts/hm_reverse_parse.py | 容器级反向解析（gzip 定位、前缀、文本记录、命名块） | ✅ 诚实、结构化、结论可复现，是唯一可靠部分 |
| hm_parser.py / hm_parser_v2.py | 启发式节点/单元提取（4 字节滑动窗口暴力猜数） | ❌ 方法学上不可行：输出全部是误报/伪造，无保真度 |
| output/, output_v2/, final_output/ | 声称的 INP/STEP/技术文档产物 | ⚠️ 手工伪造子集（每类 5 个单元、编造 ID），不能代表解析能力 |
| README.md | 容器层发现记录 | ✅ 与取证一致，但未覆盖记录层/实体层 |
| WS_3.2_3d_tetra_finish.hm（LFS） | 唯一真实样本 | 语料库=1 → 已由教程库补足（见第二节） |
| corpus/corpus_index.json（新增） | 122 文件语料索引（版本/布局/大小） | ✅ 本轮生成 |

### 2. 分层深度评估（L1–L5）

| 层 | 定义 | 现状 | 置信度 |
|---|---|---|---|
| L1 容器层 | 文件头/压缩/解压 | ✅ 基本解决且**全库证实**：122/122 文件均为 12 字节前缀（u32 0 + double 5.0）+ 单一 gzip member @0x0c；.hm10 同容器 | 高 |
| L2 记录/属性层 | 载荷内记录帧、tag、属性表 | 线索显著增加：载荷头 u32 0 + double 版本号 + u32 126 + u32 1 + u32 262144；命名块模式 [cap=19][u32 0][class_id][name] 在 3 个文件 16 处重现（class_id ∈ 5,6,7,8,10,11,12,13,17）；尾部常量 0x3e6(998)/0x3e7(999)/0x9b(155)；长度前缀 ASCII 记录（tag 0x40000065/66）目前仅存于仓库样本 | 中低 |
| L3 实体/模型层 | 节点/单元/组件/几何的真实记录结构 | 空白：无任何记录帧格式认知；现有 parser 靠滑动窗口猜 [id,x,y,z] 模式 | 无 |
| L4 验证层 | 与 ground truth 比对 | 起步：已有 3 个文件的 oracle 计数（见下），比对器未建 | 低 |
| L5 工程化 | 语料库、测试、格式文档 | 弱→改善中：语料索引已建，测试/文档仍缺 | — |

### 3. 量化结论：当前实现 vs 真实数据（oracle 实测）

| 文件 | oracle 真实数量 | 现有解析器产出 | 覆盖率 |
|---|---|---|---|
| WS_3.2_3d_tetra_finish.hm | nodes 6,408 / elements 31,843（config 103）/ comps 2（id 240 base、241 tetras）/ props 1 / points 157 / lines 354 / surfaces 93 | ~40 节点 / ~62 单元（伪造 ID） | ≈0 |
| tutorials 1d_elements.hm | nodes 443 / elements 400（config 104）/ comps 4 / mats 3 / props 2 / points 4 / lines 8 / surfaces 1 | 未跑 | — |
| tutorials leg_geom.hm | nodes 4 / elements 0 / comps 1（auto1）/ lines 3 | 未跑 | — |

深度结论：当前实现停留在「容器级事实 + 猜测性模式匹配」；模型级解码尚未真正开始。hm_reverse_parse.py 的命名块推断被 oracle 证实（base/tetras = 2 个 comps），该路线值得作为解码支点。

---

## 二、教程语料库盘点（tutorials/hm，122 文件，本轮新分析）

### 1. 容器一致性
- **122/122 文件**均为同一容器：前缀 u32 0 + double 5.0（12 字节）+ gzip member @0x0c；
- 含 2 个 .hm10 文件（3_step_proc.hm10 等），容器与 .hm 相同；
- gzip 头 flags=0x00、OS=0x0b（NTFS），单 member，未见多 member 场景。

### 2. DB 版本谱系（载荷头 double @0x04）

| DB 版本 | 文件数 | 备注 |
|---|---|---|
| 10.02 | 2 | 最旧（fe_to_surf.hm、floor.hm） |
| 11.03 / 11.04 / **11.05** | 5 / 3 / **100** | 主流版本，本仓库样本即 11.05 |
| 12.03 / 12.07 | 2 / 3 | 头部布局变化（w14=10000, w1c=20） |
| 13.02 / 13.03 | 1 / 3 | 同 v12 布局 |
| 14.07 | 1 | 新布局（w14=1, w3c=1536） |
| 17.01 | 2 | 最新（dummy_positioner.hm、seat_deformer.hm） |

---

## 三、2026-08 深入解析成果（遍历安装目录手册/案例后）

### 1. 帮助文档与脚本挖掘结论
- help/hm 1063 页: 实体参考 (entities_r 等) 为概念性描述, 无 .hm 二进制格式文档; interfacing 无 hmascii 格式说明; Tcl API 文档不在 help 内;
- hm/scripts 13,641 个 .tcl: hm_registertooltipforentitydataname 9,971 处注册 (实体 dataname 字典, 已提取至 output/ground_truth/dataname_regs.txt); hm_getentityvalue 13,685 处用法;
- 结论: .hm 二进制格式无官方文档, 只能靠 oracle 对照 + 字节取证 (本轮完成大量此类工作).

### 2. 本轮解码突破 (decoder v5+)
- **元素段统一模型**: 段头 [997][seg][175][count][X][Y]; A 型 (X=3, CONST 锚 0x70??1FF5 家族) / B 型 (X=2, 链式 eid); v12-13 u16 槽位型 (58B, CONST12 0x70501FF5); B 型 u16 槽位型 (34B, crash_tubes); 元素分块存储 + 断链重连;
- **节点段统一模型**: [136] 头 (非对齐, 字节模式定位); 52B-flat [id][0][0][x][y][z][0x4] / 92B-flat (+40B 附加) / 56B-chain (v13, [x][y][z][0x4][id+1][0][0]) / 68B (v14+/17.01, [id][0][1][x][y][z][0x8]);
- **行号语义**: 元素节点引用 = 节点表行号 (1-based), 需 row_map 映射;
- **oracle 对照覆盖率**: node-ok 101/123, elem-ok 83/123 (原 66/98, 6/98);
- 关键验证: WS 6408+31843, 1d 443+400+535, body_side 7510+7182, truck 212139+204762, SEAT_MODEL 34295+27503, car_section 26697+27854, dummy_positioner (17.01) 354176+586202, seat_deformer (17.01) 354174+586202.

### 3. 待解项 (后续轮次)
- ~~v17 文件 (dummy_positioner/seat_deformer) 节点分块 (116734/354176) 与元素全量 (44062/586202)~~ ✅ **本轮解决**（见下）
- truck 2000001+ 段为非元素段 (oracle 证实 eid 不存在, face/显示网格段), 需排除逻辑;
- 0D/特殊元素段 (joints seg3 等, config<100);
- chapter2_2 (13.03) 节点布局未解;
- 元素记录内 A/B/C 附加字段语义 (0x1a040be4/0x0a040be6/0x12040084 等, 疑为属性/显示数据).

### 4. v17 解码突破（本轮完成，2026-08）
- **节点**: 68B/92B 节点段 + 小簇补扫 (k=0) + 相邻段重叠修正 (过扫 1 条截断)。
  - dummy_positioner: 354176/354176 ✓; seat_deformer: 354174/354174 ✓ (均与 oracle 全等, 0 缺失 0 多余)
- **元素**: family-1 核心记录全局扫描 (701|686)+2596 模式 + 特殊元素段 (Y≠2 段) 解析。
  - family-1 core: 585843 (eid@标记+8, flag@+18, rows@+22)
  - 特殊元素 359 个 (config 1/3/21/22/55/61): 记录 [eid][0][k][tag u16] + 行号;
    config 55 行号 = (下一 u32 低16位<<16)|当前 u32 高16位 (节点数=n+1);
    其余 (config 1 单节点 / 3/21/22/61 每节点 (lo u16, hi u16) 对, lo=0 结束);
    tag 映射: 257→1, 259→3, 277→21, 278/534/790/1558→22, 567→55, 317→61
  - 总计: dummy 586202/586202 ✓, seat 586202/586202 ✓ (0 缺失 0 多余)
- **row_map 修正**: 相邻段 (68B→92B→小段) 互相过扫 1 条致幻影行 → 按段基址截断;
  小段记录 k=0 被流扫描拒绝 → mod-4=3 网格 + 零4 定位补扫
- 一致性: 元素节点引用 0 无效, 节点 0 重复; 特殊元素 359 个节点+config 全匹配 oracle

### 5. 语料全量比对（Phase 4 自动比对器，2026-08 本轮完成）
- **auto_compare.py**: decode 全语料 vs corpus_gt.json 逐文件计数比对, 输出覆盖率报告;
- **全量结果 (122 文件, 0 崩溃)**: node exact 108/122, elem exact 91/122 (原 101/123, 83/123);
- **本轮修复**:
  - find_node_section 阈值按 count 缩放 → 极小型 v11 文件 (count<45) 节点解码修复;
  - A 型低 config 段 (config 1/2 plotel): [CONST][eid][1|k<<16][0][0][(cfg+256)<<16][行号...];
  - B 型 u16 行号段 (config 60): [0][0][flag][(row,0) u16 对], 新增 _parse_b_u16rows;
  - Y=3 几何复合记录 (config 104): 0x1a040be4 头 + eid@+36 + 节点行号 u32@+48+4i 高16位, 新增 _parse_a_geom (wing_section 1→149);
  - decode() 版本分流: v14+ 走 family-1+special, v11-13 走分段解析 (修复 v11 元素全丢 bug);
- **剩余主要缺口**: molding1 (elems 344/14558, 节点 7191/7279), truck (204762/212489, face 段), wing_section_complete (149/1001, 复合记录变体), frame_assembly_3/4 (miss 1365/848), car_section (miss 626), chapter2_2 (v13 节点布局), geometry.hm (0/4116), icw_ex1/2 (节点少 12/23).

### 6. P0 优先修复（2026-08 本轮）
- **truck family-1 布局**: _parse_a_type 检测 701/686+2596 标记 (仅 @+4 存储 ID >= 2e6 时),
  eid@+18 语义; miss 7727→4323;
- **molding1 全解**: 92B 主段 + 56B 尾段 (7192-7279) 补充扫描 _scan_extra_node_segs
  (主段后 512KB + nid 下限 + nid 递增聚类); 节点 7191→7279, 元素 344→14558 全解;
- **SEAT_MODEL 回归修复**: family-1 检测误触发 (@+4 与 @+18 差恒定 = 不同元素),
  限制 @+4 >= 2e6 后恢复 27498 (miss 5);
- 全量: node 109/122, elem 91/122, 0 崩溃;
- 剩余: truck 4323 (A 型段 eid 映射 + config 55 段), chapter2_2 (v13), wing_section 852, frame_assembly 1365/848, car_section 626.

### 7. v13.03 布局破解 + P0-3 (2026-08 本轮)
- **节点 96B 布局**: [0x10200bc7][0][0][nid][0][0][x][y][z], 间距 96; _scan_v13_node_segs;
- **Y=4 元素 76B 记录**: [eid][恒定][(0,eid)][行号@+28 起] (3 个->config 103, 4 个->config 104); _parse_v13_elems;
- **chapter2_2 全解**: 节点 0→2898, 元素 0→2813;
- 全量: node 109/122, elem 92/122, 0 崩溃;
- 剩余: truck 4323 (A 型段 eid 映射), wing_section 852, frame_assembly 1365/848, car_section 626, geometry 4116.

### 7b. A 型元素 eid 字段判别 + frame_assembly/truck eid 映射 (2026-08 本轮)
- **问题**: 部分文件 (frame_assembly_3/4、truck Y=1) 记录 @+4 存的是存储 ID (非真实 eid),
  真实 eid 是跨 @+8 高16位与 @+12 低16位的 misaligned u32 (@+10); 而 yoke/Morph/cartridge 等 @+4 即真实 eid。需按记录布局判别。
- **A 型记录 eid 字段判别规则** (写入 `_parse_a_type`):
  - family-1 (`u16(@+12)==2596`): eid 在 @+4 (小 eid, SEAT_MODEL/cartridge) 或 @+18 (大存储 ID, truck Y=2);
  - 标准 A 型 (`@+12==0`): 完整 eid 在 `u32(@+10)`; 但未重编号文件 (cartridge `@+10=@+4+1`) 在 `@+10>@+4` 时 eid 在 @+4;
  - `@+4` 为存储 ID (`>=2e6`, truck Y=1): 完整 eid 在 `u32(@+10)`;
  - 其他 (`@+12==1..6`, yoke/Morph): 用 @+4。
- **@+8 字段语义**: `@+8=(eid低16位<<16)|维度`, 维度 1=1D/2=2D/3=3D (非节点数)。
- **truck Y=7 段** (新增 `_parse_y7_elems`): config-3 (112B, tag 259@+92, eid@+82, 节点@+96/@+100) 与 config-60 (176B, tag 316@+68, eid@+58, 节点@+72/@+76/@+164)。
- **truck Y=4 特殊元素段** (新增 `_parse_y4_elems`): 按 tag 判别 —
  - config 55 (tag 567@+52): 变长记录, `eid=u32(@+42)`, n@+56, 节点数=n+1 (节点1@+60, 节点2..n+1@+72 起), 记录长=76+4n;
  - config 60 (tag 316@+44): 152B, `eid=u32(@+34)`, 节点@+48/@+52;
  - config 21 (tag 277@+52): 80B, `eid=u32(@+42)`, 节点@+56/@+60;
  - config 22 (tag 278/534/790/1302@+52): 100B, `eid=u32(@+42)`, 278→2 节点, 其余→4 节点。
- 修复: frame_assembly_3 (10588→11953 全解), frame_assembly_4 (10513→11361 全解),
  frame_assembly_1 (9974→10066 全解), truck (196766→**212489 全解**), SEAT_MODEL (27498→27499)。
- 全量: node 110/122, elem **97/122**, 0 崩溃; 无回归。

### 7c. geometry + SEAT_MODEL config 60 + car_section config 3 (2026-08 本轮)
- **geometry Y=0 段** (新增 `_parse_y0_elems`): 无标准 CONST 锚, u16 粒度变长记录。
  记录布局 (长 22+4n): eid u16@+0, 5×0 u16, marker u16@+12 (低字节=config),
  节点 u16@+14+4i, 4×0 尾; CONST 块分隔 `[CONST][first_eid u16][0][16]`。
  config→节点数: 104→4/103→3/208→8/206→6。节点区有 gap (221..270) 需 row_map 映射。→ **4116/4116 全解**。
- **SEAT_MODEL config 60** (新增 `_parse_y2_c60`, 3 节点 136B + `_parse_y4_elems` 2 节点 152B):
  eid 判别改用 @+18 (family-1) 当 @+4 为存储 ID (非仅 >=2e6)。→ **27503/27503 全解**。
- **car_section Y=6 config 3** (新增 `_parse_y6_c3`): rigid 元素, tag 259@+22, 2 节点@+24/+28,
  100B stride, CONST 锚在 sh+84 (Y=6 段有 list 头)。tag 316 (config 60/RBE3) 与 tag 277 (config 21) 非元素跳过。→ elems 27885→28021。
- **car_section 剩余 miss 490**: 属**重复 eid 现象** — 348 个 config 208 (solid 六面体, 8 节点)
  与 142 个 rigid (config 60/21) 元素与 shell (config 104/103) **共享 eid**。oracle
  `*createmark elements` 计 28511 条 (含 490 重复), 而 `hm_getvalue elements id=...`
  对重复 eid 只返回 shell 元素。decoder 的 dict (eid→elem) 无法表示重复 eid,
  故 28021 唯一 eid 已与 oracle 一致 (real missing=0), 差 490 为重复元素。
  彻底解决需 HMModel 支持重复 eid (list 而非 dict)。
- 全量: node 110/122, elem **101/122** (+4: geometry/SEAT_MODEL + 2), 0 崩溃; 无回归。
- 剩余: car_section miss+490 (重复 eid 现象), SEAT_MODEL nodes miss+1 (节点 34328 布局待解)。

### 8. 头部布局按版本分 4 代

| 布局家族 | 版本 | 特征（u32@0x14 / 0x1c / 0x3c） | 文件数 |
|---|---|---|---|
| v10-legacy | 10.02 | 0x14/0x1c 为双精度数据（非小整数） | 2 |
| v11-classic | 11.03–11.05 | 126 / 262144 或 7277 / 397 或 0 | 108 |
| v12-13 | 12.03–13.03 | 10000 / 20 / 大值 | 9 |
| v14+ | 14.07–17.01 | 1 / 1–11 / 1536 | 3 |

v11 家族内：u32@0x1c 有两种取值（262144=55+1 文件、7277=44 文件），u32@0x3c 大多为 397（56 文件）——两者疑似「记录流偏移量/规模」类字段，待 Phase 1 验证。

### 4. 载荷头常量（v11-classic，跨文件一致）
- @0x00: u32 0；@0x04: double DB 版本（11.05 等）；@0x0c/0x10: u32 0
- @0x14: u32 126(0x7e)；@0x18: u32 1；@0x1c: u32 262144(0x40000) 或 7277
- @0x20/0x28: 两个 double（@0x28 值 0x3f1a36e2eb1c432d ≈ 1e-4 恒定；@0x20 各文件不同，疑似时间戳/GUID）
- @0x34: double 0x3fb999999999999a ≈ 0.1 恒定；@0x3c: u32 397 恒定
- 尾部：0x3e6(998)、0x3e7(999)、0x9b(155) 三常量，跨文件一致

### 5. 命名块模式（已泛化，但 class_id 语义待解）

模式：[u32 cap=19][u32 0][u32 class_id][name bytes]，在 3 个文件中 16 处重现。oracle 对照：

| name | class_id | oracle 身份 |
|---|---|---|
| BAR2 / base | 5 | comp（BAR2 为 comp 名；base 亦 comp） |
| auto1 | 6 | comp（leg_geom） |
| tetras | 7 | comp |
| geomety | 8 | comp |
| line_mesh / property1 | 10 | comp / **prop** |
| Model | 11 | 装配/模型对象 |
| joint_child / joint_parent / body_systems | 12 / 13 / 13 | 待 oracle 确认（系统/组？） |
| feature_elements | 17 | comp |

**class_id ≠ 实体类型**（comp 与 prop 均可为 10）；需要更大规模「name ↔ class_id ↔ oracle 实体类型」关联实验（Phase 2 首个实验）。

### 6. 语料库的战略价值
- **极小型文件是解码入口**：3_step_proc.hm10（载荷 5,001B）、shell_section.hm（4,919B）、leg_geom.hm（5,957B，仅 4 节点/3 线/1 组件）——已知内容 + 可人工通读的载荷长度；
- **版本差分**：10 个 DB 版本可对比记录布局演化；
- **配对外部格式**：tutorials 另含 .fem×5、.key×5、.k×4、.inp×1、.iges/.igs/.stp 等，可能与被 .hm 保存的同一模型对应，可作第二验证源；
- **版权注意**：语料属 Altair 教程文件，仓库内仅保存索引清单（corpus/corpus_index.json），不批量复制入仓库；如需离线，仅复制极小型代表文件并注明来源。

---

## 三、开放开发计划（v2，语料驱动）

总体路线不变：oracle 差分逆向，不触碰 DLL 反汇编。语料库使 Phase 0–2 的输入从「合成样本」升级为「122 个真实样本 + 版本矩阵 + 逐文件 ground truth」。

### Phase 0 — 基础建设与语料固化（约 1 天）
- [ ] oracle 封装：hmbatch 批处理模板 + Tcl 查询库（计数/命名/配置直方图/坐标查询），结果写 JSON 日志（已踩坑：Tcl 内 puts stdout 不可用，必须写文件）
- [ ] **批量 ground truth 收割**：对 122 个语料文件逐一批量运行 oracle，产出 ground_truth/*.json（实体计数、comp 名称与 ID、单元 config 直方图）
- [ ] 语料固化：corpus_index.json 已建（✅ 本轮完成）；补 corpus/manifest.md（按版本选代表 + 极小型文件的入库决策）
- [ ] 合成语料生成器（保留）：Tcl 构造已知最小模型 → 存 .hm，用于「受控变量」实验（真实语料变量不可控）
- 验收：一条命令批量产出全部语料的 ground truth JSON

### Phase 1 — 容器与头部格式定论（约 0.5–1 天）
- [x] 前缀 12 字节（u32 0 + double 5.0）恒定 → 122/122 证实
- [x] 载荷头 double@0x04 = DB 版本 → 10 个版本实测
- [ ] 待解：4 代头部布局的完整字段语义（v10-legacy / v11-classic / v12-13 / v14+），优先 v11-classic（108 文件 + 仓库样本）
- [ ] 待解：u32@0x1c（262144 vs 7277）、u32@0x3c（397 vs 0）与模型规模/保存选项的关系（用 oracle 重存同一文件对比）
- [ ] 待解：尾部常量 0x3e6/0x3e7/0x9b 的语义
- 验收：容器层格式规范 v1（各版本头部字段语义，标注已验证/推断/未知）

### Phase 2 — 记录帧与实体表逆向【核心，约 2–4 天】
- [ ] **首个解码目标：leg_geom.hm**（5,957B 载荷、4 节点/3 线/1 组件）→ 用 oracle 取全部坐标/ID/名称 → 在 6KB 载荷中人工通读定位，再放大到 shell_section.hm / 3_step_proc.hm10
- [ ] class_id 关联实验：用批量 ground truth 建立「name → class_id → oracle 实体类型/config」全表，解 class_id 语义
- [ ] 差分矩阵实验（合成语料）：+1 node / +1 elem / +1 comp / +1 属性，定位实体记录区与帧格式（tag/len/type 编码）
- [ ] 版本差分：v11.03/11.04/11.05 记录布局是否一致；v10/v12-13/v14+ 各看 1 个小型代表
- [ ] 产出：区段地图文档 + Python/Kaitai Struct 语法草案
- 验收：leg_geom.hm 全实体（4 节点坐标、3 线、auto1）可独立解码且与 oracle 一致

### Phase 3 — 解析器实现（约 1–2 天）
- [ ] 新模块 hmdecoder/：容器层 → 记录层 → 实体提取（nodes/elements/comps/props/points/lines/surfaces + 命名与属性），先支持 v11-classic
- [ ] 废弃 hm_parser.py / hm_parser_v2.py 滑动窗口方案（保留为历史参考）
- 验收：仓库样本输出 6,408 节点 / 31,843 单元，ID 与 oracle 一致

### Phase 4 — 验证闭环与导出（约 1 天）
- [ ] 自动比对器：解析结果 ↔ oracle（'*writefile' .fem/.inp + Tcl 逐 ID 查询），输出差异报告（ID 集合、坐标误差、连通性、组件归属）
- [ ] 导出器：真实 ID 的 INP/STEP（修复当前伪造输出）；坐标/拓扑 100% 一致才放行
- [ ] 回归集：≥10 个样本（合成矩阵 + 极小型真实样本 + 仓库样本），全绿才合并
- 验收：比对报告 0 差异；final_output/ 被真实数据替换

### Phase 5 — 文档与开放化（约 0.5 天）
- [ ] 格式文档（容器+记录+区段地图，按「已验证/推断/未知」分级标注置信度）
- [ ] 清理伪造产物、更新 README/AGENTS.md、语料库说明与复现步骤
- [ ] 沉淀 oracle 探针脚本为可复用工具（含 license/环境前置检查）
- 验收：新人可照 README 复现「从 .hm 到验证通过的 INP」全流程

### 里程碑
- M1（Phase 0+1 完成）：容器规范 v1 + 122 文件 ground truth 库
- M2（Phase 2 完成）：leg_geom.hm 全实体独立解码 + class_id 语义解明
- M3（Phase 3+4 完成）：仓库样本全量、零差异解析与导出
- M4（Phase 5 完成）：格式文档公开化、仓库自洽

### 风险与对策
- License 依赖：oracle 需要 license，已实测可用；若失效，退化为「纯静态 + 既有 ground truth」路线（进度大降）
- 版本差异：4 代头部布局、10 个 DB 版本 → 以 v11-classic 为主线，其余版本各选小型代表处理
- 版权边界：语料为 Altair 教程文件，仓库仅存索引不批量复制；不反汇编 DLL，只利用 oracle 正常读写
- 记录帧复杂度：若 L3 采用变长/索引表结构，Phase 2 工期上浮 → 用「极小型文件人工通读 + 差分矩阵」逐步收敛，先节点后单元

### 关键现有证据（供各阶段引用）
- 容器：前缀 u32 0 + double 5.0 + gzip @0x0c（122/122 证实）
- 载荷头（v11）：u32 0 | double 版本 | u32 0 | u32 0 | u32 126 | u32 1 | u32 262144/7277 | … | double≈0.1 @0x34 | u32 397 @0x3c
- 尾部：0x3e6=998、0x3e7=999、0x9b=155
- 命名块：[cap=19][0][class_id][name]，class_id ∈ 5,6,7,8,10,11,12,13,17（语义待解）
- 文本记录：tag 0x40000065/66 + 双长度前缀 ASCII（仅仓库样本，疑为 IGES 导入属性）
- oracle ground truth：仓库样本 6408 节点/31843 单元(config 103)/2 comps(240,241)/1 prop/157 点/354 线/93 面；1d_elements 443/400(config 104)/4 comps/3 mats/2 props；leg_geom 4 节点/3 线/1 comp
