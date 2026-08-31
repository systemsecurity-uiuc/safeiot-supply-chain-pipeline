#
# This code is part of the jarpkginfo utilty.
#
# (C) Copyright IBM 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
#
import struct
import sys

def decodeType(type, objName, argNames=None, isFunction=False):
    ndx = 0
    res = []
    args = None
    retType = None
    isArray = False

    argNDX = 0
    argID = 0

    while ndx < len(type):
        c = type[ndx]
        name = None
        if c == 'I':
            name = 'int'
            argNDX = 0
        elif c == 'Z':
            name = 'boolean'
            argNDX = 1
        elif c == 'B':
            argNDX = 0
            name = 'byte'
        elif c == 'C':
            argNDX = 5
            name = 'char'
        elif c == 'S':
            argNDX = 0
            name = 'short'
        elif c == 'J':
            argNDX = 0
            name = 'long'
        elif c == 'F':
            argNDX = 3
            name = 'float'
        elif c == 'D':
            argNDX = 3
            name = 'double'
        elif c == 'V':
            name = ""
        elif c == 'L':
            argNDX = 4
            ndx = ndx+1
            start=ndx
            while ndx < len(type) and type[ndx] != ';':
                ndx = ndx+1
            name = type[start:ndx]
        elif c == '[':
            isArray=True
            ndx = ndx + 1
            continue
        
        elif c == '(':
            ndx = ndx + 1
            start = ndx
            while ndx < len(type) and type[ndx] != ')':
                ndx = ndx+1
            args = '(' + decodeType(type[start:ndx], None, argNames, True) + ')'
        else:
            raise TypeError("Invalid character '"+c+"'in type signature "+type)

        if isArray:
            name = name + '[]'
        isArray = False

        if name is not None and args is None:
            if isFunction and argNames is not None:
                res.append(name+" "+argNames[argNDX]+str(argID))
                argID = argID + 1
            else:
                res.append(name)
        else:
            retType = name
        ndx = ndx + 1


    if args:
        if retType == "":
            return objName + args
        else:
            return objName + args + " -> " + retType
    else:
        s = ", ".join(res)
        if objName is None:
            return s
        elif s == "":
            return objName
        else:
            return s + " " + objName


#
#  Returns [rettype,[arg:type,arg:type]]
#
def getArgs(type, argNames=None,isFunction=False):
    ndx = 0
    res = []
    args = False
    retType = None
    isArray = False


    argNDX = 0
    argID = 0

    arguments = []

    while ndx < len(type):
        c = type[ndx]
        name = None
        if c == 'I':
            name = 'i32'
            argNDX = 0
        elif c == 'Z':
            name = 'i1'
            argNDX = 1
        elif c == 'B':
            argNDX = 0
            name = 'i8'
        elif c == 'C':
            argNDX = 5
            name = 'i16'
        elif c == 'S':
            argNDX = 0
            name = 'i16'
        elif c == 'J':
            argNDX = 0
            name = 'i64'
        elif c == 'F':
            argNDX = 3
            name = 'f32'
        elif c == 'D':
            argNDX = 3
            name = 'f64'
        elif c == 'V':
            name = None
        elif c == 'L':
            argNDX = 4
            ndx = ndx+1
            start=ndx
            while ndx < len(type) and type[ndx] != ';':
                ndx = ndx+1
            name = type[start:ndx].replace('/','.')
        elif c == '[':
            isArray=True
            ndx = ndx + 1
            continue

        elif c == '(':
            ndx = ndx + 1
            start = ndx
            while ndx < len(type) and type[ndx] != ')':
                ndx = ndx+1
            res = getArgs(type[start:ndx], argNames, True)[1]
            args = True
        else:
            raise TypeError("Invalid character '"+c+"'in type signature "+type)

        if isArray:
            name = name + '[]'
        isArray = False

        if name is not None and args is False:
            if isFunction:
                if argNames is not None:
                    res.append(argNames[argNDX]+str(argID)+":"+name)
                else:
                    res.append(['%a'+str(argID),name])
                argID = argID + 1
            else:
                res.append(name)
        else:
            retType = name
        ndx = ndx + 1


    return [retType,res]
            

