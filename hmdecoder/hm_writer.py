"""hm_writer — .hm 写端骨架 (M5.1 v0).

按 DEV_PLAN.md §5 M5 目标, 这是 .hm 写端的最小集. 仅支持:
  - 节点段: 52B 布局 A (db 11.x, [id][0][0][x][y][z][0x4], 7 字段)
  - 元素段: A 型锚 (CONST 0x70241FF5 + segid + count + X=3 + Y) + 元素记录
  - 包装: 12 字节前缀 (4 字节 0x00000000 + 8 字节包装版本 5.0 LE double) + gzip payload

不在范围内 (登记 NYI-M5-1):
  - collector (comps/mats/props/groups) 段
  - 几何点段 (M4.1 v3 段头签名)
  - 92B 节点 / 56B 节点 / 链式 56B 布局 (db 12+ / 14+)
  - 元素段 B 型 (链式 eid, X=2)
  - db >= 13 的多版本兼容

用法:
    from hmdecoder.decoder import decode
    from hmdecoder.hm_writer import encode_minimal_db11_05
    src = decode('input.hm')
    encode_minimal_db11_05(src, 'output.hm')
    # decode('output.hm') 应能读回相同节点坐标与单元 id (至少)

实现策略:
  1) 节点段固定为 [136] + count + 节点记录流;
     节点记录 52B 布局 A: [u32 id][u32 0][u32 0][f64 x][f64 y][f64 z][u32 0x4].
  2) 元素段 A 型锚:
     [997][segid(u32)][175][count(u32)][3(0x70241FF5)][...];
     每元素: [eid(u32)][cfg(u32)][len(nodes)(u32)][nodes u32...]
  3) 包装: 4 字节 0x00 + 8 字节 double 5.0 + gzip(payload)
"""
import gzip
import struct
from pathlib import Path

from .decoder import HMModel


# 节点段签名前缀 (与 find_node_section 一致)
NODE_SIG_BYTES = b"\x88\x00\x00\x00"  # 136 LE u32

# 元素段签名 (与 decode_elements 锚一致)
ELEM_SIG_997 = 997       # 段头标记
ELEM_SIG_175 = 175       # 段头第二标记
ELEM_CONST_A = 0x70241FF5  # A 型常量 (X=3, segid 锚)
ELEM_CONST_B = 0x70241FF5  # B 型用同一常量, 通过 X=2 区分


def _u32(v): return struct.pack("<I", v & 0xFFFFFFFF)
def _u64(v): return struct.pack("<Q", v & 0xFFFFFFFFFFFFFFFF)
def _f64(v): return struct.pack("<d", float(v))


def _serialize_nodes_db11_05_52A(m: HMModel) -> bytes:
    """写出节点段 (db 11.05 52B 布局 A). 仅适用于不含 display_points 影响.

    节点段格式:
        [u32 0x88][u32 count][u32 0x0]                  (12 字节段头 [136])
        ... 节点记录 (52B/rec, 共 count 条) ...
            [u32 id][u32 0][u32 0][f64 x][f64 y][f64 z][u32 0x4]

    注: db 11.05 真实样本的段头不一定是 [136][count] 这一简单形式, 这里按
    find_node_section 用的锚 0x88 (LE) = 136 写出.
    """
    nodes = sorted(m.nodes.values(), key=lambda n: n.id)
    buf = bytearray()
    # 段头: 锚 + count + 0 填充 (12 字节)
    buf += _u32(0x88)             # 锚 (LE 136)
    buf += _u32(len(nodes))       # count
    buf += _u32(0)                # 填充 (原段头常带 0)
    assert len(buf) == 12
    for n in nodes:
        rec = bytearray()
        rec += _u32(n.id)         # 4
        rec += _u32(0)            # 4
        rec += _u32(0)            # 4
        rec += _f64(n.x)          # 8
        rec += _f64(n.y)          # 8
        rec += _f64(n.z)          # 8
        rec += _u32(0x4)          # 4
        rec += b"\x00" * 12       # 12B 尾填充 (真实样本常含 0)
        assert len(rec) == 52, f"rec len drift: {len(rec)}"
        buf += rec
    return bytes(buf)


def _serialize_elements_A_anchor(m: HMModel, segid: int = 0) -> bytes:
    """写出元素段 (A 型锚).

    元素段格式:
        [u32 997][u32 segid][u32 175][u32 count][u32 X (3)][... X 字段重复 ...]
        ... 元素记录 ...
            [u32 eid][u32 cfg][u32 len(nodes)][u32 node_i × len]

    注: 这里采用最简化锚, 接受部分样本不被读出.
    """
    if not m.elements:
        return b""
    buf = bytearray()
    # 段头
    buf += _u32(ELEM_SIG_997)
    buf += _u32(segid)            # 元素段 segid = 组件 id; 0 = 未指定
    buf += _u32(ELEM_SIG_175)
    buf += _u32(len(m.elements))
    buf += _u32(ELEM_CONST_A)     # X = 3 锚 (A 型常量)
    # 元素记录: 简化 [eid][cfg][len][nodes...]
    for e in m.elements:
        buf += _u32(e.id)
        buf += _u32(e.config)
        buf += _u32(len(e.nodes))
        for nid in e.nodes:
            buf += _u32(nid)
    return bytes(buf)


def pack_minimal_hm(payload: bytes) -> bytes:
    """包装 gzip payload 为标准 .hm 前缀.

    格式: [4 bytes 0x00][8 bytes double 5.0 LE][gzip(payload)].
    与 load_payload 配套.
    return gzip
    """
    head = b"\x00\x00\x00\x00" + struct.pack("<d", 5.0)
    return head + gzip.compress(payload)


def _wrap_payload_internal(p: bytes, db_version: float) -> bytes:
    """payload 内部前缀: [4 字节 0][8 字节 db_version double][段数据].

    与 decode() 中 d64(p, 4) = db_version 一致.
    """
    return b"\x00\x00\x00\x00" + _f64(db_version) + p


def encode_minimal_db11_05(m: HMModel, path):
    """v0 .hm 写端骨架 (M5.1).

    仅写出 节点段 (52B 布局 A) + 元素段 (A 型锚). 无 collector/几何/解析器
    未知段. 不保证被 hmbatch 完整解析; 至少自身 decode() 应能读回节点.
    """
    payload = bytearray()
    payload += _serialize_nodes_db11_05_52A(m)
    payload += _serialize_elements_A_anchor(m)
    internal = _wrap_payload_internal(bytes(payload), m.db_version or 11.05)
    Path(path).write_bytes(pack_minimal_hm(internal))


def write_hmj(m: HMModel, path):
    """便捷: HMModel -> .hmj JSON (供 GUI Save Project / 离线 round-trip)."""
    import json
    d = {
        "app": "hm_writer", "format_version": 1,
        "db_version": m.db_version,
        "element_variant": m.element_variant,
        "source": "",
        "nodes": [[n.id, n.x, n.y, n.z]
                  for n in sorted(m.nodes.values(), key=lambda v: v.id)],
        "elements": [[e.id, e.config, list(e.nodes), e.comp]
                     for e in m.elements],
        "display_points": [[p.id, p.x, p.y, p.z]
                           for p in m.display_points.values()],
        "geo_points": [[p.id, p.x, p.y, p.z]
                       for p in m.geo_points.values()],
        "comps": m.comps, "mats": m.mats,
        "props": m.props, "groups": m.groups,
        "others": [[i, n] for i, n in m.others],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f)