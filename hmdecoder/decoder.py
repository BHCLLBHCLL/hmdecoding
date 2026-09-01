#!/usr/bin/env python3
"""hmdecoder — HyperMesh .hm 容器/节点/单元/显示/几何点解码器。

支持 DB 版本族: v10-legacy, v11-classic (11.03–11.05), v12-13 (部分).
节点段: [136] 头 + 记录 52B ([id][0][0][x][y][z][0x4]) / 92B (+40B 附加) / 56B ([x][y][z][0x4][id+1][0][0]).
元素段: [997][seg][175][count][X][Y]; A 型 (X=3, CONST 锚) / B 型 (X=2, 链式 eid).
"""
import gzip, struct
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Node:
    id: int
    x: float; y: float; z: float

@dataclass
class Elem:
    id: int
    nodes: list
    config: int = 0

@dataclass
class DisplayPoint:
    id: int
    x: float; y: float; z: float

@dataclass
class GeoPoint:
    id: int
    x: float; y: float; z: float

@dataclass
class HMModel:
    nodes: dict = field(default_factory=dict)
    elements: list = field(default_factory=list)  # list[Elem], 允许重复 eid (shell/solid/rigid 共存)
    display_points: dict = field(default_factory=dict)
    geo_points: dict = field(default_factory=dict)
    db_version: float = 0.0
    node_count: int = 0
    elem_count: int = 0
    node_section: int = 0
    elem_section: int = 0
    element_variant: str = ""

