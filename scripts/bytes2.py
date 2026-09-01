fn='hmdecoder/decoder.py'
data=open(fn,'rb').read()
# region containing the inserted function; find b\" around 1155-1207
# search for 'slave_num'
k=data.find(b'slave_num')
print('slave_num at', k)
seg=data[k:k+700]
print(repr(seg))