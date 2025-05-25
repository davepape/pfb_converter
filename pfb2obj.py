import sys, struct
from pfb_constants import *

ENDIAN_FLAG = '>'

# just guessing the value of PF_MAX_TEXTURES_19 for now - need to find that and add it to pfb_constants
# guess is almost definitely wrong, but the models I'm working with don't use this feature
PF_MAX_TEXTURES_19 = 19

# making a logical assumption for the values of PF_OFF & PF_ON - doublecheck this, then move this stuff to pfb_constants
PF_OFF = 0
PF_ON = 1
OnOff_table = [ 2, PF_OFF, PF_ON ]



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
    t.filename = name
    return t


def isGroupClassType(t):
    return t in [N_GROUP, N_SCS, N_DCS, N_PARTITION, N_SCENE, N_SWITCH, N_LOD, N_SEQUENCE, N_LAYER, N_MORPH, N_ASD, N_FCS, N_DOUBLE_DCS, N_DOUBLE_FCS, N_DOUBLE_SCS ]


class Node_data:
    def __init__(self,node_type):
        self.type = node_type
        self.name = ""

def readNode(version,f):
    buf_size = readInt32(f)
    buf = readInt32Array(f,buf_size)
    node = Node_data(buf.pop(0))
    if isGroupClassType(node.type):
        count = buf.pop(0)
        if node.type == N_GROUP:
            node.children = [buf.pop(0) for i in range(count)]
        else:
            print(f'#currently unsupported group node type "{node.type}"')
    elif node.type == N_GEODE:
        count = buf.pop(0)
        node.gsets = [buf.pop(0) for i in range(count)]
    else:
        print(f'#currently unsupported node type "{node.type}"')
    node.isect_travmask = buf.pop(0)
    node.app_travmask = buf.pop(0)
    node.cull_travmask = buf.pop(0)
    node.draw_travmask = buf.pop(0)
    name_size = readInt32(f)
    if name_size != -1:
        node.name = f.read(name_size).decode('ascii')
    return node


class Mtl_data:
    def __init__(self,version,f):
        self.side = readInt32(f)
        self.alpha = readFloat32(f)
        self.shininess = readFloat32(f)
        self.ambient = readPfVec3(f)
        self.diffuse = readPfVec3(f)
        self.specular = readPfVec3(f)
        self.emission = readPfVec3(f)
        self.cmode = readInt32Array(f,2)
        self.udata = readInt32(f)

class Gset_data:
    def __init__(self,version,f):
        self.ptype = gspt_table[readInt32(f)]
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
            self.multi_tlist = readInt32Array(f,3*(PF_MAX_TEXTURES_19-1))

def readGset(version,f):
    gset = Gset_data(version,f)
    return gset


def readMtl(version,f):
    mtl = Mtl_data(version,f)
    return mtl


class Gstate_data:
    def __init__(self):
        self.enlighting = False
        self.entexture = False
        self.frontmtl = -1
        self.texture = -1
    def read(self,version,f):
        buf_size = readInt32(f)
#NOTE: not all of the data in buf is actually Int32's - some of it can be 32-bit floats (for alpharef and for texture matrices); the original PFB code would use pointer casting to convert those parts to floats; may be able to do the same thing with Python's struct functions, but it could be messy
        buf = readInt32Array(f,buf_size)
        pos = 0
        endpos = buf_size - 1
        while pos < endpos:
            statemode = buf[pos]
            pos += 1
            if statemode == STATE_ENLIGHTING:
                self.enlighting = (OnOff_table[buf[pos]] == PF_ON)
                pos += 1
            elif statemode == STATE_ENTEXTURE:
                if version >= PFBV_MULTITEXTURE:
                    # would need to replace add a multitex alternative to "entexture"
                    pos += PF_MAX_TEXTURES_19-1
                else:
                    self.entexture = (OnOff_table[buf[pos]] == PF_ON)
                    pos += 1
            elif statemode == STATE_FRONTMTL:
                #NOTE: this is an index into the list 'data.mtl'; in original PFB code it assumed the mtl info came first, so it was looked up at this point to set the material number with pfGStateAttr
                self.frontmtl = buf[pos]
                pos += 1
            elif statemode == STATE_TEXTURE:
                #NOTE: this is an index into the list 'data.tex'
                self.texture = buf[pos]
                pos += 1
            else:
                print('#WARNING: unsupported geostate attribute; this geostate may be messed up as a result')

def readGstate(version,f):
    gstate = Gstate_data()
    gstate.read(version,f)
    return gstate


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
        self.mtl = []
        self.gset = []
        self.gstate = []
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
        elif listtype == L_MTL:
            for i in range(numobjects):
                data.mtl.append(readMtl(version,f))
        elif listtype == L_GSET:
            for i in range(numobjects):
                data.gset.append(readGset(version,f))
        elif listtype == L_GSTATE:
            for i in range(numobjects):
                data.gstate.append(readGstate(version,f))
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
            print(f'#  currently unsupported list type "{listtype}"- skipping')
            f.read(numbytes)
    except Exception as error:
        break

f.close()




obj_filename = sys.argv[2]
if obj_filename[-4:] == '.obj':
    mtl_filename = obj_filename[:-4] + '.mtl'
