# M3.3 门禁: 跑 hmbatch 逐文件 oracle 探针 -> output/m33_oracle/<file>.oracle.txt
import os, subprocess, sys

HM = r'C:/Program Files/Altair/2019/hm/bin/win64/hmbatch.exe'
TCL = os.path.abspath('scripts/m33_folder_oracle.tcl')
FILES = [
    r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm',
    r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_3.hm',
    r'C:/Program Files/Altair/2019/tutorials/hm/truck.hm',
]

def run(hmfile):
    os.makedirs('output/m33_oracle', exist_ok=True)
    with open('output/m33_oracle.path', 'w') as f:
        f.write(hmfile)
    r = subprocess.run([HM, '-tcl', TCL], capture_output=True, text=True,
                       timeout=900, cwd=os.path.dirname(os.path.dirname(TCL)))
    outp = os.path.join('output/m33_oracle', os.path.basename(hmfile) + '.oracle.txt')
    ok = os.path.exists(outp)
    print(f"{os.path.basename(hmfile)}: {'OK' if ok else 'NO-OUTPUT'} "
          f"(rc={r.returncode}, tail={r.stdout[-120:]!r})")
    return outp

if __name__ == '__main__':
    for fp in FILES:
        try:
            run(fp)
        except Exception as e:
            print(f"{fp}: ERROR {e}")
