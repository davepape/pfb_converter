import sys, struct
from pfb_constants import *

ENDIAN_FLAG = '>'

def readInt32(f):
    data = f.read(4)
    if data == "":
        raise Exception("end of file")
    return struct.unpack(ENDIAN_FLAG+'i', data)[0]

def readUInt32(f):
    data = f.read(4)
    if data == "":
        raise Exception("end of file")
    return struct.unpack(ENDIAN_FLAG+'I', data)[0]

def readUInt16(f):
    data = f.read(2)
    if data == "":
        raise Exception("end of file")
    return struct.unpack(ENDIAN_FLAG+'H', data)[0]

def readFloat32(f):
    data = f.read(4)
    if data == "":
        raise Exception("end of file")
    return struct.unpack(ENDIAN_FLAG+'f', data)[0]

def readInt32Array(f,num):
    return [readInt32(f) for i in range(num)]

def readUInt32Array(f,num):
    return [readUInt32(f) for i in range(num)]

def readUInt16Array(f,num):
    return [readUInt16(f) for i in range(num)]

def readFloat32Array(f,num):
    return [readFloat32(f) for i in range(num)]

def readPfVec4(f):
    return readFloat32Array(f,4)

def readPfVec3(f):
    return readFloat32Array(f,3)

def readPfVec2(f):
    return readFloat32Array(f,2)

def readPfVec4Array(f,num):
    return [readPfVec4(f) for i in range(num)]

def readPfVec3Array(f,num):
    return [readPfVec3(f) for i in range(num)]

def readPfVec2Array(f,num):
    return [readPfVec2(f) for i in range(num)]



class Tex0T:
    def __init__(self,f):
        self.format = readInt32Array(f,5)
        self.filter = readUInt32Array(f,4)
        self.wrap = readInt32Array(f,3)
        self.bcolor = readPfVec4(f)
        self.btype = readInt32(f)
        self.ssp = readPfVec2Array(f,4)
        self.ssc = readFloat32(f)
        self.dsp = readPfVec2Array(f,4)
        self.dsc = readFloat32(f)
        self.tdetail = readInt32Array(f,2)
        self.lmode = readInt32Array(f,3)
        self.losource = readInt32Array(f,2)
        self.lodest = readInt32Array(f,2)
        self.lsize = readInt32Array(f,2)
        self.image = readInt32(f)
        self.comp = readInt32(f)
        self.xsize = readInt32(f)
        self.ysize = readInt32(f)
        self.zsize = readInt32(f)
        self.load_image = readInt32(f)
        self.list_size = readInt32(f)
        self.frame = readFloat32(f)
        self.num_levels = readInt32(f)
        self.udata = readInt32(f)
        self.type = 0
        self.aniso_degree = 0


SIZEOF_CLIPTEX_T = 15*4
SIZEOF_CLIPLEVEL_T = 7*4

def readTex(version,f):
    size = readInt32(f)
    if size == -1:
        pass
    else:
        name = f.read(size).decode('ascii')
    if version >= PFBV_ANISOTROPY:
        # read tex_t (232 bytes)
        t = Tex0T(f)
        t.type = readInt32(f)
        readInt32(f)
    elif version >= PFBV_CLIPTEXTURE:
        # read tex_1_t (228 bytes)
        t = Tex0T(f)
        t.type = readInt32(f)
    else:
        t = Tex0T(f)
    if t.list_size > 0:
        for i in range(t.list_size):
            readInt32(f)
    if t.type == TEXTYPE_TEXTURE:
        if t.num_levels > 0:
            for i in range(t.num_levels):
                readInt32(f)
    else:
        f.read(SIZEOF_CLIPTEX_T)
        if t.num_levels > 0:
            f.read(t.num_levels * SIZEOF_CLIPLEVEL_T)
    return {}


def isGroupClassType(t):
    return t in [N_GROUP, N_SCS, N_DCS, N_PARTITION, N_SCENE, N_SWITCH, N_LOD, N_SEQUENCE, N_LAYER, N_MORPH, N_ASD, N_FCS, N_DOUBLE_DCS, N_DOUBLE_FCS, N_DOUBLE_SCS ]


def readNode(version,f):
    buf_size = readInt32(f)
    buf = readInt32Array(f,buf_size)
    node_type = buf.pop(0)
    if isGroupClassType(node_type):
        count = buf.pop(0)
        if node_type == N_GROUP:
            children = [buf.pop(0) for i in range(count)]
        else:
            print('#currently unsupported group node type')
    elif node_type == N_GEODE:
        count = buf.pop(0)
        gsets = [buf.pop(0) for i in range(count)]
    else:
        print('#currently unsupported node type')
    isect_travmask = buf.pop(0)
    app_travmask = buf.pop(0)
    cull_travmask = buf.pop(0)
    draw_travmask = buf.pop(0)
    name_size = readInt32(f)
    if name_size != -1:
        name = f.read(name_size).decode('ascii')
    return {}


