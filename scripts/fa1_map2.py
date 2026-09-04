import sys,os
sys.path.insert(0,'hmdecoder')
elems_dir='output/ground_truth/elems'
def map_outfile(path):
    b=os.path.basename(path)
    p=os.path.normpath(path).replace('\\','/')
    f1=os.path.join(elems_dir,b+'.elems.txt')
    if os.path.exists(f1): return f1,b
    parent='hm'
    if '/interfaces/lsdyna/' in p: parent='lsdyna'
    if '/interfaces/abaqus/' in p: parent='abaqus'
    if '/interfaces/samcef/' in p: parent='samcef'
    f2=os.path.join(elems_dir,(parent+'_')+b+'.elems.txt')
    if os.path.exists(f2): return f2,(parent+'_')+b
    for tag in ('lsdyna_','hm_','abaqus_','samcef_','misc_'):
        f3=os.path.join(elems_dir,tag+b+'.elems.txt')
        if os.path.exists(f3): return f3,tag+b
    return None,b
print(map_outfile('C:/Program Files/Altair/2019/tutorials/hm/frame_assembly_1.hm'))
print(map_outfile('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm'))
