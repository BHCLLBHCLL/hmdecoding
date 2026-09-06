import os
NL = chr(10)
DIRS = [
    r'C:/Program Files/Altair/2019/tutorials/hm',
    r'C:/Program Files/Altair/2019/demos/hm',
    r'C:/Program Files/Altair/2019/tutorials/hwsolvers',
    r'D:/training/hypermesh',
]
paths = []
for d in DIRS:
    if not os.path.isdir(d):
        continue
    for root, _, files in os.walk(d):
        for f in sorted(files):
            if f.lower().endswith('.hm'):
                paths.append(os.path.join(root, f).replace(chr(92), '/'))
with open('output/sweep4_files.txt', 'w', encoding='utf-8') as fh:
    for p in paths:
        fh.write(p + NL)
print('wrote', len(paths), 'files to output/sweep4_files.txt')
