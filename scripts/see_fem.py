data = open("output/ground_truth/synth_probe.fem", "rb").read()
for i in range(0, min(len(data), 512), 16):
    chunk = data[i:i+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"{i:04x}  {hexs:<47}  {ascii_}")
