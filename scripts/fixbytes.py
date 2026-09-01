fn='hmdecoder/decoder.py'
data=open(fn,'rb').read()
bad=bytes([0xc3,0xb5,0x1f])
good=bytes([0xf5,0x1f])
n=data.count(bad)
print('mangled occurrences:', n)
data=data.replace(bad, good)
open(fn,'wb').write(data)
print('fixed. good count now:', open(fn,'rb').read().count(good))