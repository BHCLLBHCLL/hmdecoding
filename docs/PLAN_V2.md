# HyperMesh .hm 解码 — 新关键开发规划 (v2)

> 更新日期: 2026-08 (goal 深入解析多轮后)
> 当前基线 (完整 oracle 对照 123 文件): **node exact 114/123 (93%), elem exact 103/123 (84%)**
> 覆盖: v10-legacy / v11-classic (11.03-11.05) / v12-13 / v14+ (17.01) 全家族; 容器层 122/122.

---

## 0. 现状基线 (精确 miss 清单, 最新 commit 实测)

### 节点 miss (9 文件, 均为 +1/-n 级)
| 文件 | cur/exp | 差距 | 性质 |
|---|---|---|---|
| truck / car_section / seat_2 / seat_start | +1~+2 | 兼容性 | 头 count 含虚值/重复 id 容差 |
| hm-ansys_contact_manager_2d | 202/203 | -1 | 末条 44B 短记录 nid 隐含 |
| icw_ex2 / icw_ex1 | 82/100, 77/89 | -18/-12 | 节点段解析截断 (52B 变体) |
| solid_geom / solid_map | 0/2, 4/2 | 小型 | v11 极小型节点段 (count<45) |

### 元素 miss (16 文件, 按缺口排序)
| 文件 | cur/exp | 缺口 | 性质 |
|---|---|---|---|
| **wing_section_complete** | 150/1001 | **-851** | Y=3 复合记录变体 (0x1a040be4 头 + ASCII 名) |
| **hm-ansys_contact_wizard_2d** | 0/202 | **-202** | Y=3 新布局 (0x30200B1F 头, 非 CONST 家族) |
| **hm-ansys_contact_manager_2d** | 0/173 | **-173** | 同上 |
| car_section | 28371/28511 | -140 | A 型部分段 (Y=1 存储 ID eid 映射片段) |
| abaqus_contactManager_3D | 1215/1340 | -125 | A 型部分段 |
| hm-ansys_contact_manager_3d / wizard_3d | 799/924 | -125 | A 型/特殊段 |
| body_side_assembly | 20215/20320 | -105 | A 型部分段 |
| abaqus_contactManager_2D | 490/537 | -47 | B 型槽位部分段 |
| rear_truss_1_new | 1702/1740 | -38 | A 型部分段 |
| seat_2 / seat_start | 1526/1562 | -36/-34 | A 型部分段 |
| joints | 998/1009 | -11 | Y=3 特殊元素 (0D/刚性) |
| hook / crash_tubes / channel / keyhole / abaqus3_0 | 3~4 级 | 微小 | 末条/边界 |

---

## 1. 规划总目标

**把 elem exact 从 103 推至 ~118/123 (96%), node exact 从 114 推至 ~120/123**, 并深化
元素记录字段语义 (属性/显示/实体类型判别), 每个关键改进自动 commit+push 到 GitHub.

---

## 2. P0 — 收敛最大缺口 (预估 +1228 元素, elem exact → ~112)

### P0-1: wing_section_complete Y=3 复合记录变体 (-851)
- 线索: 段 [997][8][475][3][3], 记录头 0x1a040be4 + [8] + ASCII 名 (如 "1795..") + 0x0a040be6 + [2] + 0x12040084 + [坐标][eid@+36][0][0] + (u16 属性, u16 节点行号) 对
- 方法: oracle 对照前 5 元素 eid/节点/坐标 → 字节定位 → _parse_a_geom 变体 (ASCII 名长度变长/属性对更多); 记录间距自适应 (非固定 71-74B)
- 验证: wing_section 1001/1001 + 既有文件不回归

### P0-2: hm-ansys 2D 系列 Y=3 新布局 (-375)
- 线索: 段 [997][1][175][40][3][2], 记录头 0x30200B1F + [7][0][0x30200B21][7][1][1][0][0][u16 属性+行号对] (无 CONST)
- 方法: oracle 对照 wizard_2d/manager_2d 前 5 元素 → 字节定位 → 新 _parse_ansys2d_elems (0x30200B1F 家族标记)
- 验证: 两文件 202/202 + 173/173