def load_payload(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b"\x00\x00\x00\x00", "非标准前缀"
    ver = struct.unpack_from("<d", raw, 4)[0]
    assert abs(ver - 5.0) < 1e-9, f"包装版本异常: {ver}"
    return gzip.decompress(raw[12:])

def u32(p, o): return struct.unpack_from("<I", p, o)[0]
def _rec_add(elems, eid, cfg, nds):
    """保留同 eid 的重复记录 (car_section 等 Ansys 多实体模型). dict[eid]=list[(cfg, nds)]."""
    elems.setdefault(eid, []).append((cfg, nds))
    return elems

def u16(p, o): return struct.unpack_from("<H", p, o)[0]
def d64(p, o): return struct.unpack_from("<d", p, o)[0]
CONST = 0x70241FF5
CONST_12 = 0x70501FF5  # v12-13 元素段常量
MARK_GEOM = 0x40008126

def is_const(v):
    """元素段常量家族: 0x70??1FF5 (v11: 0x70241FF5, v12-13: 0x70501FF5)."""
    return (v & 0xFFFF) == 0x1FF5 and ((v >> 24) & 0xFF) == 0x70

NODE_LAYOUTS = ((52, 0, 12, False), (52, 4, 12, False), (52, 8, 20, False),
                (92, 0, 12, False), (92, 4, 12, False), (92, 8, 20, False),
                (56, 44, 0, True))  # 68B 仅用于结构扫描 (v14+ 无 [136] 头)

def find_node_section(p):
    hits = []
    scan_lim = min(len(p), 8_000_000)  # 节点段均在文件前部
    start = 0
    while True:
        i = p.find(b"\x88\x00\x00\x00", start, scan_lim)
        if i < 0:
            break
        n = u32(p, i + 4)
        if 1 <= n <= 10_000_000:
            hits.append((i, n))
        start = i + 1
    hits.sort(key=lambda h: -h[1])
    best = None
    for hi, count in hits[:600]:
        for base in range(hi - 32, hi + 48, 4):
            if base < 0:
                continue
            for stride, idoff, xoff, chain in NODE_LAYOUTS:
                ok = 0; bad = 0
                seen = set()
                for k in range(min(count, 60)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    x = d64(p, rec + xoff)
                    if chain:
                        tailok = u32(p, rec + 48) == 0 and u32(p, rec + 52) == 0
                        nid = u32(p, rec + 44) - 1
                    else:
                        tailok = True
                        nid = u32(p, rec + idoff)
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and tailok:
                        ok += 1
                        seen.add(nid)
                    else:
                        bad += 1
                        if bad > 3:
                            break
                # 假候选 id 大量重复 (如 molding1 base=142 全 3) -> 淘汰
                if len(seen) < max(2, ok // 2):
                    continue
                # 小 count 文件 (极小型模型) 阈值按 count 缩放 (count=2 时需 2)
                need = max(1, min(count, max(3, int(min(count, 60) * 0.8))))
                if ok >= need and (best is None or ok > best[0]):
                    best = (ok, (hi, count, base, stride, idoff, chain))
    if best and best[0] >= max(1, min(best[1][1], max(3, int(min(best[1][1], 60) * 0.8)))):
        return best[1]
    return find_node_section_struct(p)

def _struct_stream_len(p, base, stride, idoff, xoff):
    """68B 节点流扩展: [id][0][k<=16][x][y][z][0x8]."""
    cnt = 0
    while base + cnt * stride + stride <= len(p):
        rec = base + cnt * stride
        nid = u32(p, rec + idoff)
        x = d64(p, rec + xoff)
        if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and u32(p, rec + 4) == 0 and 1 <= u32(p, rec + 8) <= 16:
            cnt += 1
        else:
            break
    return cnt

def find_node_section_struct(p, multi=False):
    """结构扫描 (v14+ 无 [136] 头, 如 dummy_positioner 68B 记录).

    全文件扫描 [id][0][k] 68B 流; multi=True 时收集全部段 (v17 多节点段),
    返回 [(count, base, stride, idoff, chain), ...]; 否则返回单段.
    """
    segs = []
    limit = len(p)
    # 68B (dummy_positioner 块 A) + 92B (块 B) 布局; 仅 v14+ 调用 (见 decode)
    for stride, idoff, xoff, chain in ((68, 0, 12, False), (92, 0, 12, False)):
        # 粗扫: [0][k] k=1..8 字节模式
        cand_bases = []
        for mark in range(1, 9):
            pat = b"\x00\x00\x00\x00" + bytes([mark]) + b"\x00\x00\x00"
            start = 0
            while True:
                i = p.find(pat, start)
                if i < 0:
                    break
                base = i - 4
                if base >= 0:
                    nid = u32(p, base + idoff)
                    if 1 <= nid <= 10_000_000:
                        cand_bases.append(base)
                start = i + 1
        cand_bases.sort()
        # 精扫: 找流起点 (第一个 30 条验证通过的 base), 扩展后跳过该流
        checked = set()
        i = 0
        while i < len(cand_bases):
            cb = cand_bases[i]
            first_match = None
            for base in range(max(0, cb - 64), min(cb + 68, limit - 20 * stride), 4):
                if base in checked:
                    continue
                checked.add(base)
                pre = 0
                for k in range(3):
                    rec = base + k * stride
                    if 1 <= u32(p, rec + idoff) <= 10_000_000 and u32(p, rec + 4) == 0 and 1 <= u32(p, rec + 8) <= 16:
                        pre += 1
                if pre < 3:
                    continue
                ok = 0
                ids = set()
                for k in range(30):
                    rec = base + k * stride
                    nid = u32(p, rec + idoff)
                    x = d64(p, rec + xoff)
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and u32(p, rec + 4) == 0 and 1 <= u32(p, rec + 8) <= 16:
                        ok += 1
                        ids.add(nid)
                    else:
                        break
                if ok >= 25 and len(ids) >= 15:
                    first_match = base
                    break
            if first_match is not None:
                cnt = _struct_stream_len(p, first_match, stride, idoff, xoff)
                segs.append((None, cnt, first_match, stride, idoff, chain))
                if not multi:
                    return segs[-1]
                # 跳过该流内的候选
                skip_until = first_match + cnt * stride
                while i < len(cand_bases) and cand_bases[i] < skip_until:
                    i += 1
                continue
            i += 1
    if not segs:
        return [] if multi else None
    if multi:
        return segs
    return max(segs, key=lambda s: s[1])

def _scan_small_node_clusters(p, lim=10000.0, min_cnt=2, max_cnt=49):
    """补扫小节点段 (2..49 条): 68B/92B 布局, 允许 k=0.

    find_node_section_struct 要求 k in 1..16 且 >=25 条连续验证,
    会漏掉 k=0 的小节点段 (如 v17 的 3 条尾段). 此处用 [nid][0][k]
    的零4 字段定位: 节点段基址均落在 mod-4=3 网格 (与已检测大段一致).
    返回 [(count, base, stride, idoff, chain), ...].
    """
    n = len(p)
    ZERO4 = b"\x00\x00\x00\x00"
    starts = {68: [], 92: []}
    j = 0
    scan_lim = min(n, 36_000_000)  # 节点数据集中在文件前部
    while True:
        j = p.find(ZERO4, j, scan_lim)
        if j < 0:
            break
        base = j - 4
        if base < 0 or base % 4 != 3:
            j += 1
            continue
        nid = u32(p, base)
        k = u32(p, base + 8)
        if not (1 <= nid <= 10_000_000 and k <= 16):
            j += 1
            continue
        for stride in (68, 92):
            if base + stride > n:
                continue
            x, y, z = d64(p, base + 12), d64(p, base + 20), d64(p, base + 28)
            if abs(x) < lim and abs(y) < lim and abs(z) < lim:
                starts[stride].append(base)
                break
        j += 1
    out = []
    for stride, lst in starts.items():
        vset = set(lst)
        runs = []
        for c in sorted(vset):
            if runs and runs[-1][-1] + stride == c:
                runs[-1].append(c)
            else:
                runs.append([c])
        for r in runs:
            if not (min_cnt <= len(r) <= max_cnt):
                continue
            # 至少一条 k>=1, 且至少一条非零坐标 (排除元素数据假阳性)
            if not any(1 <= u32(p, x + 8) <= 16 for x in r):
                continue
            if not any(max(abs(d64(p, x + 12)), abs(d64(p, x + 20)),
                           abs(d64(p, x + 28))) > 0.001 for x in r):
                continue
            out.append((None, len(r), r[0], stride, 0, False))
    return out

def _collect_node_segments(p, lim=10000.0):
    """v17 节点段收集 (快速统一扫描): 零4 定位 68B/92B 记录, 聚类成段, 重叠修正.

    覆盖大段 (块 A 68B / 块 B 92B) 与 k=0 小段 (块 C). 段基址均落在
    mod-4=3 网格 (与 find_node_section_struct 检出的大段一致). 相邻段
    紧邻切换时会互相过扫 1 条, 按段基址截断修正, 保证 row_map 无幻影行.
    """
    n = len(p)
    ZERO4 = b"\x00\x00\x00\x00"
    starts = {68: [], 92: []}
    j = 0
    while True:
        j = p.find(ZERO4, j)
        if j < 0:
            break
        base = j - 4
        if base < 0 or base % 4 != 3:
            j += 1
            continue
        nid = u32(p, base)
        k = u32(p, base + 8)
        if not (1 <= nid <= 10_000_000 and k <= 16):
            j += 1
            continue
        for stride in (68, 92):
            if base + stride > n:
                continue
            x, y, z = d64(p, base + 12), d64(p, base + 20), d64(p, base + 28)
            if abs(x) >= lim or abs(y) >= lim or abs(z) >= lim:
                continue
            # k==0 且坐标全零 -> 假起点 (原点节点记录内部的零字节)
            if k == 0 and max(abs(x), abs(y), abs(z)) < 0.001:
                continue
            starts[stride].append(base)
        j += 1
    segs = []
    for stride, lst in starts.items():
        vset = set(lst)
        runs = []
        for c in sorted(vset):
            if runs and runs[-1][-1] + stride == c:
                runs[-1].append(c)
            else:
                runs.append([c])
        for r in runs:
            if len(r) < 2:
                continue
            # 至少一条 k>=1, 且至少一条非零坐标 (排除元素数据假阳性)
            if not any(1 <= u32(p, x + 8) <= 16 for x in r):
                continue
            if not any(max(abs(d64(p, x + 12)), abs(d64(p, x + 20)),
                           abs(d64(p, x + 28))) > 0.001 for x in r):
                continue
            segs.append((None, len(r), r[0], stride, 0, False))
    # 若未检出 (其他版本布局), 回退到旧结构扫描
    if not segs:
        segs = list(find_node_section_struct(p, multi=True))
        segs += _scan_small_node_clusters(p)
    # 重叠修正
    segs.sort(key=lambda s: s[2])
    fixed = []
    for i, (hi, cnt, base, stride, idoff, chain) in enumerate(segs):
        end = base + cnt * stride
        for j2 in range(i + 1, len(segs)):
            if segs[j2][2] > base:
                if end > segs[j2][2]:
                    cnt = (segs[j2][2] - base) // stride
                break
        if cnt >= 1:
            fixed.append((None, cnt, base, stride, idoff, chain))
    return fixed

def _scan_extra_node_segs(p, exclude_ranges, lo=0, hi=None, min_nid=0, lim=10000.0):
    """补充扫描小节点段 (v11 多布局): 52/56/68/92B, 任意对齐, 排除已知主段范围.

    v11 文件可能把节点拆成多个布局段 (如 molding1: 92B 主段 + 56B 尾段),
    而 find_node_section 只返回主段. 零4 定位 + 聚类, 要求 >=2 条且非零坐标.
    exclude_ranges: [(start, end), ...] 已知主段覆盖范围.
    lo/hi: 扫描范围 (默认主段之后区域). min_nid: 段内 nid 下限 (主段节点数).
    返回 [(count, base, stride, idoff, chain), ...].
    """
    n = len(p)
    if hi is None:
        hi = n
    ZERO4 = b"\x00\x00\x00\x00"
    starts = {52: [], 56: [], 68: [], 92: []}
    j = max(lo, 0)
    while True:
        j = p.find(ZERO4, j, hi)
        if j < 0:
            break
        base = j - 4
        if base < 0 or any(a <= base < b for a, b in exclude_ranges):
            j += 1
            continue
        nid = u32(p, base)
        k = u32(p, base + 8)
        if not (min_nid < nid <= 10_000_000 and k <= 16):
            j += 1
            continue
        for stride in (52, 56, 68, 92):
            if base + stride > n:
                continue
            x, y, z = d64(p, base + 12), d64(p, base + 20), d64(p, base + 28)
            if abs(x) < lim and abs(y) < lim and abs(z) < lim:
                starts[stride].append(base)
        j += 1
    out = []
    for stride, lst in starts.items():
        vset = set(lst)
        # 聚类: 间距 == stride 且 nid 严格递增 (相差 1); 假候选 (nid 跳变,
        # 间距 < 2*stride) 跳过, 间距 > 2*stride 视为新段起点
        runs = []
        for c in sorted(vset):
            if runs:
                last = runs[-1][-1]
                if c - last == stride and u32(p, c) == u32(p, last) + 1:
                    runs[-1].append(c)
                    continue
                if c - last > stride * 2:
                    runs.append([c])
                continue
            runs.append([c])
        for r in runs:
            if len(r) < 2:
                continue
            if not any(max(abs(d64(p, x + 12)), abs(d64(p, x + 20)),
                           abs(d64(p, x + 28))) > 0.001 for x in r):
                continue
            # 段起点回溯: 假候选污染聚类可能丢弃段首 (如 manager id 232 @base-stride).
            b = r[0]
            while b - stride >= 0 and u32(p, b - stride) == u32(p, b) - 1:
                # 校验回溯候选的坐标合理, 防止向数据区过度回溯
                if not (abs(d64(p, b - stride + 12)) < 10000.0
                        and abs(d64(p, b - stride + 20)) < 10000.0):
                    break
                b -= stride
                r.insert(0, b)
            out.append((None, len(r), b, stride, 0, False))
    return out

def _scan_v13_node_segs(p, lim=10000.0):
    """v13.03 节点段: 96B 记录 [0x10200bc7][0][0][nid][0][0][x][y][z], 间距 96."""
    MARK = (0x10200bc7).to_bytes(4, "little")
    hits = []
    j = 0
    while True:
        j = p.find(MARK, j)
        if j < 0:
            break
        nid = u32(p, j + 12)
        x = d64(p, j + 24)
        if 1 <= nid <= 10_000_000 and abs(x) < lim:
            hits.append(j)
        j += 1
    runs = []
    for c in sorted(hits):
        if runs and c - runs[-1][-1] == 96:
            runs[-1].append(c)
        else:
            runs.append([c])
    segs = []
    for r in runs:
        if len(r) >= 2:
            segs.append((None, len(r), r[0], 96, 12, False))
    return segs

def parse_nodes(p, cfg):
    hi, count, base, stride, idoff, chain = cfg
    nodes = {}
    xoff = 24 if stride == 96 else 12  # v13.03 96B 记录坐标 @+24
    prev_nid = 0
    for k in range(count):
        rec = base + k * stride
        if rec + stride > len(p):
            break
        if chain:
            nid = u32(p, rec + 44) - 1
            x, y, z = d64(p, rec), d64(p, rec + 8), d64(p, rec + 16)
            # 末条 44B 短记录: nid 字段被紧随的元素段标记覆盖 (读回更小的值),
            # 隐含 nid = 前一条 + 1 (如 SEAT_MODEL 节点 34328)
            if k == count - 1 and nid <= prev_nid:
                nid = prev_nid + 1
        else:
            nid = u32(p, rec + idoff)
            x, y, z = d64(p, rec + xoff), d64(p, rec + xoff + 8), d64(p, rec + xoff + 16)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9 and abs(y) < 1e9 and abs(z) < 1e9):
            break  # 记录流结束 (count 字段可能含虚值)
        nodes[nid] = Node(nid, x, y, z)
        prev_nid = nid
    return nodes, base

def row_map_from_nodes(p, cfg, base):
    hi, count, stride, idoff, chain = cfg[0], cfg[1], cfg[3], cfg[4], cfg[5]
    if chain:
        return {k + 1: k + 1 for k in range(count)}
    rows = {}
    for k in range(count):
        rec = base + k * stride
        if rec + stride > len(p):
            break
        rows[k + 1] = u32(p, rec + idoff)
    return rows

# ---------------------------------------------------------------------------
# 元素段
# ---------------------------------------------------------------------------
CONFIG_NODES = {103: 3, 104: 4, 204: 4, 220: 8, 205: 4, 206: 6, 208: 8,
                100: 2, 101: 2, 102: 2, 105: 2, 106: 2, 108: 2, 112: 2, 114: 2,
                201: 3, 202: 3, 203: 3, 301: 6, 302: 8, 303: 6, 304: 8, 305: 10, 306: 12,
                60: 3}

def find_elem_segments(p):
    segs = []
    start = 0
    while True:
        i = p.find(b"\xe5\x03\x00\x00", start)
        if i < 0:
            break
        if i + 24 <= len(p):
            segid = u32(p, i + 4); cfg71 = u32(p, i + 8); cnt = u32(p, i + 12)
            X = u32(p, i + 16); Y = u32(p, i + 20)
            if X in (2, 3) and 100 <= cfg71 <= 500 and 1 <= cnt <= 10_000_000 and Y < 10_000_000:
                segs.append((i, segid, cfg71, cnt, X, Y))
        start = i + 1
    return segs

def _parse_a_type(p, sh, cnt, row_count, row_map, max_rec=None):
    for s in range(sh + 16, sh + 80):
        if not is_const(u32(p, s)):
            continue
        elems = {}
        rec = s
        ok = True
        for k in range(min(cnt, max_rec if max_rec else cnt)):
            if not is_const(u32(p, rec)):
                # 断点重连: 记录流可能被其他数据块打断
                nxt = None
                j = p.find(b"\xf5\x1f", rec + 4, min(rec + 200, len(p) - 2))
                while j >= 0:
                    if is_const(u32(p, j)):
                        nxt = j
                        break
                    j = p.find(b"\xf5\x1f", j + 1, min(rec + 200, len(p) - 2))
                if nxt is None:
                    ok = False; break
                rec = nxt
                if not is_const(u32(p, rec)):
                    ok = False; break
            rec_v8 = u32(p, rec + 8)
            # A 型记录 eid 字段判别 (多布局). 完整 eid 是跨 @+8 高16位与 @+12 低16位的
            # misaligned u32 (@+10): 高16位存 eid_hi, @+8 高16位存 eid_lo, @+8 低16位存维度(1/2/3).
            # - family-1 (@+12==2596): eid 在 @+4 (小 eid) 或 @+18 (大存储 ID, 下面检测处理)
            # - @+4 为存储 ID (>=2e6, truck Y=1): 完整 eid 在 @+10
            # - 标准 A 型 (@+12==0): @+10 为完整 eid, 但未重编号文件 (cartridge 等 @+10=@+4+1)
            #   在 @+10 > @+4 时 eid 实际在 @+4
            # - 其他 (@+12==1..6, yoke/Morph): eid 在 @+4
            rec_v12 = u16(p, rec + 12)
            rec_v4 = u32(p, rec + 4)
            eid10 = u32(p, rec + 10)
            f1_eid = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
            if rec_v12 == 2596:
                # family-1 (@+12==2596): @+4 可能是存储 ID, 真实 eid 在 @+18
                # (SEAT_MODEL/truck). @+18 合法且 != @+4 时用 @+18, 否则 @+4 即真 eid.
                eid = f1_eid if (0 < f1_eid < 10_000_000 and f1_eid != rec_v4) else rec_v4
            elif rec_v4 >= 2_000_000:
                eid = eid10
            elif rec_v12 == 0:
                eid = eid10 if eid10 <= rec_v4 else rec_v4
            else:
                eid = rec_v4
            if not (0 < eid < 10_000_000):
                ok = False; break
            nxt = None
            j = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
            while j >= 0:
                if is_const(u32(p, j)):
                    nxt = j
                    break
                j = p.find(b"\xf5\x1f", j + 1, min(rec + 200, len(p) - 2))
            d = (nxt - rec) if nxt else None
            got = None
            # ---- family-1 布局 (v11 truck 等): CONST 后 701/686+2596 标记, eid@+18 ----
            # 仅当 @+4 为存储 ID (>= 2e6, 非真 eid) 且 != eid@+18 时启用;
            # 普通文件 (SEAT_MODEL 等 @+4 即真 eid) 走常规 flag 路径
            f1_eid = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
            if (rec_v8 in (0x02BD0002, 0x02AE0002)
                    and u16(p, rec + 12) == 2596
                    and u32(p, rec + 4) >= 2_000_000
                    and u32(p, rec + 4) != f1_eid):
                f1_flag = u32(p, rec + 28)
                f1_cfg = (f1_flag >> 16) - 256
                if (0 < f1_eid < 10_000_000 and 300 <= (f1_flag >> 16) <= 500
                        and (f1_flag & 0xFFFF) == 0):
                    f1_rows = []
                    kk = rec + 32
                    while len(f1_rows) < 12 and u32(p, kk) != 0:
                        f1_rows.append(u32(p, kk))
                        kk += 4
                    if 1 <= len(f1_rows) <= 12 and all(1 <= r <= row_count for r in f1_rows):
                        eid = f1_eid
                        got = (0, len(f1_rows), f1_rows, f1_cfg)
            # ---- v11 路径: flag<<16 u32 + u32 节点 ----
            prelens = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40] if d else [0]
            if got is None:
                for prelen in prelens:
                    rec_len = (d - prelen) if d else None
                    if rec_len is not None and (rec_len < 32 or rec_len % 4 or rec_len > 140):
                        continue
                    lim = (rec_len - 12) if rec_len else 84
                    cands = []
                    for off in range(12, lim, 4):
                        v = u32(p, rec + off)
                        f = v >> 16
                        if 300 <= f <= 500 and (v & 0xFFFF) == 0:
                            cands.append(off)
                    for fp in sorted(cands, reverse=True):
                        nodes_off = rec + fp + 4
                        n = 0
                        while n < 12 and nodes_off + 4 * n + 4 <= len(p) and u32(p, nodes_off + 4 * n) != 0:
                            n += 1
                        if n < 1:
                            continue
                        if rec_len is not None and nodes_off + 4 * n >= rec + rec_len:
                            continue
                        if u32(p, nodes_off + 4 * n) != 0:
                            continue
                        nds = [u32(p, nodes_off + 4 * j) for j in range(n)]
                        if all(1 <= r <= row_count for r in nds):
                            got = (prelen, n, nds, (u32(p, rec + fp) >> 16) - 256)
                            break
                    if got:
                        break
            # ---- v12 路径: u16 flag + u16 槽位节点 (58B 记录等) ----
            if got is None:
                for fp in range(16, 56, 2):
                    f = u16(p, rec + fp)
                    if not (300 <= f <= 500):
                        continue
                    nodes_off = rec + fp + 2
                    n = 0
                    while n < 12 and u16(p, nodes_off + 4 * n) != 0 and u16(p, nodes_off + 4 * n + 2) == 0:
                        n += 1
                    if n < 1:
                        continue
                    nds = [u16(p, nodes_off + 4 * j) for j in range(n)]
                    if all(1 <= r <= row_count for r in nds):
                        got = (fp, n, nds, f - 256)
                        break
            # ---- 低 config (plotel/1 节点等): [CONST][eid][1|k<<16][0][0][(cfg+256)<<16][row...][tail] ----
            if got is None:
                cfg = u16(p, rec + 22) - 256
                if (1 <= cfg <= 100 and u32(p, rec + 20) == (cfg + 256) << 16):
                    if cfg == 1:
                        ncfg = 1
                    elif cfg == 2:
                        ncfg = 2
                    else:
                        ncfg = 0
                        while ncfg < 8 and 1 <= u32(p, rec + 24 + 4 * ncfg) <= row_count:
                            ncfg += 1
                    if ncfg >= 1:
                        nds = [u32(p, rec + 24 + 4 * j) for j in range(ncfg)]
                        if all(1 <= r <= row_count for r in nds):
                            got = (24, ncfg, nds, cfg)
            if got is None:
                ok = False; break
            fp, n, nds, config = got
            _rec_add(elems, eid, config, [row_map.get(r, r) for r in nds])
            if nxt is None:
                break
            rec = nxt
        if ok:
            return elems
    return None

def _parse_b_type(p, sh, cnt, row_count, row_map, first_eid, max_rec=None):
    s = sh + 24
    elems = {}
    rec = s
    eid = first_eid
    for k in range(min(cnt, max_rec if max_rec else cnt)):
        if u32(p, rec) != 0 or u32(p, rec + 4) != 0:
            # 断点重连: 跳过异常数据块继续
            nxt = None
            for j in range(rec + 4, min(rec + 400, len(p) - 4)):
                if u32(p, j) == 0 and u32(p, j + 4) == 0 and 300 <= u16(p, j + 8) <= 500:
                    nxt = j
                    break
            if nxt is None:
                break
            rec = nxt
            if u32(p, rec) != 0 or u32(p, rec + 4) != 0:
                break
        flag = u16(p, rec + 8)
        if not (300 <= flag <= 500):
            break
        config = flag - 256
        n = CONFIG_NODES.get(config)
        if n is None:
            break
        nds = [u32(p, rec + 10 + j * 4) for j in range(n)]
        if not all(1 <= r <= row_count for r in nds):
            break
        _rec_add(elems, eid, config, [row_map.get(r, r) for r in nds])
        nxt = None
        for j in range(rec + 10 + 4 * n + 4, rec + 400):
            if u32(p, j) == 0 and u32(p, j + 4) == 0 and 300 <= u16(p, j + 8) <= 500:
                nxt = j
                break
        if nxt is None:
            break
        stride = nxt - rec
        if u32(p, nxt - 8) != 0:
            break
        ne = u32(p, nxt - 4)
        if not (0 < ne < 10_000_000):
            break
        eid = ne
        rec = nxt
    return elems

def _parse_b_slots(p, sh, cnt, row_count, row_map, first_eid, max_rec=None):
    """B 型 u16 槽位记录: [0][0][X u16][n1][0][n2][0]..[next_eid][0..]  (crash_tubes 等)."""
    s = sh + 24
    if u32(p, s) != 0 or u32(p, s + 4) != 0:
        return None
    rec = s + 8  # X 字段位置 (每记录常量, 语义待解)
    elems = {}
    for k in range(min(cnt, max_rec if max_rec else cnt)):
        slots = 0
        while slots < 12 and u16(p, rec + 2 + 4 * slots) != 0 and u16(p, rec + 2 + 4 * slots + 2) == 0:
            slots += 1
        nds = [u16(p, rec + 2 + 4 * j) for j in range(slots)] if slots else []
        if slots < 1 or not all(1 <= r <= row_count for r in nds):
            # 断链重扫: 元素分块存储, 块间有非元素数据
            nxt = None
            for j in range(rec + 2, min(rec + 50000, len(p) - 8)):
                if not (u16(p, j) != 0 and u16(p, j + 2) != 0 and u16(p, j + 4) == 0
                        and u16(p, j + 6) != 0 and u16(p, j + 8) == 0):
                    continue
                t_slots = 0
                while t_slots < 12 and u16(p, j + 2 + 4 * t_slots) != 0 and u16(p, j + 2 + 4 * t_slots + 2) == 0:
                    t_slots += 1
                t_nds = [u16(p, j + 2 + 4 * t) for t in range(t_slots)] if t_slots else []
                if not t_slots or not all(1 <= r <= row_count for r in t_nds):
                    continue
                t_ne = u16(p, j + 2 + 4 * t_slots + 4)
                if t_ne != first_eid + k + 2:
                    continue
                nxt = j
                break
            if nxt is None:
                break
            rec = nxt
            slots = 0
            while slots < 12 and u16(p, rec + 2 + 4 * slots) != 0 and u16(p, rec + 2 + 4 * slots + 2) == 0:
                slots += 1
            if slots < 1:
                break
            nds = [u16(p, rec + 2 + 4 * j) for j in range(slots)]
            if not all(1 <= r <= row_count for r in nds):
                break
        eid = first_eid + k
        _rec_add(elems, eid, 0, [row_map.get(r, r) for r in nds])
        if k >= min(cnt, max_rec if max_rec else cnt) - 1:
            break  # 末条: 直接结束 (末条已存)
        nxt = None
        for j in range(rec + 2 + 4 * slots + 8, min(rec + 50000, len(p) - 8)):
            if not (u16(p, j) != 0 and u16(p, j + 2) != 0 and u16(p, j + 4) == 0
                    and u16(p, j + 6) != 0 and u16(p, j + 8) == 0):
                continue
            t_slots = 0
            while t_slots < 12 and u16(p, j + 2 + 4 * t_slots) != 0 and u16(p, j + 2 + 4 * t_slots + 2) == 0:
                t_slots += 1
            t_nds = [u16(p, j + 2 + 4 * t) for t in range(t_slots)] if t_slots else []
            if not t_slots or not all(1 <= r <= row_count for r in t_nds):
                continue
            t_ne = u16(p, j + 2 + 4 * t_slots + 4)
            # 允许前向链 (t_ne >= expected): 删除元素产生 eid 空洞 (下一条跳号)
            # 只要链仍前向推进即视为同一元素段继续; 末 5 条允许任意 next_eid (链尾 0).
            if t_ne < first_eid + k + 2 and not (k >= min(cnt, max_rec if max_rec else cnt) - 5):
                continue
            nxt = j
            break
        if nxt is None:
            break
        rec = nxt
    return elems

def _parse_b_u16rows(p, sh, cnt, row_count, row_map, first_eid, max_rec=None):
    """B 型 u16 行号记录 (config 60 等): [0][0][flag u16][(row,0) u16 对 ...].

    与 crash_tubes 槽位不同: 行号 u16 与 0 交错, 无下一条 eid 字段;
    下一条记录以 [0][0][flag] 定位.
    """
    s = sh + 24
    if u32(p, s) != 0 or u32(p, s + 4) != 0:
        return None
    elems = {}
    rec = s
    eid = first_eid
    for k in range(min(cnt, max_rec if max_rec else cnt)):
        flag = u16(p, rec + 8)
        cfg = flag - 256
        if not (1 <= cfg <= 100):
            break
        nds = []
        j = 0
        while j < 12:
            r = u16(p, rec + 10 + 4 * j)
            z = u16(p, rec + 12 + 4 * j)
            if r == 0 or z != 0 or not (1 <= r <= row_count):
                break
            nds.append(r)
            j += 1
        if not nds:
            break
        _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in nds])
        eid += 1
        # 找下一条记录: [0][0][flag 300-500]
        nxt = None
        for q in range(rec + 10 + 4 * len(nds), min(rec + 400, len(p) - 10)):
            if u32(p, q) == 0 and u32(p, q + 4) == 0 and 300 <= u16(p, q + 8) <= 500:
                nxt = q
                break
        if nxt is None:
            break
        rec = nxt
    return elems

