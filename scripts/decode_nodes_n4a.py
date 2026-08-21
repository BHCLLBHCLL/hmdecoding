import gzip, struct

def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])

def u32(p, off): return struct.unpack_from("<I", p, off)[0]
def d(p, off): return struct.unpack_from("<d", p, off)[0]

p4 = load("v1913_02_n4a")
# node1 triple in n4a
import re
pat = struct.pack("<ddd", 1.0, 2.0, 3.0)
base = [m.start() for m in re.finditer(re.escape(pat), p4)][0]
print("n4a node1 at 0x%x" % base)
for i in range(4):
    rec = base + i * 72
    print(f"  node{i+1} @0x{rec:x}: ({d(p4,rec):g},{d(p4,rec+8):g},{d(p4,rec+16):g}) +0x34={u32(p4,rec+0x34)} +0x38={u32(p4,rec+0x38)} +0x3c={u32(p4,rec+0x3c)}")
# after last node record: 0x624..
print("after node4 (0x624..0x6a0):")
for off in range(0x624, 0x6a0, 16):
    chunk = p4[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    print(f"  {off:04x}  {hexs}")

# t1 (4 nodes + 1 elem): node5? no. check element section: look for connectivity 1,2,3,4 as u32 in t1
p1 = load("v1913_03_t1")
pat = struct.pack("<4I", 1, 2, 3, 4)
hits = [m.start() for m in re.finditer(re.escape(pat), p1)]
print("t1 u32(1,2,3,4) hits:", [hex(h) for h in hits])
for h in hits[:5]:
    print(f"  @0x{h:x} ctx pre={p1[h-16:h].hex()} post={p1[h+16:h+48].hex()}")
