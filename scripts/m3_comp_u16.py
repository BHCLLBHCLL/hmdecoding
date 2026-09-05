import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/cover.hm')
# 组件段头部 + 记录, u16 视角
print('=== u16 视角 (111400..111470) ===')
for o in range(111400, 111470, 2):
    v = u16(p, o)
    print('@%d u16=%d' % (o, v))
print('=== 搜 1/2/4 在组件区出现位置 (u16) ===')
for o in range(111400, 111700, 2):
    v = u16(p, o)
    if v in (1, 2, 4):
        # 只打印紧邻标记/名字附近
        pass
