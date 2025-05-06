import sys, struct
from pfb_constants import *

SIZEOF_CLIPTEX_T = 15*4
SIZEOF_CLIPLEVEL_T = 7*4

def swap_32(a):
    return a[::-1]

def readInt32(f):
    data = f.read(4)
    if data == "":
        raise Exception("end of file")
    return struct.unpack('>i', data)[0]

def readUInt32(f):
    data = f.read(4)
    if data == "":
        raise Exception("end of file")
    return struct.unpack('>I', data)[0]

def readFloat32(f):
    data = f.read(4)
    if data == "":
        raise Exception("end of file")
    return struct.unpack('>f', data)[0]

def readInt32Array(f,num):
    return [readInt32(f) for i in range(num)]

def readUInt32Array(f,num):
    return [readUInt32(f) for i in range(num)]

def readFloat32Array(f,num):
    return [readFloat32(f) for i in range(num)]

def readPfVec4(f):
    return readFloat32Array(f,4)

def readPfVec3(f):
    return readFloat32Array(f,3)

def readPfVec2(f):
    return readFloat32Array(f,2)

def readTex0T(f):
    # 224 bytes
    readInt32Array(f,5)
    readUInt32Array(f,4)
    readInt32Array(f,3)
    readPfVec4(f)
    readInt32(f)
    readPfVec2(f)
    readPfVec2(f)
    readPfVec2(f)
    readPfVec2(f)
    readFloat32(f)
    readPfVec2(f)
    readPfVec2(f)
    readPfVec2(f)
    readPfVec2(f)
    readFloat32(f)
    readInt32Array(f,2)
    readInt32Array(f,3)
    readInt32Array(f,2)
    readInt32Array(f,2)
    readInt32Array(f,2)
    readInt32(f)
    readInt32(f)
    readInt32Array(f,3)
    readInt32(f)
    t_list_size = readInt32(f)
    readFloat32(f)
    readInt32(f)
    readInt32(f)

def readTex(version,f):
    size = readInt32(f)
    t_list_size = 0
    t_type = 0
    t_num_levels = 0
    if size == -1:
        pass
    else:
        name = f.read(size).decode('ascii')
        print(f'texture name: "{name}"')
    if version >= PFBV_ANISOTROPY:
        # read tex_t (232 bytes)
        readTex0T(f)
        t_type = readInt32(f)
        readInt32(f)
    elif version >= PFBV_CLIPTEXTURE:
        # read tex_1_t (228 bytes)
        readTex0T(f)
        t_type = readInt32(f)
    else:
        readTex0T(f)
    if t_list_size > 0:
        print(f'reading {t_list_size} ints for itlist')
        for i in range(t_list_size):
            readInt32(f)
    if t_type == TEXTYPE_TEXTURE:
        if t_num_levels > 0:
            print(f'reading {t_num_levels} ints for levels')
            for i in range(t_num_levels):
                readInt32(f)
    else:
        f.read(SIZEOF_CLIPTEX_T)
        if t_num_levels > 0:
            print('reading cliplevels')
            f.read(t_num_levels * SIZEOF_CLIPLEVEL_T)


def isGroupClassType(t):
    return t in [N_GROUP, N_SCS, N_DCS, N_PARTITION, N_SCENE, N_SWITCH, N_LOD, N_SEQUENCE, N_LAYER, N_MORPH, N_ASD, N_FCS, N_DOUBLE_DCS, N_DOUBLE_FCS, N_DOUBLE_SCS ]


def readNode(version,f):
    buf_size = readInt32(f)
    buf = readInt32Array(f,buf_size)
    node_type = buf.pop(0)
    print(f'node {node_names[node_type]}  buf_size={buf_size}')
    if isGroupClassType(node_type):
        count = buf.pop(0)
        if node_type == N_GROUP:
            children = [buf.pop(0) for i in range(count)]
            print(f'  {count} children: {children}')
        else:
            print('currently unsupported group node type')
    elif node_type == N_GEODE:
        count = buf.pop(0)
        gsets = [buf.pop(0) for i in range(count)]
        print(f'  {count} gsets: {gsets}')
    else:
        print('currently unsupported node type')
    isect_travmask = buf.pop(0)
    app_travmask = buf.pop(0)
    cull_travmask = buf.pop(0)
    draw_travmask = buf.pop(0)
    print(f'  travmasks: {isect_travmask} {app_travmask} {cull_travmask} {draw_travmask}')
    print(f'  remaining data: {buf}')
    name_size = readInt32(f)
    if name_size != -1:
        name = f.read(name_size).decode('ascii')
        print(f'  name: {name}')


class Gset0T:
    def __init__(self,f):
        self.ptype = readInt32(f)
        self.pcount = readInt32(f)
        self.llist = readInt32(f)
        self.vlist = readInt32Array(f,3)
        self.clist = readInt32Array(f,3)
        self.nlist = readInt32Array(f,3)
        self.tlist = readInt32Array(f,3)
        self.draw_mode = readInt32Array(f,3)
        self.gstate = readInt32Array(f,2)
        self.line_width = readFloat32(f)
        self.point_size = readFloat32(f)
        self.draw_bin = readInt32(f)
        self.isect_mask = readUInt32(f)
        self.hlight = readInt32(f)
        self.bbox_mode = readInt32(f)
        self.bbox = readFloat32Array(f,6)
        self.udata = readInt32(f)

def readGset(version,f):
    if version >= PFBV_MULTITEXTURE:
        gset = Gset0T(f)
        readUInt32(f)
        readInt32(f)
        readFloat32Array(f,3)
        readFloat32(f)
        readInt32(f)
        readInt32Array(f,3*(19-1)) # guessing that PF_MAX_TEXTURES_19 is 19 - need to find that
    elif version >= PFBV_GSET_BBOX_FLUX:
        gset = Gset0T(f)
        readUInt32(f)
        readInt32(f)
        readFloat32Array(f,3)
        readFloat32(f)
        readInt32(f)
    elif version >= PFBV_GSET_DO_DP:
        gset = Gset0T(f)
        readUInt32(f)
        readInt32(f)
        readFloat32Array(f,3)
        readFloat32(f)
    else:
        gset = Gset0T(f)
    print(f'Gset: primType {gset.ptype}  numPrims {gset.pcount}  lengthlist {gset.llist}')

f = open(sys.argv[1],'rb')

magicnum = readInt32(f)
print('magic number = ' + hex(magicnum))
version = readUInt32(f)
print(f'version {version}')
dummy = readInt32(f)
byteoffset = readInt32(f)
print(f'{byteoffset} byte offset')
f.seek(byteoffset,0)

while True:
    try:
        listtype = readInt32(f)
        numobjects = readInt32(f)
        numbytes = readInt32(f)
        print(f'list type {l_name[listtype]}, {numobjects} objects, {numbytes} bytes')
        if listtype == L_TEX:
            for i in range(numobjects):
                readTex(version,f)
        elif listtype == L_NODE:
            for i in range(numobjects):
                readNode(version,f)
        elif listtype == L_GSET:
            for i in range(numobjects):
                readGset(version,f)
        else:
            f.read(numbytes)
    except Exception as error:
        break

f.close()