def _parse_a_geom(p, sh, hi, cnt, row_count, row_map, max_rec=None):
    """A 型几何复合记录 (Y=3, config 104 等): 无 CONST 锚, 含显示坐标.

    记录布局 (间距 71-74B, 0x1a040be4 头):
      [+0] 0x1a040be4  [+4] 8  [+8] ASCII 名  [+16] 0x0a040be6  [+20] 2
      [+24] 0x12040084 [+28..35] 坐标 [+36] eid  [+40][+44] 0
      [+48+4i] (u16 属性, u16 节点行号)  i=0..n-1
    0x1a040be4 在坐标数据中大量误匹配, 用 记录间距(68-80) + eid 合法 +
    节点行号合法 三重验证过滤.
    """
    MARK = b"\xe4\x0b\x04\x1a"
    elems = {}
    prev = None
    j = sh + 24
    n_parsed = 0
    while j < hi:
        j = p.find(MARK, j, hi)
        if j < 0:
            break
        if prev is not None and not (68 <= j - prev <= 80):
            j += 1
            continue  # 间距异常 -> 误匹配
        L = u32(p, j + 4)  # ASCII 名长度 (8 = 标准, 5 = 短名变体)
        eid_off = 28 + L
        eid = u32(p, j + eid_off)
        nds = []
        if L == 8:
            for i in range(8):
                r = u32(p, j + eid_off + 12 + 4 * i) >> 16
                if not (1 <= r <= row_count):
                    break
                nds.append(r)
        else:
            # 短名变体: 行号为 u16 [行号, 0] 对 @ eid_off+14+4i
            for i in range(8):
                r = u16(p, j + eid_off + 14 + 4 * i)
                if not (1 <= r <= row_count):
                    break
                nds.append(r)
        if nds and 0 < eid < 10_000_000:
            _rec_add(elems, eid, 104, [row_map.get(r, r) for r in nds])
            n_parsed += 1
            if max_rec and n_parsed >= max_rec:
                break
        prev = j  # 坏记录也推进 prev, 避免间距基准卡死酿成连锁跳过
        j += 1
    return elems

