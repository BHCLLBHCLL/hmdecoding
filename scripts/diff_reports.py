import os
def parse(fn):
    d = {}
    for l in open(fn, encoding='utf-8'):
        # 匹配: name  version  layout  payload= N | nodes .. | elems A/B STATUS
        parts = l.split('|')
        if len(parts) < 3:
            continue
        name = parts[0].split()[0]
        # payload 在第一段
        m = __import__('re').search(r'payload=\s*([\d,]+)', parts[0])
        pay = int(m.group(1).replace(',', '')) if m else 0
        # elems 状态在第三段
        es = parts[2].strip().split()
        st = es[-1] if es else '?'
        d[(name, pay)] = st
    return d

t = os.environ['TEMP']
b = parse(os.path.join(t, 'before.txt'))
a = parse(os.path.join(t, 'after.txt'))
print('=== 状态变化 ===')
for k in sorted(set(b) | set(a), key=lambda x: (x[0], x[1])):
    bs = b.get(k); as_ = a.get(k)
    if bs != as_:
        print(f'{k[0]:40s} {k[1]:>10,}  {bs} -> {as_}')
