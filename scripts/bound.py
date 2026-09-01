fn='hmdecoder/decoder.py'
d=open(fn,encoding='utf-8').read()
i=d.index('def _parse_cfg55_mpc')
j=d.index('def decode_elements')
print('start',i,'end',j)
print(repr(d[i:i+40]))