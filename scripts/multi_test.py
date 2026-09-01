import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
files = {
  'seat_2':'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm',
  'seat_start':'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_start.hm',
  'hook':'C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm',
  'keyhole':'C:/Program Files/Altair/2019/tutorials/hm/keyhole.hm',
  'channel':'C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm',
  'joints':'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm',
}
for name,f in files.items():
    try:
        m=decode(f)
        print(name, len(m.elements))
    except Exception as ex:
        print(name, 'ERR', ex)