def _parse_v13_elems(p, sh, cnt, row_count, row_map, max_rec=None):
    """v13.03 Y=4 元素段 (chapter2_2): 记录 76B 间距.

    记录: [eid][(2,996)][(3076,1)][(0,eid)][0][0][(0,seg)][行号...][0][4][段间标记][CONST].
    行号 @+28 起遇 0 停; 3 个 -> config 103, 4 个 -> config 104.
    """
    MARK = b"\xf5\x1f\x24\x70"
    elems = {}
    rec = sh + 52
    for k in range(min(cnt, max_rec if max_rec else cnt)):
        eid = u32(p, rec)
        if not (0 < eid < 10_000_000):
            # 重定位: 找下一条记录头 (CONST 后 eid)
            j = p.find(MARK, rec, min(rec + 200, len(p)))
            if j < 0:
                break
            rec = j + 4
            eid = u32(p, rec)
            if not (0 < eid < 10_000_000):
                break
        rows = []
        i = 0
        while i < 12 and 1 <= u32(p, rec + 28 + 4 * i) <= row_count:
            rows.append(u32(p, rec + 28 + 4 * i))
            i += 1
        if not rows:
            break
        cfg = 104 if len(rows) == 4 else (103 if len(rows) == 3 else 0)
        if cfg:
            _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in rows])
        j = p.find(MARK, rec + 20, min(rec + 200, len(p)))
        if j < 0:
            break
        rec = j + 4
    return elems