### P0-3: car_section/body_side_assembly/abaqus_3D 部分段 (-370)
- 方法: 逐文件定位剩余 miss 段 (A 型 eid 字段判别泛化 — 存储 ID vs 真实 eid 的 @+10 misaligned 判别), 补 config 55/60 段
- 验证: 三文件各 +100~140

---

## 3. P1 — 节点完整性 (node exact → ~120)

### P1-1: icw_ex1/2 节点 (-30)
- 线索: 52B 变体 + 进度截断; 参照 _scan_small_node_clusters 扩阈
- 方法: oracle 对照节点 id 序列 → 段流断点定位 → 合并多子块

### P1-2: solid_geom/solid_map 极小型段 (0/2, 4/2)
- 方法: find_node_section 阈值按 count 缩放 (已有), 扩展覆盖 count<50 的 v11 小段

### P1-3: truck/car_section/seat ±1-2 兼容性
- 方法: 头 count 虚值/重复 id 过滤 — parse_nodes 按 id 去重 (同 id 保留一个), 或 count 取实际有效数

---

## 4. P2 — 中等缺口 (-3 到 -47)
- hook / crash_tubes / channel / keyhole / abaqus3_0 / rear_truss / seat_2 / seat_start / abaqus_2D / joints: 均为末条记录或单个特殊段
- 方法: 逐文件 oracle 对照缺失 eid → 定位断链点 (末条 eid 链尾 / 0D 元素 tag) → 补 _parse_b_slots 尾链 / _parse_y3 0D 处理
- 验证: 各文件 exact

---

## 5. P3 — 深度 (记录字段语义)

### P3-1: 元素记录附加字段语义
- 0x1a040be4 / 0x0a040be6 / 0x12040084: body_side/composites/wing 前置字段 — 疑为显示/属性数据, oracle 对照 comp/prop 引用
- **@+8 = (eid低16<<16)|维度** (维度 1/2/3 = 1D/2D/3D): 已记录, 补 config 字典
- **存储 ID vs 真实 eid**: 未重编号文件判别泛化

### P3-2: 实体类型判别 (元素 vs edge/face)
- truck 2000001+ 段为 **edge 段** (oracle edges=212489; 记录结构近似元素但 eid 非元素实体)
- 方法: oracle 对照 edge/face 实体 id → 记录特征 (edge 2-节点 + 元素引用字段) → 段排除逻辑
- 价值: truck 排除 7049 个伪元素, 且避免其它文件的 edge/face 段误判

### P3-3: config 完整字典
- 收集全语料出现的 config (1/2/3/21/22/55/60/61/103/104/204/205/206/208/220/...) → 名称/维数映射到 spec

---

## 6. P4 — 工程化与验证

- **auto_compare.py 固化**: decode 全语料 vs corpus_gt.json, 输出覆盖率报告, 作为回归门禁
- **崩溃防护**: 全语料 decode 0 崩溃 (当前达标); 每改进后跑全量确认
- **导出一致性**: export_inp/step/iges 用最新 elements (list 形式) 回归
- **文档**: PLAN/README/spec 每阶段更新; 每关键改进 commit+push

---

## 7. 里程碑与验收

| 阶段 | 完成标志 | 预估 |
|---|---|---|
| P0 | elem exact ≥112 | 3-5 轮 |
| P1 | node exact ≥120 | 2 轮 |
| P2 | 中等缺口清零 (elem 118+) | 3 轮 |
| P3 | 字段语义 50% 记录到 spec | 3 轮 |
| P4 | auto_compare 门禁 + 文档固化 | 随各轮 |

**本轮 (P0) 立即行动**: 先攻 wing_section_complete (最大缺口 851) — 已定位头 0x1a040be4 + ASCII 名, oracle 对照即得布局.
