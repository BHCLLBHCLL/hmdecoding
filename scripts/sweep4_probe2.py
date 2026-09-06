import sys, os
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u16, u32, d64, _scan_v11_records

f19 = r'D:/training/hypermesh/abaqus3_0tutorial.hm'
p = load_payload(f19)
print('=== abaqus3_0tutorial(db 19.02) len=%d ===' % len(p))
print('first 48 bytes:', p[:48].hex())
print('db double @4:', d64(p, 4))

fl = r'D:/training/hypermesh/chart 8/WorkShop8-3/WS_8.3_building_ResponseSpectrumAnalysis_finish.hm'
if os.path.exists(fl):
    p2 = load_payload(fl)
    print()
    print('=== WS_8.3_finish db=%.2f len=%d (oracle: 4 loads, 6 loadcols) ===' % (d64(p2,4), len(p2)))
    normal, groups = _scan_v11_records(p2)
    print('collector-like records:', len(normal))
    for off, nm in normal[:30]:
        print('  @%d id@off-16=%d name=%r' % (off, u16(p2, off-16), nm))