def _parse_y7_elems(p, sh, cnt, row_count, row_map, max_rec=None):
    """truck Y=7 段: config-3 (112B) 与 config-60 (176B).

    config-3: [CONST][存储ID@+4][列表数据][eid@+82][(259<<16)@+92][节点1@+96][节点2@+100].
    config-60: [CONST][存储ID@+4][...][eid@+58][(316<<16)@+68][节点1@+72][节点2@+76][节点3@+152].
    """
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s
            break
    if anchor is None:
        return None
    elems = {}
    rec = anchor
    for k in range(min(cnt, max_rec if max_rec else cnt)):
        tag3 = u32(p, rec + 92) >> 16
        tag60 = u32(p, rec + 68) >> 16
        if tag3 == 259:
            eid = (u16(p, rec + 84) << 16) | u16(p, rec + 82)
            nds = [u32(p, rec + 96), u32(p, rec + 100)]
            cfg = 3
            stride = 112
        elif tag60 == 316:
            eid = (u16(p, rec + 60) << 16) | u16(p, rec + 58)
            nds = [u32(p, rec + 72), u32(p, rec + 76), u32(p, rec + 164)]
            cfg = 60
            stride = 176
        else:
            break
        if not (0 < eid < 10_000_000):
            break
        if not all(1 <= r <= row_count for r in nds):
            break
        _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in nds])
        rec += stride
    return elems

def _parse_y4_elems(p, sh, cnt, row_count, row_map, max_rec=None):
    """truck Y=4 特殊元素段: config-55 (变长) 与 config-60 (152B 定长).

    config-55: [CONST][...][eid@+42][(567<<16)@+52][n@+56][节点1@+60][1][123456][节点2..n+1@+72][4]
              节点数=n+1, 记录长=76+4*n.
    config-60: [CONST][...][eid@+34][(316<<16)@+44][节点1@+48][节点2@+52], 记录长=152.
    """
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s
            break
    if anchor is None:
        return None
    elems = {}
    rec = anchor
    for k in range(min(cnt, max_rec if max_rec else cnt)):
        tag55 = u32(p, rec + 52) >> 16
        tag60 = u32(p, rec + 44) >> 16
        if tag55 == 567:
            eid = (u16(p, rec + 44) << 16) | u16(p, rec + 42)
            n = u32(p, rec + 56)
            if not (0 <= n <= 100):
                break
            nds = [u32(p, rec + 60)]
            for i in range(n):
                nds.append(u32(p, rec + 72 + 4 * i))
            cfg = 55
            stride = 76 + 4 * n
        elif tag55 == 277:
            # config 21: 2 节点, 80B
            eid = (u16(p, rec + 44) << 16) | u16(p, rec + 42)
            nds = [u32(p, rec + 56), u32(p, rec + 60)]
            cfg = 21
            stride = 80
        elif tag55 in (278, 534, 790, 1302):
            # config 22: tag 278→2 节点, tag 534/790/1302→4 节点, 100B
            eid = (u16(p, rec + 44) << 16) | u16(p, rec + 42)
            nn = 2 if tag55 == 278 else 4
            nds = [u32(p, rec + 56 + 4 * i) for i in range(nn)]
            cfg = 22
            stride = 100
        elif tag60 == 316:
            eid = (u16(p, rec + 36) << 16) | u16(p, rec + 34)
            nds = [u32(p, rec + 48), u32(p, rec + 52)]
            cfg = 60
            stride = 152
        else:
            break
        if not (0 < eid < 10_000_000):
            break
        if not all(1 <= r <= row_count for r in nds):
            break
        _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in nds])
        rec += stride
    return elems


def _parse_ansys2d_elems(p, sh, cnt, row_count, row_map, max_rec=None):
    """ansys 2D 教程 Y=2 段: 头 0x30200B1F, 记录 62B 固定.

    记录: [0x30200B1F][7][0][0x30200B21][7][1][eid@+24][0][0][?][行号×4 @+38][0][2].
    行号 = u32 @+38 连续 (遇 0 停); cfg 由行号数推 (4->104, 3->103).
    """
    pat = b"\x1f\x0b\x20\x30"
    elems = {}
    j = sh + 24
    n = 0
    lim = min(cnt, max_rec if max_rec else cnt)
    while n < lim:
        j = p.find(pat, j, min(j + 200, len(p)))
        if j < 0:
            break
        eid = u32(p, j + 24)
        # flag @+36 (u16) 指示 config (476->220 8节点, 360->104 4节点); 无 flag 默认 4 节点 cfg 104
        flag = u16(p, j + 36)
        if 300 <= flag <= 500:
            nrow = CONFIG_NODES.get(flag - 256, 4)
            cfg = flag - 256
        else:
            nrow = 4
            cfg = 104
        rows = []
        for i in range(nrow):
            r = u16(p, j + 38 + 4 * i)
            if not (1 <= r <= row_count):
                break
            rows.append(r)
        if rows and 0 < eid < 10_000_000 and len(rows) == nrow:
            _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in rows])
        j += 62
        n += 1
    # 补漏: 主链之外的记录 (如 wizard_2d eid 58 @ sh+82) — 独立 find 全部头补缺失 eid
    j = sh + 24
    while True:
        j = p.find(pat, j, min(sh + 40 * 70, len(p)))
        if j < 0:
            break
        eid = u32(p, j + 24)
        if 0 < eid < 10_000_000:
            rows = []
            for i in range(8):
                r = u32(p, j + 38 + 4 * i)
                if not (1 <= r <= row_count):
                    break
                rows.append(r)
            if rows:
                cfg = 104 if len(rows) == 4 else (103 if len(rows) == 3 else 0)
                if cfg:
                    _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in rows])
        j += 1
    # v12 变体 (manager_2d seg2 eid 203..307): 38B 记录, eid@+0, 行号 u16 @+14+4i
    # 从最后一个头之后开始扫 eid 递增 38B 流
    last_head = None
    jj = sh + 24
    while True:
        jj = p.find(pat, jj, min(sh + 40 * 70, len(p)))
        if jj < 0:
            break
        last_head = jj
        jj += 62
    if last_head is not None:
        rec = last_head + 62
        guard = 0
        while rec + 38 <= len(p) and guard < cnt * 2:
            eid = u32(p, rec)
            rows = []
            for i in range(4):
                r = u16(p, rec + 14 + 4 * i)
                if not (1 <= r <= row_count):
                    break
                rows.append(r)
            if 0 < eid < 10_000_000 and len(rows) == 4:
                _rec_add(elems, eid, 104, [row_map.get(r, r) for r in rows])
            rec += 38
            guard += 1
            if len(rows) < 4 and u32(p, rec) == 0:
                break
    return elems

