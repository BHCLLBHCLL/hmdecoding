import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u16
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')
# 找 collector 类型字符 (C/M/P/L/S/G) 且前 8 字节内有 count
for i in range(0, min(len(p), 8_000_000) - 20, 2):
    tch = u16(p, i)
    if tch in (67, 77, 80, 76, 83, 71):  # C M P L S G
        # 前 8 u16 内找 count (1..500)
        for k in range(2, 20, 2):
            cnt = u16(p, i - k)
            if 1 <= cnt <= 500:
                ch = chr(tch)
                print('type=%s @%d (count=%d @%d)' % (ch, i, cnt, i-k))
                break
