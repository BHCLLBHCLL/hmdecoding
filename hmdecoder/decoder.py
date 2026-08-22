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
    elements: dict = field(default_factory=dict)
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
                if len(seen) < max(5, ok // 2):
                    continue
                if ok > 30 and (best is None or ok > best[0]):
                    best = (ok, (hi, count, base, stride, idoff, chain))
    if best and best[0] >= 45:
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

def parse_nodes(p, cfg):
    hi, count, base, stride, idoff, chain = cfg
    nodes = {}
    for k in range(count):
        rec = base + k * stride
        if rec + stride > len(p):
            break
        if chain:
            nid = u32(p, rec + 44) - 1
            x, y, z = d64(p, rec), d64(p, rec + 8), d64(p, rec + 16)
        else:
            nid = u32(p, rec + idoff)
            x, y, z = d64(p, rec + 12), d64(p, rec + 20), d64(p, rec + 28)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9 and abs(y) < 1e9 and abs(z) < 1e9):
            break  # 记录流结束 (count 字段可能含虚值)
        nodes[nid] = Node(nid, x, y, z)
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
                201: 3, 202: 3, 203: 3, 301: 6, 302: 8, 303: 6, 304: 8, 305: 10, 306: 12}

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
            eid = u32(p, rec + 4)
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
            # ---- v11 路径: flag<<16 u32 + u32 节点 ----
            prelens = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40] if d else [0]
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
            if got is None:
                ok = False; break
            fp, n, nds, config = got
            elems[eid] = (config, [row_map.get(r, r) for r in nds])
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
        elems[eid] = (config, [row_map.get(r, r) for r in nds])
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
        elems[eid] = (0, [row_map.get(r, r) for r in nds])
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
            if t_ne != first_eid + k + 2:
                continue
            nxt = j
            break
        if nxt is None:
            break
        rec = nxt
    return elems

def decode_elements(p, row_map, row_count, max_rec=None):
    segs = find_elem_segments(p)
    if not segs:
        return None
    elems = {}
    for (sh, segid, cfg71, cnt, X, Y) in segs:
        got = None
        if X == 3:
            got = _parse_a_type(p, sh, cnt, row_count, row_map, max_rec=max_rec)
        else:
            got = _parse_b_type(p, sh, cnt, row_count, row_map, Y, max_rec=max_rec)
            got2 = _parse_b_slots(p, sh, cnt, row_count, row_map, Y, max_rec=max_rec)
            if got2 and (got is None or len(got2) > len(got)):
                got = got2
        if got:
            elems.update(got)
    return elems or None

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
    返回 {eid: (config, (row, ...))}.
    """
    import struct
    elems = {}
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
                    elems.setdefault(eid, (cfg - 256, tuple(rows)))
            j += 2
    return elems

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
    返回 {eid: (config, [row, ...])}.
    """
    elems = {}
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
            elems.setdefault(eid, (cfg, tuple(rows)))
        j += 1
    return elems

# ---------------------------------------------------------------------------
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
        if len(nodes) < 10:
            for ens in find_node_section_struct(p, multi=True):
                if ens[1] < 50:
                    continue  # 假段过滤
                if any(abs(ens[2] - c[2]) < 32 for c in ns_list):
                    continue  # 同段跳过
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
                    for k in range(count):
                        rec = base2 + k * stride
                        if rec + stride > len(p):
                            break
                        nid = u32(p, rec + idoff)
                        x = d64(p, rec + 12)
                        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9):
                            break
                        row += 1
                        row_map[row] = nid
            elems = _scan_family1_cores(p, row_map, len(nodes))
            if elems:
                # 特殊元素段 (Y≠2 段) 补扫: 节点段之后的区域
                scan_from = max((s[2] + s[1] * s[3]) for s in ns_list) if ns_list else 0
                elems_spec = _parse_special_elems(p, row_map, len(nodes), scan_from=scan_from)
                if elems_spec:
                    elems.update(elems_spec)
                # 行号 -> 节点 ID
                elems = {eid: (cfg, [row_map.get(r, r) for r in rows])
                         for eid, (cfg, rows) in elems.items()}
            elems_b = _parse_ws_variant_b(p, row_map, ns[1])
            if elems_b and (not elems or len(elems_b) > len(elems)):
                model.elements = elems_b
                model.elem_count = len(elems_b)
                model.element_variant = "WS-B"
            elif elems:
                model.elements = elems
                model.elem_count = len(elems)
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