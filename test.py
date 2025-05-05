import sys, struct

L_MTL = 0
L_TEX = 1
L_TENV = 2
L_GSTATE = 3
L_LLIST = 4
L_VLIST = 5
L_CLIST = 6
L_NLIST = 7
L_TLIST = 8
L_ILIST = 9
L_GSET = 10
L_NODE = 12

PFBV_CLIPTEXTURE = 7
PFBV_ANISOTROPY = 20

TEXTYPE_TEXTURE = 0
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
        name = f.read(size)
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
        print(f'list type {listtype}, {numobjects} objects, {numbytes} bytes')
        if listtype == L_TEX:
            for i in range(numobjects):
                readTex(version,f)
        else:
            f.read(numbytes)
    except Exception as error:
        print(repr(error))
        break

f.close()
