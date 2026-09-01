import re
fn='hmdecoder/decoder.py'
data=open(fn,'rb').read()
target=bytes([0xf5,0x1f])
idx=[]
i=0
while True:
    j=data.find(target,i)
    if j<0: break
    idx.append((j,bytes(data[j-5:j])))
    i=j+1
print('f5 1f occurrences:', len(idx))
for j,pre in idx[:20]:
    print(j, pre)