class Gset_data:
    def __init__(self,version,f):
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
        if version >= PFBV_GSET_DO_DP:
            self.draw_order = readUInt32(f)
            self.decal_plane = readInt32(f)
            self.dplane_normal = readFloat32Array(f,3)
            self.dplane_offset = readFloat32(f)
        if version >= PFBV_GSET_BBOX_FLUX:
            self.bbox_flux = readInt32(f)
        if version >= PFBV_MULTITEXTURE:
            self.multi_tlist = readInt32Array(f,3*(19-1)) # guessing that PF_MAX_TEXTURES_19 is 19 - need to find that

class Gset:
    def __init__(self,g):
        self.PrimType = gspt_table[g.ptype]
        self.NumPrims = g.pcount

def readGset(version,f):
    gset_data = Gset_data(version,f)
    gset = Gset(gset_data)
    return gset



def readLlist(version,f):
    buf = readInt32Array(f,3)
    size = buf[0]
    llist = readInt32Array(f,size)
    return llist

def readVlist(version,f):
    buf = readInt32Array(f,3)
    size = buf[0]
    vlist = readPfVec3Array(f,size)
    return vlist

def readClist(version,f):
    buf = readInt32Array(f,3)
    size = buf[0]
    clist = readPfVec4Array(f,size)
    return clist

def readNlist(version,f):
    buf = readInt32Array(f,3)
    size = buf[0]
    nlist = readPfVec3Array(f,size)
    return nlist

def readTlist(version,f):
    buf = readInt32Array(f,3)
    size = buf[0]
    tlist = readPfVec2Array(f,size)
    return tlist

def readIlist(version,f):
    buf = readInt32Array(f,3)
    size = buf[0]
    ilist = readUInt16Array(f,size)
    return ilist


class modelData:
    def __init__(self):
        self.node = []
        self.gset = []
        self.llist = []
        self.vlist = []
        self.clist = []
        self.nlist = []
        self.tlist = []
        self.ilist = []
        self.tex = []



f = open(sys.argv[1],'rb')

magicnum = readUInt32(f)
print('#magic number = ' + hex(magicnum))
if magicnum == PFB_MAGIC_NUMBER_LE:
    ENDIAN_FLAG = '<'
version = readUInt32(f)
print(f'#pfb version {version}')
dummy = readInt32(f)
byteoffset = readInt32(f)
f.seek(byteoffset,0)

data = modelData()

while True:
    try:
        listtype = readInt32(f)
        numobjects = readInt32(f)
        numbytes = readInt32(f)
        print(f'#list type {l_name[listtype]}, {numobjects} objects, {numbytes} bytes')
        if listtype == L_TEX:
            for i in range(numobjects):
                data.tex.append(readTex(version,f))
        elif listtype == L_NODE:
            for i in range(numobjects):
                data.node.append(readNode(version,f))
        elif listtype == L_GSET:
            for i in range(numobjects):
                data.gset.append(readGset(version,f))
        elif listtype == L_LLIST:
            for i in range(numobjects):
                data.llist.append(readLlist(version,f))
        elif listtype == L_VLIST:
            for i in range(numobjects):
                data.vlist.append(readVlist(version,f))
        elif listtype == L_CLIST:
            for i in range(numobjects):
                data.clist.append(readClist(version,f))
        elif listtype == L_NLIST:
            for i in range(numobjects):
                data.nlist.append(readNlist(version,f))
        elif listtype == L_TLIST:
            for i in range(numobjects):
                data.tlist.append(readTlist(version,f))
        elif listtype == L_ILIST:
            for i in range(numobjects):
                data.ilist.append(readIlist(version,f))
        else:
            print('#  currently unsupported - skipping')
            f.read(numbytes)
    except Exception as error:
        break

f.close()

sys.exit(1)

numverts = 0
for vl in data.vlist:
    for v in vl:
        print(f'v {v[0]} {v[1]} {v[2]}')
        numverts += 1
for nl in data.nlist:
    for n in nl:
        print(f'vn {n[0]} {n[1]} {n[2]}')
for tl in data.tlist:
    for t in tl:
        print(f'vt {t[0]} {t[1]}')

#for i in range(0,numverts,3):
#    print(f'f {i}/{i}/{i} {i+1}/{i+1}/{i+1} {i+2}/{i+2}/{i+2}')