class JavaClass:

    TAG_UTF8String = 1
    TAG_Int32 = 3
    TAG_Float = 4
    TAG_Int64 = 5
    TAG_Double = 6
    TAG_ClassRef = 7
    TAG_StringRef = 8
    TAG_FieldRef = 9
    TAG_MethodRef = 10
    TAG_InterfaceMethodRef = 11
    TAG_NameAndType = 12
    TAG_MethodHandle = 15
    TAG_MethodType = 16
    TAG_Dynamic = 17
    TAG_InvokeDynamic = 18
    TAG_Module = 19
    TAG_Package = 20

    
    READHEADER=0
    READCONSTPOOL=1
    READCLASSINFO=2
    READIF=3
    READFIELDS=4
    READMETHODCOUNT=5
    READMETHODS=6
    READATTRCOUNT=7
    READATTRS=8
    LOADED=9
    
    major_version = 0
    minor_version = 0
    
    __class = None
    __super = None
    __constants = []
    __methodInfo = []
    __fields = []
    __interfaces = []

    __NullSlot = False

    __file = None

    def __init__(self):
        self.heldbytes = None
        self.state = JavaClass.READHEADER
        self.__class = None
        self.__constants = None
        self.__annotation_names = set()


    def get_flags(self):
        return self.access
    
    def isLoaded(self):
        if self.state == JavaClass.LOADED:
            return True
        return False
            
    def loadIncremental(self, data):

        if self.state == JavaClass.LOADED:
            return False

        if self.heldbytes is not None:
            if data is None:
                data = self.heldbytes
            else:
                data = self.heldbytes + data
            self.heldbytes = None

        offset = 0

        if self.state == JavaClass.READHEADER:
            if len(data) < 10:
                self.heldbytes = data
                return False

            magic = self.__readlong(data, 0)
            if magic != 0xCAFEBABE:
                return None

            self.minor_version = self.__readshort(data, 4)
            self.major_version = self.__readshort(data, 6)

            self.const_count = self.__readshort(data, 8)
            self.state = JavaClass.READCONSTPOOL
            self.__constants = []
            self.__NullSlot = False            
            data = data[10:]

        if self.state == JavaClass.READCONSTPOOL:
            #
            # const_count is + 1
            #
            while self.const_count > 1:
                size = self.__readconstant(data)
                if size is False:
                    self.heldbytes = data
                    return False
                data = data[size:]
                self.const_count = self.const_count - 1


            self.state = JavaClass.READCLASSINFO

        if self.state == JavaClass.READCLASSINFO:
            if len(data) < 8:
                self.heldbytes = data
                return False
            self.access = self.__readshort(data, 0)
            self.__class = self.__readshort(data, 2)
            self.__super = self.__readshort(data, 4)
            self.ifcount = self.__readshort(data, 6)
            self.__fields = []
            self.__field_offset_obj = 0
            self.__field_offset_class = 0
            self.__methodInfo = []
            self.__attr = []
            data = data[8:]
            self.fields_ = {}
            self.methods_ = {}
            self.methods_by_sig_ = {}
            self.state = JavaClass.READIF

        if self.state == JavaClass.READIF:
            if len(data) < (self.ifcount * 2 + 2):  # + 2 to get field count as well
                self.heldbytes = data
                return False

            self.__interfaces = [self.__readshort(data,i*2) for i in range(0,self.ifcount)]
            data = data[self.ifcount*2:]
            self.state = JavaClass.READFIELDS
            self.fcount = self.__readshort(data, 0)
            data = data[2:]

        if self.state == JavaClass.READFIELDS:
            while self.fcount > 0:
                n = self.__readfm(data, self.__fields)
                if not n:
                    self.heldbytes = data
                    return False
                self.fcount = self.fcount - 1
                data = data[n:]

            for f,ndx,desc,attr in self.__fields:
                n = self.__getStrConst(ndx)
                t = self.__getStrConst(desc)

                flags=set()

                if f & 0x0001: flags.add('public')
                if f & 0x0002: flags.add('private')
                if f & 0x0004: flags.add('protected')
                if f & 0x0008: flags.add('static')
                if f & 0x0010: flags.add('final')
                if f & 0x0040: flags.add('volatile')
                if f & 0x0080: flags.add('transient')
                if f & 0x1000: flags.add('synthetic')
                if f & 0x4000: flags.add('enum')

                _, ftype, fraw = self.getArgTypes(t)
                
                rec = {
                    'name': n,
                    'type': ftype[0],
                    'signature': fraw[0],
                    'flags': flags,
                    'attr': self.decodeAttributes(attr),
                }

                t = rec['type']
                width = 4
                if t in ['long', 'double'] or t[0] == 'L':
                    width = 8

                if f & 0x0008:  # Class field
                    rec['offset'] = self.__field_offset_class
                    self.__field_offset_class += width
                else:
                    rec['offset'] = self.__field_offset_obj
                    self.__field_offset_obj += width
                    

                cn = self.className()
                cn = cn.replace("/", '.')
                n = cn + '.' + n

                rec['fullname'] = n
                rec['class'] = cn

                self.fields_[n] = rec
                

            self.state = JavaClass.READMETHODCOUNT


        if self.state == JavaClass.READMETHODCOUNT:
            if len(data) < 2:
                self.heldbytes = data
                return False
            self.mcount = self.__readshort(data, 0)
            data = data[2:]
            self.state = JavaClass.READMETHODS

        if self.state == JavaClass.READMETHODS:
            while self.mcount > 0:
                n = self.__readfm(data, self.__methodInfo)
                if not n:
                    self.heldbytes = data
                    return False
                self.mcount = self.mcount - 1
                data = data[n:]

            for f,ndx,desc,attr in self.__methodInfo:
                name = self.__getStrConst(ndx)
                tsig = self.__getStrConst(desc)

                flags = set()

                if f & 0x0001: flags.add('public')
                if f & 0x0002: flags.add('private')
                if f & 0x0004: flags.add('protected')
                if f & 0x0008: flags.add('static')
                if f & 0x0010: flags.add('final')
                if f & 0x0020: flags.add('synchronized')
                if f & 0x0040: flags.add('bridged')
                if f & 0x0080: flags.add('varargs')
                if f & 0x0100: flags.add('native')
                if f & 0x0400: flags.add('abstract')
                if f & 0x0800: flags.add('strictfp')
                if f & 0x1000: flags.add('synthetic')


                rec = {
                    'name': name,
                    'flags': flags,
                    'attr': self.decodeAttributes(attr),
                    'type_signature': tsig
                }


                cn = self.className()
                cn = cn.replace("/", '.')
                name = cn + '.' + name

                rec['class'] = cn
                rec['fullname'] = name

                rettype, argtypes, raw = self.getArgTypes(tsig)

                if rettype is not None:
                    rettype = rettype.replace("/", ".")

                rec['return_type'] = rettype

                args = []

                if not 'static' in flags:
                    args.append({
                        'type': cn,
                        'name': 'this'
                    })

                for n,t in enumerate(argtypes):
                    args.append({
                        'type': t.replace("/", "."),
                        'name': f"arg{n+1}"
                    })

                rec['parameters'] = args
                rec['typesignatures'] = raw

                if name not in self.methods_:
                    self.methods_[name] = list()
                self.methods_[name].append(rec)

                key = name + "," + tsig
                self.methods_by_sig_[key] = rec

            self.state = JavaClass.READATTRCOUNT

        
        if self.state == JavaClass.READATTRCOUNT:
            if len(data) < 2:
                self.heldbytes = data
                return False
            self.acount = self.__readshort(data, 0)
            data = data[2:]
            self.state = JavaClass.READATTRS

        if self.state == JavaClass.READATTRS:
            while self.acount > 0:
                n = self.__readattr(self.__attr, data)
                if not n:
                    self.heldbytes = data
                    return False
                self.acount = self.acount - 1
                data = data[n:]

            self.class_attributes = self.decodeAttributes(self.__attr)
            self.state = JavaClass.LOADED

        return True

    def load(self, file):
        while True:
            bytes = file.read()
            if bytes is None:
                continue
            if len(bytes) == 0:
                break
            if self.loadIncremental(bytes):
                break
        if self.state != JavaClass.LOADED:
            return None
        return self
        
    def loadFile(self,filename):
        '''Loads a class file specified by filename'''
        with open(filename, mode='rb') as file:
            return self.load(file)

    #------------------------------------------------------------------------

    def decodeCodeAttr(self, d):
        stksz, nlocal = struct.unpack('>2H', d[0:4])
        codelen = struct.unpack('>I', d[4:8])[0]
        code = d[8:codelen+8]
        offset = codelen+8
        exlen = struct.unpack('>H', d[offset:offset+2])[0]
        offset += 2
        exinfo = []

        while exlen > 0:
            spc, epc, hpc, extype = struct.unpack('>4H', d[offset:offset+8])
            if extype != 0:
                exname = self.__getClassName(extype)
            else:
                exname = None
            exinfo.append({
                'start_pc': spc,
                'end_pc': epc,
                'handler_pc': hpc,
                'exception': exname
            })
            offset += 8
            exlen -= 1
        acount = struct.unpack('>H', d[offset:offset+2])[0]
        attr = []
        offset += 2
        while acount > 0:
            n = self.__readattr(attr, d[offset:])
            offset += n
            acount -= 1
        return {
            'stacksize': stksz,
            'nlocal': nlocal,
            'codesize': codelen,
            'code': code,
            'exceptions': exinfo,
            'attr': self.decodeAttributes(attr)
        }

    def decodeStackMapTableAttr(self, d):
        n = struct.unpack('>H', d[0:2])[0]
        offset = 2
        while n > 0:
            b = d[offset]
            if b <= 63:
                # same_frame
                offset += 1
                pass
            elif b <= 127:
                # same_locals_1_stack_item_frame
                pass
            elif b <= 246:
                # should not see (reserved for future use)
                pass
            elif b == 247:
                # same_locals_1_stack_item_frame_extended
                pass
            elif b <= 250:
                # chop_frame
                pass
            elif b == 251:
                # same_frame_extended
                pass
            elif b <= 254:
                # append_frame
                pass
            else:
                delta, nlocals = struct.unpack('>2H', d[0:4])
                nl = nlocals
                vi = []
                    
            n -= 1
        
        return {}


    def decodeRTTypeAnnotation(self, data):
        offset = 0
        count = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2
        
        tn = []

        while count > 0:
            count -= 1
            ta, offset = self.decode_type_annotation(data, offset)
            tn.append(ta)

        return tn


    def decode_element_value(self, data, offset):

        etype = data[offset]   # Don't unpack as a byte
        offset += 1

        if type(etype) == type(0):
            etype = chr(etype)

        if etype in ['B', 'C', 'D', 'F', 'I', 'J', 'S', 'Z', 's']: # constant
            cvndx = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2

            cv = self.getConstantPool(cvndx)
            el = {
                'type': 'const',
                'value': cv,
                'str': 'const:' + str(cv)
            }

        elif etype == 'e':  # enum
            tndx, cndx = struct.unpack('>2H', data[offset:offset+4])
            offset += 4
            tname = self.getConstantPool(tndx)
            cname = self.getConstantPool(cndx)
            el = {
                'type': 'enum',
                'enum_type': tname,
                'enum_constant': cname,
                'str': 'enum:'+str(tname)+':'+str(cname)
            }

        elif etype == 'c':  # class
            cndx = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2

            cname = self.getConstantPool(cndx)


            el = {
                'type': 'class',
                'name': cname,
                'str': 'class:'+str(cname)
            }

        elif etype == '@':  # annotation
            a,offset = self.decode_annotation(data, offset)
            el = {
                'type': 'annotation',
                'annotation': a,
                'str': 'annotation:' + a['str']
            }

        elif etype == '[':  # array
            nv = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2

            ev = []
            while nv > 0:
                nv -= 1
                el, offset = self.decode_element_value(data, offset)
                ev.append(el)
            el = {
                'type': 'array',
                'element_values': ev,
                'str': 'array:[' + ",".join(sorted([x['str'] for x in ev])) + ']'
            }
        else:
             sys.stderr.write("Unrecognized type code: " + str(etype) + "\n")
             el = None

        return el, offset


    def decode_type_annotation(self, data, offset):

        tt = struct.unpack('B', data[offset:offset+1])[0]

        offset += 1

        rec = {}
        rec['typecode'] = tt

        #
        # Decode the target type
        #

        if tt == 0 or tt == 1:
            # type_parameter_target

            rec['type'] = 'type parameter'
            rec['index'] = struct.unpack('B', data[offset:offset+1])[0]
            offset += 1

            if tt == 0:
                rec['target'] = 'classfile'
            else:
                rec['target'] = 'method'

            rec['str'] = rec['type'] + ':' + rec['target'] + ':' + str(rec['index'])


        elif tt == 16:
            rec['type'] = 'supertype'
            rec['target'] = 'classfile'
            rec['index'] = struct.unpack('>H', data[offset:offset+2])[0]
            rec['str'] = rec['type'] + ':' + rec['target'] + ':' + str(rec['index'])
            offset += 2

        elif tt == 17 or tt == 18:
            rec['type'] = 'type parameter bound'

            a, b = struct.unpack('2B', data[offset:offset+2])
            offset += 2
            rec['index'] = a
            rec['bound_index'] = b

            if tt == 17:
                rec['target'] = 'classfile'
            else:
                rec['target'] = 'method'

            rec['str'] = rec['type'] + ':' + rec['target'] + ':' + str(rec['index'])


        elif tt == 19 or tt == 20 or tt == 21:
            rec['type'] = 'empty'

            if tt == 19:
                rec['target'] = 'field'
            else:
                rec['target'] = 'method'

            rec['str'] = rec['type'] + ':' + rec['target']


        elif tt == 22:
            rec['type'] = 'formal parameter'
            rec['target'] = 'method'
            rec['index'] = struct.unpack('B', data[offset:offset+1])[0]
            rec['str'] = rec['type'] + ':' + rec['target'] + ':' + str(rec['index'])
            offset += 1

        elif tt == 23:
            rec['type'] = 'throws'
            rec['target'] = 'method'
            rec['index'] = struct.unpack('B', data[offset:offset+1])[0]
            rec['str'] = rec['type'] + ':' + rec['target'] + ':' + str(rec['index'])
            offset += 1

        elif tt == 64 or tt == 65:
            if tt == 64:
                rec['type'] = 'local variable'
            else:
                rec['type'] == 'resource variable'
            rec['target'] = 'code'

            tlen = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            table = []
            while tlen > 0:
                spc, clen, ndx = struct.unpack('>3H', data[offset:offset+6])
                offset += 6
                tlen -= 1
                table.append({
                    'start_pc': spc,
                    'end_pc': spc + clen,
                    'index': ndx
                })
            rec['table'] = table
            rec['str'] = rec['type'] + ':' + rec['target']

        elif tt == 66:
            rec['type'] == 'catch'
            rec['target'] = 'code'
            rec['index'] = struct.unpack('B', data[offset:offset+1])[0]
            rec['str'] = rec['type'] + ':' + rec['target'] + ':' + str(rec['index'])
            offset += 1

        elif tt >= 67 and tt <= 70:
            rec['type'] = 'offset'
            rec['target'] = 'code'
            rec['offset'] = struct.unpack('>H', data[offset:offset+2])[0]
            rec['str'] = rec['type'] + ':' + rec['target'] + ':' + str(rec['offset'])
            offset += 2

        elif tt >= 71 and tt <= 75:
            rec['type'] = 'type argument'
            rec['target'] = 'code'
            rec['offset'] = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            rec['index'] = struct.unpack('B', data[offset:offset+1])[0]
            offset += 1
            rec['str'] = rec['type'] + ':' + rec['target'] + ':' + str(rec['index']) + ':' + str(rec['offset'])


        #
        # Decode type path
        #

        plen = struct.unpack('B', data[offset:offset+1])[0]
        offset += 1
        path = []

        while plen > 0:
            pkind, pndx = struct.unpack('2B', data[offset:offset+2])
            offset += 2
            plen -= 1

            path.append({
                'kind': pkind,
                'index': pndx
            })

        #
        # Decode rest of annotation
        #

        rec['annotations'], offset = self.decode_annotation(data, offset)

        return rec, offset
    
    

    def decode_annotation(self, data, offset):

        tndx, npairs = struct.unpack('>2H', data[offset:offset+4])
        offset += 4

        rec = {}
        _,s = self.getConstantPool(tndx)
        if s[0] == 'L':
            x = decodeType(s, None)
            x = x.replace('/', '.')
            self.__annotation_names.add(x)
        rec['annotation'] = s

        ev = []
        while npairs > 0:
            npairs -= 1
            endx = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            _,ename = self.getConstantPool(endx)
            el, offset =  self.decode_element_value(data, offset)
            if el is not None:
                el['element_name'] = ename
            ev.append(el)

        elements = []

        while npairs > 0:
            npairs -= 1

            nndx = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2

            _,ename = self.getConstantPool(nndx)

            etype = data[offset]   # Don't unpack as a byte
            offset += 1

            el, offset = self.decode_element_value(data,offset)
            elements.append(el)

        rec['element_values'] = elements

        if len(elements) != 0:
            rec['str'] = rec['annotation'] + ':[' + ",".join(sorted([x['str'] for x in elements])) + ']'
        else:
            rec['str'] = rec['annotation']

        return rec, offset
    
        
    def decodeRTAnnotation(self, data):

        offset = 0
        tn = []

        count = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2

        while count > 0:
            count -= 1
            a, offset = self.decode_annotation(data, offset)
            tn.append(a)
        

    def decodeAttributes(self, attr):
        a = {}

        for ndx, d in attr:
            s = self.__getStrConst(ndx)
            if s == 'ConstantValue':
                cndx = struct.unpack('>H', d[0:2])[0]
                a[s] = cndx
            elif s == 'Code':
                a[s] = self.decodeCodeAttr(d)
            elif s == 'StackMapTable':
                a[s] = self.decodeStackMapTableAttr(d)
            elif s in ['RuntimeVisibleTypeAnnotatons','RuntimeInvisibleTypeAnnotations']:
                a[s] = self.decodeRTTypeAnnotation(d)
            elif s in ['RuntimeVisibleAnnotations','RuntimeInvisibleAnnotations']:
                a[s] = self.decodeRTAnnotation(d)
            elif s in ['RuntimeInvisibleParameterAnnotations','RuntimeVisibleParameterAnnotations']:
                pass
            else:
                a[s] = d
                #sys.stderr.write(f"A: {s}\n")
                pass

        return a

    def getFieldByName(self, name):
        rec = self.fields_.get(name, None)
        if rec is None:
            return None
        if 'initialize' in rec:
            return rec
        for attr_name in rec['attr']:
            if attr_name != 'ConstantValue':
                continue
            ndx = rec['attr'][attr_name]
            t, v = self.getConstantPool(ndx)
            rec['initializer'] = {
                'type': t,
                'value': v
            }
            break
        return rec

    def className(self, raw=False):
        '''Returns the name of the class of the loaded class file'''
        return self.__getClassName(self.__class, raw)
    
    def classSuper(self, raw=False):
        '''Returns the name of the super class of the loaded class file'''
        if self.__super != 0:
            return self.__getClassName(self.__super, raw)
        return None

    def getConstantPool(self, ndx):
        if ndx > len(self.__constants):
            raise IndexError(f"Index {ndx} is past end of java class file constant pool (size={len(self.__constants)})")
        if ndx <= 0:
            raise IndexError(f"Invalid index {ndx} into java class file constant pool (index must be > 0)")

        
        c = self.__constants[ndx-1]
        type = c[0]
        if type == JavaClass.TAG_UTF8String:
            return ['U',self.__getStrConst(ndx)]
        elif type == JavaClass.TAG_Int32:
            return ['i',str(c[1])]
        elif type == JavaClass.TAG_Float:
            v = struct.unpack('>f',c[1])[0]
            return ['f',str(v)]
        elif type == JavaClass.TAG_Double:
            v = struct.unpack('>d',c[1])[0]
            return ['d',str(v)]
        elif type == JavaClass.TAG_Int64:
            v = struct.unpack('>q',c[1])[0]
            return ['l',str(v)]
        elif type == JavaClass.TAG_StringRef:
            return ['s',self.__getStrConst(c[1])]
        elif type == JavaClass.TAG_FieldRef:
            cn = self.__getClassName(c[1])
            cn = cn.replace("/",".")
            (n,t) = self.__getNameType(c[2])
            return ['F', cn+"."+n+","+t]
        elif type == JavaClass.TAG_MethodRef:
            cn = self.__getClassName(c[1])
            cn = cn.replace("/",".")
            (n,t) = self.__getNameType(c[2])
            return ['M',cn+"."+n+","+t]
        elif type == JavaClass.TAG_InterfaceMethodRef:
            (n,t) = self.__getNameType(c[2])
            return ['I',n+","+t]
        elif type == JavaClass.TAG_InvokeDynamic:
            (n,t) = self.__getNameType(c[2])
            return ['I',n+","+t]
        elif type == JavaClass.TAG_ClassRef:
            return ['c',self.__getStrConst(c[1])]
        else:
            return ['u',str(type)]

    def annotations(self):
        for name in self.__annotation_names:
            yield name
    
    def methodNames(self, raw=False):
        '''
        Returns a list of the defined method names in the class.

        Each element of the list contains a tuple consisting of the
        method name and the type signature of the method.
        '''
        for x in self.__methodInfo:
            if x[0] & 0x1040:
                continue
            name = self.__getStrConst(x[1], raw)
            if raw:
                if name == b'<init>':
                    name = self.className(raw)
                    slash = name.rfind(b'/')
                    if slash != -1:
                        name = name[slash+1:]
            elif name == '<init>':
                name = self.className(raw)
                slash = name.rfind("/")
                if slash != -1:
                    name = name[slash+1:]
            desc = self.__getStrConst(x[2], raw)
            yield (name, desc)

    def findAttribute(self, attr, id):
        for a in attr:
            name = self.__getStrConst(a[0], False)
            if name == id:
                return a
        return None

    def methods(self):
        for name in self.methods_:
            for r in self.methods_[name]:
                yield r

    def fields(self):
        for name in self.fields_:
            yield self.fields_[name]

    def get_method_by_sig(self, sig):
        return self.methods_by_sig_.get(sig, None)

    def getMethods(self):
        for x in self.__methodInfo:
            if x[0] & 0x1040:
                continue
            name = self.__getStrConst(x[1], False)
            if False:
                if name == '<clinit>' or name == '<init>':
                    name = self.className(False)
                    slash = name.rfind("/")
                    if slash != -1:
                        name = name[slash+1:]
            bytecode = None
            codeattr = self.findAttribute(x[3], "Code")
            if codeattr is not None:
                bytecode = codeattr[1]
            access = []
            flags = x[0]
            if flags & 0x0001:
                access.append("public")
            if flags & 0x0002:
                access.append("private")
            if flags & 0x0004:
                access.append("protected")
            if flags & 0x0008:
                access.append("static")
            if flags & 0x0010:
                access.append("final")
            if flags & 0x0400:
                access.append("abstract")

            desc = self.__getStrConst(x[2])
                
            yield (name, bytecode, desc, access)

    def fieldNames(self, raw=False):
        '''
        Returns a list of the defined fields in the class.

        Each element of the list contains a tuple consisting of the
        method name and the type signature of the method.
        '''
        return map(lambda x: (self.__getStrConst(x[1], raw),self.__getStrConst(x[2],raw)),
                   filter(lambda x: x[0] & 0x1040 == 0, self.__fields)
              )


    def methodRefs(self, raw=False):
        '''
        Returns a list of methods referenced by the class.

        Each element of the list contains a 3 element tuple. The first
        element is the class where the called class is located.  The second
        element is the method name, and the third is the type signature of
        the method.
        '''

        if self.__constants is None:
            return []

        for x in self.__constants:
            if x[0] == JavaClass.TAG_MethodRef:
                cname = self.__getClassName(x[1], raw)
                method,type = self.__getNameType(x[2],raw)
                yield (cname,method,type)

    def getReferences(self,raw=False):
        '''
        Returns a list of all references in the class.

        Each element of the list contains a 4 element tuple. The first
        element is the class where the reference is located.  The second
        element is the method name, and the third is the type signature of
        the method.  The fourth element is the type of reference: 'field',
        'method', or 'interface'.
        '''

        for x in self.__constants:
            
            tagname = None
            if raw:
                if x[0] == JavaClass.TAG_MethodRef:
                    tagname = b'method'
                elif x[0] == JavaClass.TAG_FieldRef:
                    tagname = b'field'
                elif x[0] == JavaClass.TAG_InterfaceMethodRef:
                    tagname = b'interface'
                else:
                    continue
            else:
                if x[0] == JavaClass.TAG_ClassRef:
                    cname = self.__getStrConst(x[1], raw)
                    yield (cname, None, None, 'classref')
                    continue
                elif x[0] == JavaClass.TAG_MethodRef:
                    tagname = 'method'
                elif x[0] == JavaClass.TAG_FieldRef:
                    tagname = 'field'
                elif x[0] == JavaClass.TAG_InterfaceMethodRef:
                    tagname = "interface"
                else:
                    continue

            cname = self.__getClassName(x[1], raw)
            method,type = self.__getNameType(x[2], raw)
            yield (cname,method,type,tagname)

    def getStrings(self, raw=False):
        '''Returns a list of all the string constants in the class file'''

        return map(lambda x: self.__getStrConst(x[1], raw),
                   filter(lambda x: x[0] == JavaClass.TAG_StringRef, self.__constants)
               )

    def getPackageName(self, raw=False):
        '''Returns the package name'''
        cname = self.className(raw)
        if raw:
            n = cname.rfind(b'/')
        else:
            n = cname.rfind('/')
        if n == -1:
            return None
        return cname[0:n]

    def getIntValues(self, raw=False):
        '''Returns a list of all the int32 constants in the class file'''

        if raw:
            return map(lambda x:x[2],
                   filter(lambda x: x[0] == JavaClass.TAG_Int32, self.__constants))
        
        return map(lambda x:x[1],
                   filter(lambda x: x[0] == JavaClass.TAG_Int32, self.__constants))

    def getInterfaces(self, raw=False):
        '''Returns a list of all implemented interfaces'''

        return map(lambda x: self.__getClassName(x,raw), self.__interfaces)

    
        
    #------------------------------------------------------------------------

    def __getClassName(self, index, raw=False):
        c = self.__constants[index-1]
        type = c[0]
        if type == JavaClass.TAG_ClassRef:
            return self.__getStrConst(c[1], raw)
        elif type == JavaClass.TAG_UTF8String:
            if raw:
                return c[1]
            return c[1].decode("utf-8", errors='replace')
        raise TypeError("Wrong type tag<"+str(type)+"> for class name record")

    def __getNameType(self, index, raw=False):
        c = self.__constants[index-1]
        type = c[0]
        if type == JavaClass.TAG_NameAndType:
            name = self.__getStrConst(c[1], raw)
            type = self.__getStrConst(c[2], raw)
            return (name,type)
        raise TypeError("Wrong type tag<"+str(type)+"> for name record")
        

    def __getMethodName(self, index, raw=False):
        c = self.__constants[index-1]
        type = c[0]
        if type == JavaClass.TAG_MethodRef:
            cname = self.__getClassName(c[1], raw)
            (name,type) = self.__getNameType(c[2], raw)
            return (cname, name, type)
        raise TypeError("Wrong type tag<"+str(type)+"> for method name record")

    def __getStrConst(self, index, raw=False):
        c = self.__constants[index-1]
        type = c[0]

        if type == JavaClass.TAG_UTF8String:
            if raw:
                return c[1]
            return c[1].decode("utf-8", errors='replace')
        raise TypeError("Wrong type tag<"+str(type)+"> for UTF-8 string constant")

    #------------------------------------------------------------------------

    def __readshort(self,data, offset):
        return struct.unpack('>H', data[offset:offset+2])[0]

    def __readlong(self,data, offset):
        return struct.unpack('>I', data[offset:offset+4])[0]

    def __readfm(self, data, res):

        if len(data) < 8:
            return False
        
        flags = self.__readshort(data, 0)
        index = self.__readshort(data, 2)
        desc = self.__readshort(data, 4)
        acount = self.__readshort(data, 6)

        d = data[8:]
        attr = []
        length = 8
        
        while acount > 0:
            n = self.__readattr(attr, d)
            if n == False:
                return False
            acount = acount - 1
            length = length + n
            d = d[n:]

        res.append((flags, index, desc, attr))
        return length

    def __readattr(self, attr, d):

        if len(d) < 6:
            return False

        index = self.__readshort(d, 0)
        alen = self.__readlong(d, 2)
        if len(d) < alen + 6:
            return False
        attr.append((index, d[6:alen+6]))
        return alen+6

    def __readconstant(self, data):

        if self.__NullSlot is True:
            self.__NullSlot = False
            self.__constants.append((None,None))
            return 0


        if len(data) < 3:
            return False

        tag = struct.unpack('B',data[0:1])[0]

        if tag == JavaClass.TAG_UTF8String:
            dlen = self.__readshort(data, 1)
            if len(data) < dlen + 3:
                return False
            self.__constants.append((tag, data[3:dlen+3]))
            return dlen + 3
                
        elif tag == JavaClass.TAG_NameAndType or tag == JavaClass.TAG_MethodRef or \
             tag == JavaClass.TAG_FieldRef or tag == JavaClass.TAG_InterfaceMethodRef:
            if len(data) < 5:
                return False
            index1 = self.__readshort(data, 1)
            index2 = self.__readshort(data, 3)
            self.__constants.append((tag, index1, index2))
            return 5
                
        elif tag == JavaClass.TAG_ClassRef or tag == JavaClass.TAG_StringRef:
            index = self.__readshort(data, 1)
            self.__constants.append((tag, index))
            return 3
                
        elif tag == JavaClass.TAG_Int32:
            if len(data) < 5:
                return False
            a = self.__readshort(data, 1)
            b = self.__readshort(data, 3)
            n = a << 16 | b
            self.__constants.append((tag, n, data[1:4]))
            return 5
                
        elif tag == JavaClass.TAG_Float:
            if len(data) < 5:
                return False
            self.__constants.append((tag, data[1:5]))
            return 5
                
        elif tag == JavaClass.TAG_Int64 or tag == JavaClass.TAG_Double: # Long/Double
            if len(data) < 9:
                return False
            self.__NullSlot = True
            self.__constants.append((tag, data[1:9]))
            return 9
                
        elif tag == JavaClass.TAG_MethodHandle:
            if len(data) < 4:
                return False
            self.__constants.append((tag, data[1:3]))
            return 4

        elif tag == JavaClass.TAG_MethodType:
            self.__constants.append((tag, data[1:3]))
            return 3
                
        elif tag == JavaClass.TAG_Dynamic:
            self.__constants.append((tag, data[1:3]))
            return 3
                
        elif tag == JavaClass.TAG_InvokeDynamic:
            if len(data) < 5:
                return False
            bma = self.__readshort(data, 1)
            nt = self.__readshort(data, 3)
            self.__constants.append((tag, bma, nt))
            return 5
                
        elif tag == JavaClass.TAG_Package or tag == JavaClass.TAG_Module:
            index = self.__readshort(data, 1)
            self.__constants.append((tag, index))
            return 3
                
        else:
            raise TypeError("Unrecognized tag<"+str(tag)+"> while loading constant pool")

    @staticmethod
    def decodeType(type, objName, argNames=None, isFunction=False):
        ndx = 0
        res = []
        args = None
        retType = None
        isArray = False

        argNDX = 0
        argID = 0

        while ndx < len(type):
            c = type[ndx]
            name = None
            if c == 'I':
                name = 'int'
                argNDX = 0
            elif c == 'Z':
                name = 'boolean'
                argNDX = 1
            elif c == 'B':
                argNDX = 0
                name = 'byte'
            elif c == 'C':
                argNDX = 5
                name = 'char'
            elif c == 'S':
                argNDX = 0
                name = 'short'
            elif c == 'J':
                argNDX = 0
                name = 'long'
            elif c == 'F':
                argNDX = 3
                name = 'float'
            elif c == 'D':
                argNDX = 3
                name = 'double'
            elif c == 'V':
                name = ""
            elif c == 'L':
                argNDX = 4
                ndx = ndx+1
                start=ndx
                while ndx < len(type) and type[ndx] != ';':
                    ndx = ndx+1
                name = type[start:ndx]
            elif c == '[':
                isArray=True
                ndx = ndx + 1
                continue

            elif c == '(':
                ndx = ndx + 1
                start = ndx
                while ndx < len(type) and type[ndx] != ')':
                    ndx = ndx+1
                args = '(' + JavaClass.decodeType(type[start:ndx], None, argNames, True) + ')'
            else:
                raise TypeError("Invalid character '"+c+"'in type signature "+type)

            if isArray:
                name = name + '[]'
            isArray = False

            if name is not None and args is None:
                if isFunction and argNames is not None:
                    res.append(name+" "+argNames[argNDX]+str(argID))
                    argID = argID + 1
                else:
                    res.append(name)
            else:
                retType = name
            ndx = ndx + 1


        if args:
            if retType == "":
                return objName + args
            else:
                return objName + args + " -> " + retType
        else:
            s = ", ".join(res)
            if objName is None:
                return s
            elif s == "":
                return objName
            else:
                return s + " " + objName
    #
    #  Returns [rettype,[arg:type,arg:type]]
    #
    @staticmethod
    def getArgs(type, argNames=None,isFunction=False):
        ndx = 0
        res = []
        args = False
        retType = None
        isArray = False

        argNDX = 0
        argID = 0

        arguments = []

        while ndx < len(type):
            c = type[ndx]
            name = None
            if c == 'I':
                name = 'i32'
                argNDX = 0
            elif c == 'Z':
                name = 'i1'
                argNDX = 1
            elif c == 'B':
                argNDX = 0
                name = 'i8'
            elif c == 'C':
                argNDX = 5
                name = 'i16'
            elif c == 'S':
                argNDX = 0
                name = 'i16'
            elif c == 'J':
                argNDX = 0
                name = 'i64'
            elif c == 'F':
                argNDX = 3
                name = 'f32'
            elif c == 'D':
                argNDX = 3
                name = 'f64'
            elif c == 'V':
                name = None
            elif c == 'L':
                argNDX = 4
                ndx = ndx+1
                start=ndx
                while ndx < len(type) and type[ndx] != ';':
                    ndx = ndx+1
                name = type[start:ndx].replace('/','.')
            elif c == '[':
                isArray=True
                ndx = ndx + 1
                continue

            elif c == '(':
                ndx = ndx + 1
                start = ndx
                while ndx < len(type) and type[ndx] != ')':
                    ndx = ndx+1
                res = JavaClass.getArgs(type[start:ndx], argNames, True)[1]
                args = True
            else:
                raise TypeError("Invalid character '"+c+"'in type signature "+type)

            if isArray:
                name = name + '[]'
            isArray = False

            if name is not None and args is False:
                if isFunction:
                    if argNames is not None:
                        res.append(argNames[argNDX]+str(argID)+":"+name)
                    else:
                        res.append(['%a'+str(argID),name])
                    argID = argID + 1
                else:
                    res.append(name)
            else:
                retType = name
            ndx = ndx + 1

        return [retType,res]
        
    def getArgTypes(self, type):
        ndx = 0
        rettype = None
        params = None
        isArray = 0
        getRetType = False
        res = []
        input = type

        raw = []

        while ndx < len(type):
            c = type[ndx]
            lt = None
            if c == 'I':
                lt = 'int'
                raw.append(c)
            elif c == 'Z':
                lt = 'boolean'
                raw.append(c)
            elif c == 'B':
                lt = 'byte'
                raw.append(c)
            elif c == 'C':
                lt = 'char'
                raw.append(c)
            elif c == 'S':
                lt = 'short'
                raw.append(c)
            elif c == 'J':
                lt = 'long'
                raw.append(c)
            elif c == 'F':
                lt = 'float'
                raw.append(c)
            elif c == 'D':
                lt = 'double'
                raw.append(c)
            elif c == 'V':
                lt = 'void'
                raw.append(c)
            elif c == 'L':
                ndx = ndx+1
                start=ndx
                while ndx < len(type) and type[ndx] != ';':
                    ndx = ndx+1
                lt = type[start:ndx]
                raw.append(c + lt + ';')
            elif c == '[':
                isArray+=1
                ndx = ndx + 1
                continue
            elif c == '(':
                ndx = ndx + 1
                start = ndx
                while ndx < len(type) and type[ndx] != ')':
                    ndx = ndx+1
                _, res, raw = self.getArgTypes(type[start:ndx])
                getRetType=True
                ndx += 1
                continue
            else:
                raise TypeError("Invalid character '"+c+"'in type signature "+type)

            lt = lt + ("[]" * isArray)
            isArray = 0

            if getRetType:
                rettype = lt
                getRetType = False
            else:
                res.append(lt)

            ndx = ndx + 1

        #print(f"--> {input} {rettype} {res}")
        return rettype, res, raw

    __bcnops={
        16:1,17:2,18:1,19:2,20:2,21:1,22:1,23:1,24:1,25:1,54:1,55:1,56:1,57:1,58:1,132:2,153:2,154:2,155:2,156:2,157:2,158:2,159:2,160:2,161:2,162:2,163:2,164:2,165:2,166:2,167:2,168:2,169:1,170:-1,171:-1,178:2,179:2,180:2,181:2,182:2,183:2,184:2,185:4,186:4,187:2,188:1,189:2,192:2,193:2,196:-2,197:2,198:2,199:2,200:4,201:4        
    }

    __bcstk_in={
        50:2,83:3,189:1,176:1,190:1,58:1,75:1,76:1,77:1,78:1,191:1,51:2,84:3,52:2,85:3,192:1,144:1,142:1,143:1,99:2,49:2,82:3,152:2,151:2,111:2,107:2,119:1,115:2,175:1,57:1,71:1,72:1,73:1,74:1,103:2,89:1,90:2,91:3,92:2,93:3,94:4,141:1,139:1,140:1,98:2,48:2,81:3,149:2,150:2,110:2,106:2,118:1,114:2,174:1,56:1,67:1,68:1,69:1,70:1,102:2,180:1,145:1,146:1,135:1,134:1,133:1,147:1,96:2,46:2,126:2,79:3,108:2,165:2,166:2,159:2,162:2,163:2,164:2,161:2,160:2,153:1,156:1,157:1,158:1,155:1,154:1,199:1,198:1,104:2,116:1,193:1,186:-1,185:-1,183:-1,184:-1,182:-1,128:2,112:2,172:1,120:2,122:2,54:1,59:1,60:1,61:1,62:1,100:2,124:2,130:2,138:1,137:1,136:1,97:2,47:1,127:2,80:3,148:2,109:2,105:2,117:1,171:1,129:2,113:2,173:1,121:2,124:2,55:1,63:1,64:1,65:1,66:1,101:2,125:2,131:2,194:1,195:1,197:-1,188:1,87:1,88:2,181:2,179:1,53:2,86:3,195:2,186:1,196:-1
    }

    __bcstk_out={
        58:0,75:0,76:0,77:0,78:0,202:0,85:0,57:0,71:0,72:0,73:0,74:0,89:2,90:3,91:4,92:4,93:5,94:6,81:0,56:0,67:0,68:0,69:0,70:0,165:0,166:0,159:0,162:0,163:0,164:0,161:0,160:0,153:0,156:0,157:0,158:0,155:0,154:0,199:0,198:0,54:0,59:0,60:0,61:0,62:0,171:0,55:0,63:0,64:0,61:0,62:0,194:0,195:0,87:0,88:0,179:0,177:0,86:0,186:0,196:-1
    }

    @classmethod
    def instructions(cls, bytecode):
        ndx=0
        nbytes = len(bytecode)

        while ndx < nbytes:
            op = bytecode[ndx]
                
            ndx += 1

            stkin=cls.__bcstk_in.get(op, 0)
            stkout=cls.__bcstk_out.get(op,1)

            if op not in cls.__bcnops:
                yield op, None, stkin, stkout
                continue
            
            nb = cls.__bcnops[op]
            
            if nb > 0:
                opbytes = bytecode[ndx:ndx+nb]
                ndx += nb
                yield op, list(opbytes), stkin, stkout
                continue

            if op == 170: #tableswitch
                while ndx & 3 != 0:
                    ndx += 1
                ip = ndx + 4
                lb, hb = struct.unpack('>2i', bytecode[ip:ip+8])
                count = 8 + 4*((hb-lb)+1)
                ops = bytecode[ndx:ndx+count]
                ndx = ip + count
                yield op, list(ops), stkin, stkout
                
            if op == 171: #lookupswitch
                while ndx & 3 != 0:
                    ndx += 1
                # Skip default target
                ip = ndx + 4
                npairs = struct.unpack('>I', bytecode[ip:ip+4])[0]
                count = 4 + npairs * 8
                ops = bytecode[ndx:ndx+count]
                ndx = ip + count
                yield op, list(ops), stkin, stkout
            if op == 196: #wide
                if bytecode[ndx] == 132:   # wide iinc
                    ops = bytecode[ndx:ndx+5]
                    ndx += 5
                    yield op, list(ops), 0, 0
                else:
                    stkin = cls.__bcstk_in.get(bytecode[ndx], 0)
                    stkout = cls.__bcstk_out.get(bytecode[ndx], 1)
                    ops = bytecode[ndx:ndx+3]
                    ndx += 3
                    yield op, list(ops), stkin, stkout
                