else:
    mtl_filename = obj_filename + '.mtl'

mtl_file = open(mtl_filename,'w')

i=0
for gstate in data.gstate:
    mtl_file.write(f'newmtl gstate{i}\n')
    if gstate.frontmtl > -1:
        mtl = data.mtl[gstate.frontmtl]
        mtl_file.write(f'Ka {mtl.ambient[0]} {mtl.ambient[1]} {mtl.ambient[2]}\n')
        mtl_file.write(f'Kd {mtl.diffuse[0]} {mtl.diffuse[1]} {mtl.diffuse[2]}\n')
        mtl_file.write(f'Ks {mtl.specular[0]} {mtl.specular[1]} {mtl.specular[2]}\n')
        mtl_file.write(f'Ns {mtl.shininess}\n')
    if gstate.texture > -1:
        tex = data.tex[gstate.texture]
        pngfile = tex.filename.replace('.sgi','.png')
        mtl_file.write(f'map_Kd {pngfile}\n')
    mtl_file.write('\n')
    i += 1

mtl_file.close()

obj_file = open(obj_filename,'w')
obj_file.write(f'mtllib {mtl_filename}\n')

def print_tristrip_triangle(firstindex, normal_mode, texc_mode, ccw):
    if ccw:
        if texc_mode == PFGS_OFF:
            obj_file.write(f'f {firstindex+1}//{firstindex+1} {firstindex+2}//{firstindex+2} {firstindex+3}//{firstindex+3}\n')
        else:
            obj_file.write(f'f {firstindex+1}/{firstindex+1}/{firstindex+1} {firstindex+2}/{firstindex+2}/{firstindex+2} {firstindex+3}/{firstindex+3}/{firstindex+3}\n')
    else:
        if texc_mode == PFGS_OFF:
            obj_file.write(f'f {firstindex+1}//{firstindex+1} {firstindex+3}//{firstindex+3} {firstindex+2}//{firstindex+2}\n')
        else:
            obj_file.write(f'f {firstindex+1}/{firstindex+1}/{firstindex+1} {firstindex+3}/{firstindex+3}/{firstindex+3} {firstindex+2}/{firstindex+2}/{firstindex+2}\n')
numverts = 0

for n in data.node:
    if n.type == N_GEODE:
        for g in n.gsets:
            coords = []
            norms = []
            texc = []
            gset = data.gset[g]
            obj_file.write(f'#gset type {gset.ptype}   numprims {gset.pcount}   gstate {gset.gstate}\n')
            if gset.llist != -1:
                lens = data.llist[gset.llist]
                obj_file.write(f'#  lenlist: {lens}\n')
            if gset.vlist[1] != -1:
                coords = data.vlist[gset.vlist[1]]
            else:
                continue    # i.e. if there's no list of vertices, just skip this geoset
            if gset.vlist[2] != -1:
                indices = data.ilist[gset.vlist[2]]
                coords = [coords[i] for i in indices]
            vstart = numverts
            for v in coords:
                obj_file.write(f'v {v[0]} {v[1]} {v[2]}\n')
                numverts += 1
#NOTE: this code assumes that normals & texcoords are per-vertex.  Support for PFGS_OVERALL and PFGS_PER_PRIM will need to be added.
            normal_mode = gsb_table[gset.nlist[0]]
            if normal_mode != PFGS_PER_VERTEX:
                obj_file.write('#WARNING: unsupported normal mode !!!!\n')
            if gset.nlist[1] != -1:
                norms = data.nlist[gset.nlist[1]]
                if gset.nlist[2] != -1:
                    indices = data.ilist[gset.nlist[2]]
                    norms = [norms[i] for i in indices]
                for n in norms:
                    obj_file.write(f'vn {n[0]} {n[1]} {n[2]}\n')
            texc_mode = gsb_table[gset.tlist[0]]
            if (texc_mode != PFGS_PER_VERTEX) and (texc_mode != PFGS_OFF):
                obj_file.write('#WARNING: unsupported texture coordinate mode !!!!\n')
            if gset.tlist[1] != -1:
                texc = data.tlist[gset.tlist[1]]
                if gset.tlist[2] != -1:
                    indices = data.ilist[gset.tlist[2]]
                    texc = [texc[i] for i in indices]
                for t in texc:
                    obj_file.write(f'vt {t[0]} {t[1]}\n')
            if (len(coords) != len(norms)) or (len(coords) != len(texc)):
                obj_file.write('#ERROR: mismatched number of normals or texture coordinates - only per-vertex is supported !!!!\n')
                print('#ERROR: mismatched number of normals or texture coordinates - only per-vertex is supported !!!!\n')
#NOTE: should look up how pfGSetGStateIndex() works (if gstate[1] is not -1); probably none of our models use that feature, however
            if gset.gstate[0] != -1:
                obj_file.write(f'usemtl gstate{gset.gstate[0]}\n')
            if gset.ptype == PFGS_TRISTRIPS:
                stripstart = vstart
                for striplen in lens:
                    vertindex = stripstart
                    ccw = True
                    for tri in range(striplen-2):
                        print_tristrip_triangle(vertindex, normal_mode, texc_mode, ccw)
                        vertindex += 1
                        ccw = not ccw
                    stripstart += striplen

obj_file.close()