def _parse_y2_c60(p, sh, cnt, row_count, row_map, max_rec=None):
    """SEAT_MODEL seg 29: Y=2 段 3 节点 config 60 (136B stride).

    记录: [CONST][存储ID@+4][...][eid@+18][...][316@+30][节点1@+32][节点2@+36]
          [...][节点3@+124]. tag 316 判别 (config 60).
    """
    rec = sh + 24
    if rec + 136 > len(p) or not is_const(u32(p, rec)):
        return None
    if u16(p, rec + 30) != 316:
        return None
    elems = {}
    limit = min(cnt, max_rec if max_rec else cnt)
    for k in range(limit):
        if rec + 136 > len(p) or not is_const(u32(p, rec)):
            break
        if u16(p, rec + 30) != 316:
            break
        eid = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
        nds = [u16(p, rec + 32), u16(p, rec + 36), u16(p, rec + 124)]
        if not (0 < eid < 10_000_000) or not all(1 <= r <= row_count for r in nds):
            break
        _rec_add(elems, eid, 60, [row_map.get(r, r) for r in nds])
        rec += 136
    return elems or None

def _parse_y0_elems(p, sh, cnt, row_count, row_map, max_rec=None):
    """geometry Y=0 元素段: 无 CONST 锚, u16 粒度变长记录, CONST 块分隔.

    记录布局 (长 22+4n 字节):
      [+0] eid u16  [+2..+10] 5×0 u16  [+12] marker u16 (低字节=config)
      [+14+4i] (0, 节点行号) u16 对 i=0..n-1  [+14+4n..+22+4n] 4×0 u16 尾
    config→节点数: 104→4, 103→3, 208→8, 206→6.
    CONST 块分隔: [CONST][first_eid u16][0 u16][16 u16] + 记录 (记录自身带 eid).
    """
    B = sh + 24
    elems = {}
    limit = min(cnt, max_rec if max_rec else cnt)
    k = 0
    while k < limit:
        if B + 10 <= len(p) and is_const(u32(p, B)):
            B += 10  # CONST + 块头 (6 字节)
            continue
        eid = u16(p, B)
        marker = u16(p, B + 12)
        cfg = marker & 0xFF
        n = CONFIG_NODES.get(cfg)
        if n is None:
            break
        nds = [u16(p, B + 14 + 4 * i) for i in range(n)]
        if not (0 < eid < 10_000_000) or not all(1 <= r <= row_count for r in nds):
            break
        _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in nds])
        B += 22 + 4 * n
        k += 1
    return elems

def _parse_y6_c3(p, sh, cnt, row_count, row_map, max_rec=None):
    """car_section Y=6 段 config 3 (rigid, tag 259, 2 节点, 100B stride).

    Y=6 段有 list 头 (60B), CONST 锚在 sh+84 之后; _parse_a_type 的 sh+16..80 扫不到.
    记录: [CONST][eid@+4][...][259@+22][节点1@+24][节点2@+28]. tag 316 (config 60,
    RBE3/rigid wall) 非元素, 跳过.
    """
    anchor = None
    for s in range(sh + 16, sh + 240):
        if is_const(u32(p, s)):
            anchor = s
            break
    if anchor is None:
        return None
    tag = u16(p, anchor + 22)
    if tag == 259:
        stride, nrow, noff = 100, 2, 24
    elif tag == 316:
        # car_section Y=6 rigid: 168B 记录, eid=存储ID@+4, 行号@+24/+28/+32 (3 节点)
        stride, nrow, noff = 168, 3, 24
    else:
        return None
    elems = {}
    rec = anchor
    limit = min(cnt, max_rec if max_rec else cnt)
    for k in range(limit):
        if rec + 32 > len(p) or not is_const(u32(p, rec)):
            break
        if u16(p, rec + 22) != tag:
            break
        eid = u16(p, rec + 4)
        nds = [u16(p, rec + noff + 4 * i) for i in range(nrow)]
        if not (0 < eid < 10_000_000) or not all(1 <= r <= row_count for r in nds):
            break
        _rec_add(elems, eid, 3, [row_map.get(r, r) for r in nds])
        rec += stride
    return elems or None

def _parse_cfg55_mpc(p, sh, cnt, row_count, row_map, max_rec=None):
    """Family-1 family record (config 22/55), two variants:
    - seat-style (0x70241FF5; v11): eid=u16@+18, cfg=u16@+30-512, nslave=@+32, master@+36, slave@+48
    - hook-style (0x70541FF5; v12):  eid=u32@+4,  cfg=u16@+22-256, ncount=@+24, node@+40"""
    s = None
    for off in range(sh + 16, min(sh + 80, len(p) - 4)):
        if is_const(u32(p, off)):
            s = off
            break
    if s is None:
        return None
    elems = {}
    rec = s
    limit = min(cnt, max_rec if max_rec else cnt)
    for k in range(limit):
        if not is_const(u32(p, rec)):
            nxt = None
            j = p.find(b"\xf5\x1f", rec + 4, min(rec + 200, len(p) - 2))
            while j >= 0:
                if is_const(u32(p, j)):
                    nxt = j
                    break
                j = p.find(b"\xf5\x1f", j + 1, min(rec + 200, len(p) - 2))
            if nxt is None:
                break
            rec = nxt
        const = u32(p, rec)
        eid = None; cfg = None; nds = None; tail = None
        if (const >> 16) == 0x7054:
            # hook-style (v12): eid@+4, cfg = u16@+22 - 256, ncount@+24, node@+40,+4
            e = u32(p, rec + 4)
            cc = u16(p, rec + 22) - 256
            ncount = u32(p, rec + 24)
            if 0 < e < 10_000_000 and 1 <= cc <= 100 and 1 <= ncount <= 2000:
                ns = [u32(p, rec + 40 + 4 * t) for t in range(ncount)]
                if all(1 <= r <= row_count for r in ns):
                    eid, cfg, nds, tail = e, cc, ns, rec + 40 + 4 * ncount
        elif (const >> 16) == 0x7024:
            # seat-style (v11): eid=u16@+18, cfg=u16@+30-512
            e = u16(p, rec + 18)
            cc = u16(p, rec + 30) - 512
            if cc == 55:
                nslave = u32(p, rec + 32)
                master = u32(p, rec + 36)
                if 0 < e < 10_000_000 and 1 <= master <= row_count and 0 <= nslave <= 60:
                    slaves = [u32(p, rec + 48 + 4 * t) for t in range(nslave)]
                    if all(1 <= r <= row_count for r in slaves):
                        eid, cfg, nds, tail = e, cc, [master]+slaves, rec + 48 + 4 * nslave
            else:
                # fixed node sequence @+32,+4 until 0/out-of-range (config 22 etc)
                ncfg = 0
                while ncfg < 20 and rec + 32 + 4 * ncfg + 4 <= len(p):
                    r = u32(p, rec + 32 + 4 * ncfg)
                    if not (1 <= r <= row_count):
                        break
                    ncfg += 1
                if 0 < e < 10_000_000 and ncfg >= 1 and 1 <= cc <= 100:
                    eid, cfg, nds, tail = e, cc, [u32(p, rec + 32 + 4 * t) for t in range(ncfg)], rec + 32 + 4 * ncfg
        if eid is None or cfg is None or nds is None or tail is None:
            break
        _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in nds])
        nxt = None
        j = p.find(b"\xf5\x1f", tail, min(tail + 120, len(p) - 2))
        while j >= 0:
            if is_const(u32(p, j)):
                nxt = j
                break
            j = p.find(b"\xf5\x1f", j + 1, min(tail + 120, len(p) - 2))
        if nxt is None:
            break
        rec = nxt
    return elems or None

