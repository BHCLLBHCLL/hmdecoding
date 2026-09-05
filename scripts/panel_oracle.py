import sys, subprocess, os, json, re
# 面板级 oracle 快照: 调用 hmbatch 跑 panel_oracle.tcl, 解析输出为 JSON
HM = r'C:/Program Files/Altair/2019/hm/bin/win64/hmbatch.exe'
TCL = os.path.abspath('scripts/panel_oracle.tcl')
def run_panel(panel):
    # 面板 oracle 是交互, Tcl 无法真正"打开面板"; 但面板底层操作 (createnode/movemark/renumber)
    # 可无头驱动, 作为面板行为的 oracle 证据. hmbatch 的 $argv 不可靠, 用文件传 panel 名.
    open('output/panel_oracle.panel', 'w').write(panel)
    r = subprocess.run([HM, '-tcl', TCL], capture_output=True, text=True, timeout=120)
    logf = open('output/panel_oracle.log', encoding='utf-8').read()
    lines = [l for l in logf.splitlines() if l.strip()]
    return {'panel': panel, 'stdout_tail': r.stdout[-200:], 'log': lines}
if __name__ == '__main__':
    out = {}
    for p in ['nodes', 'translate', 'renumber']:
        try:
            out[p] = run_panel(p)
            print('panel=%s' % p)
            for l in out[p]['log']:
                print('   ', l)
        except Exception as e:
            out[p] = {'error': str(e)}
            print('panel=%s ERROR %s' % (p, e))
    json.dump(out, open('output/panel_oracle_snapshot.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('snapshot saved: output/panel_oracle_snapshot.json')
