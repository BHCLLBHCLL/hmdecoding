import gzip, struct, re
raw = open("output/ground_truth/synth_probe.fem", "rb").read()
payload = gzip.decompress(raw[12:])
print("payload size:", len(payload))
def u32le(b, off): return struct.unpack_from("<I", b, off)[0]
for i in range(0, len(payload), 16):
    chunk = payload[i:i+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"{i:04x}  {hexs:<47}  {ascii_}")