def decode_elements(p, row_map, row_count, max_rec=None):
    segs = find_elem_segments(p)
    if not segs:
        return None
    records = []
    for (sh, segid, cfg71, cnt, X, Y) in segs:
        got = None
        if X == 3:
            if Y == 0:
                # geometry Y=0 段: u16 变长记录 + CONST 块分隔 (无标准 CONST 锚)
                got = _parse_y0_elems(p, sh, cnt, row_count, row_map, max_rec=max_rec)
            elif Y == 2:
                # SEAT_MODEL seg 29: 3 节点 config 60 (tag 316) 优先于 A 型 (后者读到存储 ID)
                got = _parse_y2_c60(p, sh, cnt, row_count, row_map, max_rec=max_rec)
                if got is None:
                    got = _parse_a_type(p, sh, cnt, row_count, row_map, max_rec=max_rec)
                if got is None or len(got) < 2:
                    got_a = _parse_ansys2d_elems(p, sh, cnt, row_count, row_map, max_rec=max_rec)
                    if got_a and (got is None or len(got_a) > len(got)):
                        got = got_a
                # Family-1 MPC 变长记录 (config 55): 覆盖 seat 等 seg6/seg7 高 eid 尾段
                got_m = _parse_cfg55_mpc(p, sh, cnt, row_count, row_map, max_rec=max_rec)
                if got_m and len(got_m) > len(got or {}):
                    got = got_m
            elif Y == 6:
                # car_section Y=6: config 3 rigid (tag 259); tag 316/277 非元素跳过
                got = _parse_y6_c3(p, sh, cnt, row_count, row_map, max_rec=max_rec)
            else:
                got = _parse_a_type(p, sh, cnt, row_count, row_map, max_rec=max_rec)
                # Y=1 等族: family-1 变长/固定节点记录 (hook/keyhole/channel/joints config 22/55)
                got_m = _parse_cfg55_mpc(p, sh, cnt, row_count, row_map, max_rec=max_rec)
                if got_m and len(got_m) > len(got or {}):
                    got = got_m
            if Y == 7:
                # truck Y=7 段 (config 3/60): 优先于 A 型 (后者读到存储 ID)
                got7 = _parse_y7_elems(p, sh, cnt, row_count, row_map, max_rec=max_rec)
                if got7:
                    got = got7
            if Y == 4:
                # truck Y=4 特殊元素段 (config 55/60, CONST 锚 + tag): 优先于 A 型 (后者读到存储 ID)
                got4 = _parse_y4_elems(p, sh, cnt, row_count, row_map, max_rec=max_rec)
                if got4:
                    got = got4
                elif got is None:
                    # v13.03 Y=4 元素段 (chapter2_2)
                    got = _parse_v13_elems(p, sh, cnt, row_count, row_map, max_rec=max_rec)
            if Y == 3:
                # Y=3 几何复合记录 (无 CONST 锚): 与 A 型并行取多 (A 型对 Y=3 部分成功会掩盖 geom)
                nxt_sh = None
                for (sh2, *_rest) in segs:
                    if sh2 > sh:
                        nxt_sh = sh2
                        break
                hi = nxt_sh if nxt_sh else len(p)
                got_g = _parse_a_geom(p, sh, hi, cnt, row_count, row_map, max_rec=max_rec)
                if got_g and (got is None or len(got_g) > len(got)):
                    got = got_g
        else:
            got = _parse_b_type(p, sh, cnt, row_count, row_map, Y, max_rec=max_rec)
            got2 = _parse_b_slots(p, sh, cnt, row_count, row_map, Y, max_rec=max_rec)
            got3 = _parse_b_u16rows(p, sh, cnt, row_count, row_map, Y, max_rec=max_rec)
            if got2 and (got is None or len(got2) > len(got)):
                got = got2
            if got3 and (got is None or len(got3) > len(got)):
                got = got3
        if got:
            records.extend((eid, cfg, nds) for eid, recs in got.items() for (cfg, nds) in recs)
    return records or None

# ---------------------------------------------------------------------------
# 显示点 / 几何点
# ---------------------------------------------------------------------------
def parse_display_points(p):
    points = {}
    marks = [i for i in range(len(p) - 8) if u32(p, i) == MARK_GEOM]
    for m in marks:
        off = u32(p, m + 4)
        if off >= len(p):
            continue
        best = None
        for start in range(off, min(off + 0x40, len(p) - 52)):
            ok = True
            for k in range(10):
                rec = start + k * 52
                if rec + 52 > len(p):
                    ok = False; break
                x, y, z = d64(p, rec), d64(p, rec + 8), d64(p, rec + 16)
                if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
                    ok = False; break
            if not ok:
                continue
            score = sum(1 for k in range(10) if 0 < u32(p, start + k * 52 + 40) < 1e6)
            if best is None or score > best[0]:
                best = (score, start)
        if not best or best[0] < 3:
            continue
        base = best[1]
        k = 0
        while base + 52 <= len(p) and k < 200000:
            rec = base + k * 52
            x, y, z = d64(p, rec), d64(p, rec + 8), d64(p, rec + 16)
            rid = u32(p, rec + 40)
            if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
                break
            if 0 < rid < 1e6:
                points[rid] = DisplayPoint(rid, x, y, z)
            k += 1
    return points

def parse_geo_points_variant_b(p, node_ids=None):
    OFFSETS = (-249, -145, -93, -41, 15)
    n = len(p)
    results = {}
    i = 0
    while i < n - 8:
        v = u32(p, i)
        if 1 <= v <= 10_000_000 and u32(p, i + 4) == 1 and v not in results and (not node_ids or v not in node_ids):
            best = None
            for off in OFFSETS:
                j = i + off
                if 0 <= j and j + 24 <= n:
                    x, y, z = d64(p, j), d64(p, j + 8), d64(p, j + 16)
                    if abs(x) < 1e5 and abs(y) < 1e5 and abs(z) < 1e5 and abs(x) > 1 and abs(y) > 1:
                        if abs(y - 2.063) < 1e-3:
                            continue
                        s = 0
                        if abs(z - round(z)) < 1e-4:
                            s += 10
                        for dd in (52, -52, 104, -104):
                            j2 = j + dd
                            if 0 <= j2 and j2 + 24 <= n:
                                x2, y2, z2 = d64(p, j2), d64(p, j2 + 8), d64(p, j2 + 16)
                                if abs(x2 - x) < 1e-4 and abs(y2 - y) < 1e-4 and abs(z2 - z) < 1e-4:
                                    s += 20
                                    break
                        if best is None or s > best[0]:
                            best = (s, j, x, y, z)
            if best and best[0] >= 20:
                results[v] = GeoPoint(v, best[2], best[3], best[4])
            i += 8
        else:
            i += 1
    return results

# ---------------------------------------------------------------------------
# family-1 核心记录全局扫描 (v14+): (701|686)+2596 模式
# ---------------------------------------------------------------------------
def _scan_family1_cores(p, row_map, row_count):
    """全局扫描 family-1 核心记录, 覆盖 Y=2 段全部元素.

    标记: u16=701/686 后接 u16=2596; 记录相对标记 q:
      eid = u16(q+8) | u16(q+10)<<16; flag = u32(q+18);
      cfg = flag>>16 (300..500); 节点行号 u32 @q+22 起, 遇 0 结束.
    返回 [(eid, config, (row, ...)), ...] 列表.
    同一 eid 可出现多条 (shell/solid/rigid 合法重复), 仅去除完全相同记录
    (同 eid+config+rows, 扫描重叠产生的同一条).
    """
    import struct
    recs = []
    seen = set()
    for MARK in (struct.pack("<HH", 701, 2596), struct.pack("<HH", 686, 2596)):
        j = 0
        while True:
            j = p.find(MARK, j)
            if j < 0:
                break
            q = j
            eid = u16(p, q + 8) | (u16(p, q + 10) << 16)
            flag = u32(p, q + 18)
            cfg = flag >> 16
            if 300 <= cfg <= 500 and (flag & 0xFFFF) == 0 and 1 <= eid <= 10_000_000:
                rows = []
                k = q + 22
                while u32(p, k) != 0 and len(rows) < 20:
                    rows.append(u32(p, k))
                    k += 4
                if 1 <= len(rows) <= 20 and all(1 <= r <= row_count for r in rows):
                    key = (eid, cfg - 256, tuple(rows))
                    if key not in seen:
                        seen.add(key)
                        recs.append(key)
            j += 2
    return recs

# ---------------------------------------------------------------------------
# 特殊元素段 (Y≠2 段): config 1/3/21/22/55/61, 记录 [eid][0][k][tag u16] + 行号
# ---------------------------------------------------------------------------
SPECIAL_ELEM_TAGS = {257: 1, 259: 3, 277: 21, 278: 22, 534: 22,
                     790: 22, 1558: 22, 567: 55, 317: 61}

