fn='hmdecoder/decoder.py'
data=open(fn,'rb').read()
good=bytes([0xf5,0x1f])
esc=b'\\xf5\\x1f'  # ASCII backslash-x escape text
n=data.count(good)
print('raw f5 1f occurrences:', n)
data=data.replace(good, esc)
open(fn,'wb').write(data)