def _parse_special_elems(p, row_map, row_count, scan_from=0):
    """解析 Y≠2 段的杂项特殊元素 (不在 family-1 core 中).

    记录布局: [eid u32][0][k=2|3][tag u16][节点行号区].
      - config 55: [tag=567][n u16] 后接 u32 序列; 节点行号 =
        (下一 u32 低16位 << 16) | 当前 u32 高16位; 节点数 = n+1.
      - config 1: 单节点 (lo u16 @+14, hi u16 @+16) -> (hi<<16)|lo.
      - 其他 (config 3/21/22/61): 每节点 (lo u16 @+14+4i, hi u16 @+16+4i),
        lo==0 结束. 行号低 16 位存高 u16 位 (行号 > 65535 时截断).
    返回 [(eid, config, (row, ...)), ...] 列表 (保留同 eid 合法重复, 去完全相同记录).
    """
    recs = []
    seen = set()
    ZERO4 = b"\x00\x00\x00\x00"
    j = max(scan_from, 0)
    n = len(p)
    while True:
        j = p.find(ZERO4, j)
        if j < 0:
            break
        eid = u32(p, j - 4) if j >= 4 else 0
        if not (1 <= eid <= 10_000_000):
            j += 1
            continue
        k = u32(p, j + 4)
        if k not in (2, 3):
            j += 1
            continue
        tag = u16(p, j + 8)
        cfg = SPECIAL_ELEM_TAGS.get(tag)
        if cfg is None:
            j += 1
            continue
        h = j - 4
        rows = []
        if cfg == 55:
            nn = u16(p, h + 14)
            if 0 <= nn <= 100:
                rows.append(((u32(p, h + 20) & 0xFFFF) << 16) | (u32(p, h + 16) >> 16))
                for i in range(1, nn + 1):
                    low = u32(p, h + 28 + 4 * (i - 1)) >> 16
                    high = u32(p, h + 32 + 4 * (i - 1)) & 0xFFFF
                    rows.append((high << 16) | low)
        elif cfg == 1:
            lo = u16(p, h + 14)
            hi = u16(p, h + 16)
            rows = [(hi << 16) | lo]
        else:
            i = 0
            while len(rows) <= 100:
                lo = u16(p, h + 14 + 4 * i)
                if lo == 0:
                    break
                hi = u16(p, h + 16 + 4 * i)
                rows.append((hi << 16) | lo)
                i += 1
        if rows and all(1 <= r <= row_count for r in rows):
            key = (eid, cfg, tuple(rows))
            if key not in seen:
                seen.add(key)
                recs.append(key)
        j += 1
    return recs

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
def _elems_to_list(recs):
    """将 [(eid, config, nodes), ...] 合并为 list[Elem] (保留同 eid 合法重复,
    仅去除完全相同的记录, 以免扫描重叠重复计数)."""
    out = []
    seen = set()
    for eid, cfg, nds in recs:
        key = (eid, cfg, tuple(nds))
        if key in seen:
            continue
        seen.add(key)
        out.append(Elem(id=eid, config=cfg, nodes=list(nds)))
    return out

def decode(path):
    p = load_payload(path)
    model = HMModel(db_version=d64(p, 4))
    ns = find_node_section(p)
    ns_list = []
    nodes = {}
    if d64(p, 4) >= 14:
        # v14+ (v17): 统一扫描收集全部节点段 (含小段, 已重叠修正)
        for ens in _collect_node_segments(p):
            n2, b2 = parse_nodes(p, ens)
            if n2:
                nodes.update(n2)
                ns_list.append(ens)
    else:
        # v11-13: [136] 头; 失败时结构扫描兜底
        if ns:
            n1, b1 = parse_nodes(p, ns)
            if n1:
                nodes = n1
                ns_list.append(ns)
        need = max(10, ns[1] * 0.85) if ns else 10
        if len(nodes) < need:
            for ens in find_node_section_struct(p, multi=True):
                if ens[1] < 50:
                    continue  # 假段过滤
                if any(abs(ens[2] - c[2]) < 32 for c in ns_list):
                    continue  # 同段跳过
                n2, b2 = parse_nodes(p, ens)
                if n2:
                    nodes.update(n2)
                    ns_list.append(ens)
        # 补充小节点段 (多布局: 52/56/68/92B), 如 molding1 92B 主段 + 56B 尾段;
        # 仅扫描主段之后 512KB 区域, 且 nid > 主段节点数 (排除元素区假段)
        if ns_list:
            main = ns_list[0]
            m_end = main[2] + len(nodes) * main[3]
            excl = [(c[2], c[2] + 8) for c in ns_list]
            for ens in _scan_extra_node_segs(p, excl, lo=max(0, m_end - 256),
                                             hi=m_end + 512 * 1024, min_nid=len(nodes) - 16):
                if any(abs(ens[2] - c[2]) < 32 for c in ns_list):
                    continue
                n2, b2 = parse_nodes(p, ens)
                if n2:
                    nodes.update(n2)
                    ns_list.append(ens)
        # v13.03 96B 节点段 (0x10200bc7 标记), 如 chapter2_2 — 无条件补充 (与主段合并)
        for ens in _scan_v13_node_segs(p):
            if any(abs(ens[2] - c[2]) < 32 for c in ns_list):
                continue
            n2, b2 = parse_nodes(p, ens)
            if n2:
                nodes.update(n2)
                ns_list.append(ens)
    if ns_list and nodes:
        model.node_section = ns_list[0][0]
        model.node_count = len(nodes)
        model.nodes = nodes
        if nodes:
            # 多段行号续接构建全局 row_map
            row_map = {}
            row = 0
            for cfg in sorted(ns_list, key=lambda s: s[2]):
                hi, count, base2, stride, idoff, chain = cfg
                if chain:
                    for k in range(count):
                        row += 1
                        row_map[row] = row
                else:
                    xoff = 24 if stride == 96 else 12
                    for k in range(count):
                        rec = base2 + k * stride
                        if rec + stride > len(p):
                            break
                        nid = u32(p, rec + idoff)
                        x = d64(p, rec + xoff)
                        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9):
                            break
                        row += 1
                        row_map[row] = nid
            main_recs = None  # list[(eid, config, nodes)] 主路径记录
            if d64(p, 4) >= 14:
                # v14+ (v17): family-1 核心记录 + 特殊元素段 (均为去除完全重复的 record 列表,
                # 保留同 eid 的 shell/solid/rigid 合法重复)
                fam = _scan_family1_cores(p, row_map, len(nodes))
                if fam:
                    scan_from = max((s[2] + s[1] * s[3]) for s in ns_list) if ns_list else 0
                    spec = _parse_special_elems(p, row_map, len(nodes), scan_from=scan_from)
                    all_recs = fam + (spec or [])
                    # 行号 -> 节点 ID
                    main_recs = [(eid, cfg, [row_map.get(r, r) for r in rows])
                                 for eid, cfg, rows in all_recs]
            else:
                # v11-13: 分段解析 (A 型 CONST 锚 / B 型链式, 含 family-1 布局检测)
                de = decode_elements(p, row_map, len(row_map)) or []
                main_recs = list(de)
            main_elems = _elems_to_list(main_recs) if main_recs else []
            ws_b = _parse_ws_variant_b(p, row_map, len(nodes) if nodes else 0)
            wsb_elems = list(ws_b.values()) if ws_b else []
            if wsb_elems and (not main_elems or len(wsb_elems) > len(main_elems)):
                model.elements = wsb_elems
                model.elem_count = len(wsb_elems)
                model.element_variant = "WS-B"
            elif main_elems:
                model.elements = main_elems
                model.elem_count = len(main_elems)
                model.element_variant = "segmented"
            model.display_points = parse_display_points(p)
            if not model.elements:
                model.geo_points = parse_geo_points_variant_b(p, set(model.nodes))
    return model

def _parse_ws_variant_b(p, row_map, row_count):
    elems = {}
    pat = b"\x00\x00\x00\x00\x00\x00\x00\x00"
    start = 0
    while True:
        i = p.find(pat, start)
        if i < 0:
            break
        eid_pos = i - 4
        if eid_pos >= 0 and eid_pos + 30 <= len(p):
            eid = u32(p, eid_pos)
            flag = u16(p, eid_pos + 12)
            if 100000 <= eid <= 10_000_000 and flag in (359, 460):
                refs = [u16(p, eid_pos + 14), u16(p, eid_pos + 18), u16(p, eid_pos + 22), u16(p, eid_pos + 26)]
                if all(r <= row_count for r in refs):
                    nodes = [row_map.get(r, 0) for r in refs if r != 0]
                    if eid not in elems:
                        elems[eid] = Elem(eid, nodes, flag - 256)
        start = i + 1
    return elems

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        m = decode(path)
        print(f"{path.split('/')[-1]}: db={m.db_version} nodes={len(m.nodes)}/{m.node_count} "
              f"elems={len(m.elements)}/{m.elem_count} display={len(m.display_points)} "
              f"geopts={len(m.geo_points)} var={m.element_variant}")