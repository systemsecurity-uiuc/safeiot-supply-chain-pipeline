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
import sys
import json
from io import StringIO, BytesIO
import zipfile as zip
import traceback

import xml.sax as sax
from xml.sax.handler import ContentHandler

try:
    import xmltodict
except:
    pass

try:
    from .javaclass import JavaClass
except:
    from javaclass import JavaClass
    
from hashlib import sha256

ATTR_MAP = {
    'Bundle-SymbolicName': 'pkg-name',
    'Bundle-Name': 'pkg-name2',
    'Bundle-Version': 'pkg-version',
    'Bundle-Description': 'pkg-description',
    'Bnd-LastModified': 'pkg-timestamp',
    'Bundle-Vendor' : 'pkg-vendor',
    'Bundle-License': lambda x: 'pkg-license-url' if str(x).startswith('http') else 'pkg-license',
}


class POM(ContentHandler):

    def setproperty(self, value, subtag=None):
        if subtag is not None:
            self.properties[subtag] = value

    #
    # Dependency info
    #
    def dgroupid(self, value, subtag=None):
        self.dependencies[value] = {}
        self.last_dependency = value

    def dgroupversion(self, value, subtag=None):
        if self.last_dependency is not None:
            if len(value) > 2 and value[0:2] == '${':
                key = value[2:-1]
                if key in self.properties:
                    value = self.properties[key]
                else:
                    sys.stderr.write(f"No value for variable {value} {self.filename}\n")
                    return

            self.dependencies[self.last_dependency]['version'] = value
        else:
            sys.stderr.write("Dependency version without prior dependency\n")

    def dartifactid(self, value, subtag=None):
        if self.last_dependency is not None:
            self.dependencies[self.last_dependency]['artifactid'] = value
        else:
            sys.stderr.write("Dependency artifactid without prior dependency\n")

    #
    # Information about the 'parent'
    #

    def pgroupid(self, value, subtag=None):
        self.rec['parent.groupid'] = value
        if 'project.groupId' not in self.properties:
            self.properties['project.groupId'] = value
        if 'groupid' not in self.rec:
            self.rec['groupid'] = value

    def partifactid(self, value, subtag=None):
        self.rec['parent.artifactid'] = value
        if 'project.artifactId' not in self.properties:
            self.properties['project.artifactId'] = value
        if 'artifactid' not in self.rec:
            self.rec['artifactid'] = value

    def pversion(self, value, subtag=None):
        self.rec['parent.version'] = value
        if 'project.version' not in self.properties:
            self.properties['project.version'] = value
        if 'version' not in self.rec:
            self.rec['version'] = value

    #
    # Information about this project
    #
    def groupid(self, value, subtag=None):
        self.rec['groupid'] = value
        self.properties['project.groupId'] = value

    def artifactid(self, value, subtag=None):
        self.rec['artifactid'] = value
        self.properties['project.artifactId'] = value

    def setname(self, value, subtag=None):
        self.rec['name'] = value

    def version(self, value, subtag=None):
        self.rec['version'] = value
        self.properties['project.version'] = value

    def license(self, value, subtag=None):
        self.licenses.append({})

    def licenseName(self, value, subtag=None):
        self.licenses[-1]['name'] = value

    def licenseURL(self, value, subtag=None):
        self.licenses[-1]['url'] = value

    def inithandlers(self):
        self.handlers = {
            'project.artifactId': self.artifactid,
            'project.groupId': self.groupid,
            'project.parent.groupId': self.pgroupid,
            'project.parent.artifactId': self.partifactid,
            'project.parent.version': self.pversion,
            'project.properties': self.setproperty,
            'project.name': self.setname,
            'project.dependencies.dependency.groupId': self.dgroupid,
            'project.dependencies.dependency.version': self.dgroupversion,
            'project.dependencies.dependency.artifactId': self.dartifactid,
            'project.licenses.license.name': self.licenseName,
            'project.licenses.license.url': self.licenseURL,
            'project.licenses.license': self.license
        }

    def __init__(self, filename=None):
        self.filename = filename
        self.rec = {}
        self.active = []
        self.properties = {}
        self.dependencies = {}
        self.licenses = []
        self.rec['imports'] = self.dependencies
        self.rec['licenses'] = self.licenses
        self.last_dependency = None
        self.inithandlers()

    def startElement(self, name, attrs):
        self.active.append(name)

    def endElement(self, name):
        self.active.pop()
        return

    def characters(self, content):
        content = content.strip()
        n = len(self.active)
        while n > 0:
            t = ".".join(self.active[0:n])
            if t in self.handlers:
                if n < len(self.active):
                    st = ".".join(self.active[n:])
                else:
                    st = None
                self.handlers[t](content, subtag=st)
                break
            n -= 1
        return


class JavaJar:


    def __init__(self):
        self.exports = None
        self.imports = None
        self.manifest = None
        return

    def parse_list(self, text, keywords):

        res = {}
        pkg = None

        while True:
            if len(text) == 0:
                break
            isKeyword = False
            for kw in keywords:
                if not text.startswith(kw):
                    continue

                n = len(kw)
                if text[n] == '=':
                    ndx = n + 1
                elif text[n:n + 2] == ':=':
                    ndx = n + 2
                else:
                    continue

                isKeyword = True
                if text[ndx] == '"':
                    start = ndx + 1
                    a = text.find(';')
                    b = text.find('",')
                    if a != -1 and (a < b or b == -1):
                        endpt = a
                    elif b != -1 and (b < a or a == -1):
                        endpt = b + 1
                    else:
                        endpt = -1

                    if endpt == -1:
                        v = text[start:]
                        text = ""
                    else:
                        v = text[start:endpt - 1]
                        text = text[endpt + 1:]
                else:
                    start = ndx
                    endpt = text.find(',')
                    if endpt == -1:
                        v = text[start:]
                        text = ""
                    else:
                        v = text[start:endpt]
                        text = text[endpt + 1:]

                res[pkg][kw] = v
                break

            if not isKeyword:
                ndx1 = text.find(',')
                ndx2 = text.find(';')
                if ndx1 != -1 and (ndx1 < ndx2 or ndx2 == -1):
                    ndx = ndx1
                elif ndx2 != -1 and (ndx2 < ndx1 or ndx1 == -1):
                    ndx = ndx2
                else:
                    ndx = -1

                if ndx == -1:
                    pkg = text
                    text = ""
                else:
                    pkg = text[0:ndx]
                    text = text[ndx + 1:]

                if pkg not in res:
                    res[pkg] = {}

        return res

    def parse_export(self, ep):
        self.exports = self.parse_list(ep, ["uses", "version"])
        if len(self.exports) == 0:
            self.exports = None
        if self.exports is not None:
            for k in self.exports:
                if 'uses' in self.exports[k]:
                    self.exports[k]['uses'] = self.exports[k]['uses'].split(',')

    def parse_import(self, ep):
        self.imports = self.parse_list(ep, ["version", "resolution"])
        if len(self.imports) == 0:
            self.imports = None

    def parse_manifest(self, input):

        curTag = None
        manifest = {}
        tag = None
        for line in input:
            line = line.rstrip()
            if len(line) == 0:
                continue
            if not line[0].isspace():
                tag, value = line.split(':', maxsplit=1)
                manifest[tag] = value.strip()
            else:
                value = line.strip()
                manifest[tag] += value

        if 'Export-Package' in manifest:
            ep = manifest['Export-Package']
            self.parse_export(ep)
            del manifest['Export-Package']

        if 'Import-Package' in manifest:
            ip = manifest['Import-Package']
            self.parse_import(ip)
            del manifest['Import-Package']

        if 'Main-Class' in manifest:
            manifest['Main-Class'] = '.'.join(manifest['Main-Class'].split('/'))

        self.manifest = manifest


class JarHandler:

    class_loaders = {
        'static': {
            'java.lang.Class.forName': {
                '(Ljava/lang/String;)Ljava/lang/Class;': 0,
                '(Ljava/lang/String;ZLjava/lang/ClassLoader;)Ljava/lang/Class;': 0
            },
            'java.rmi.server.RMIClassLoader.loadClass': {
                '(Ljava/net/URL;Ljava/lang/String;)Ljava/lang/Class;': 1,
                '(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Class;': 1,
                '(Ljava/lang/String;Ljava/lang/String;Ljava/lang/ClassLoader;)Ljava/lang/Class;': 1
            },
            'java.rmi.server.RMIClassLoader.loadProxyClass': {
                '(Ljava/lang/String;[Ljava/lang/String;Ljava/lang/ClassLoader;)Ljava/lang/Class;': None
            },
            'java.rmi.server.RMIClassLoaderSpi.loadClass': {
                '(Ljava/lang/String;Ljava/lang/String;Ljava/lang/ClassLoader;)Ljava/lang/Class;': 1
            },

            'javax.management.DefaultLoaderRepository.loadClass': {
                '(Ljava/lang/String;)Ljava/lang/Class;': 0
            },
            'javax.management.DefaultLoaderRepository.loadClassWithout': {
                '(Ljava/lang/ClassLoader;Ljava/lang/String;)Ljava/lang/Class;': 1
            },

            'javax.management.loading.loadClass': {
                '(Ljava/lang/String;)Ljava/lang/Class;': 0
            },
            
            'javax.management.loading.DefaultLoaderRepository.loadClassWithout': {
                '(Ljava/lang/ClassLoader;Ljava/lang/String;)Ljava/lang/Class;': 1,
            },

            'java.rmi.server.RMIClassLoader.loadClass': {
                '(Ljava/lang/String;)Ljava/lang/Class;': 0,
                '(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Class;': 1,
                '(Ljava/net/URL;Ljava/lang/String;)Ljava/lang/Class;': 1
            },

            'java.rmi.server.RMIClassLoader.loadProxyClasss': {
                '(Ljava/lang/String;[Ljava/lang/String;Ljava/lang/ClassLoader;)Ljava/lang/Class;': None
            },

            'java.rmi.server.RMIClassLoaderSpi.loadClass': {
                '(Ljava/lang/String;Ljava/lang/String;Ljava/lang/ClassLoader;)Ljava/lang/Class;': 1
            },
            
            'java.rmi.server.RMIClassLoaderSpi.loadProxyClass': {
                '(Ljava/lang/String;[Ljava/lang/String;Ljava/lang/ClassLoader;)Ljava/lang/Class;': None
            }
            
        },
        
       'virtual': {
           'java.lang.ClassLoader.loadClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0,
               '(Ljava/lang/String;Z)Ljava/lang/Class;': 0
           },
           'java.security.SecureClassLoader.loadClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0,
               '(Ljava/lang/String;Z)Ljava/lang/Class;': 0
           },
           'java.net.URLClassLoader.loadClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0,
               '(Ljava/lang/String;Z)Ljava/lang/Class;': 0
           },
           'javax.management.loading.Mlet.loadClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0,
               '(Ljava/lang/String;Ljava/management/loading/ClassLoaderRepository;)Ljava/lang/Class;': 0
           },
            
           'javax.management.loading.Mlet.findClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

           'java.lang.ClassLoader.findClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

           'java.lang.SecureClassLoader.findClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

           'java.lang.URLClassLoader.findClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },


           'java.lang.ClassLoader.findLoadedClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

           'java.lang.SecureClassLoader.findLoadedClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

           'java.lang.URLClassLoader.findLoadedClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

           'java.lang.ClassLoader.findSystemClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

           'java.lang.SecureClassLoader.findSystemClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

           'java.lang.URLClassLoader.findSystemClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },
           
           

           'javax.management.loading.Mlet.findLoadedClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },
           
           'javax.management.loading.Mlet.findSystemClass': {
               '(Ljava/lang/String;)Ljava/lang/Class;': 0
           },

        }
    }

    @classmethod
    def enable_recursion(cls):
        cls.recurse_jars = True

    def __init__(self, filename, is_child=False):
        self.imports = None
        self.exports = None
        self.manifest = None
        self.extern = set()
        self.reflections = set()
        self.reflected = {}
        self.packages = {}
        self.filedata = BytesIO()
        self.filename = filename
        self.digests = {}
        self.pom = None
        self.in_child = False
        self.child_info = []
        self.dynamic = set()
        return

    def process(self, file, fn, filetype, parent=None):

        if self.in_child:
            sys.stderr.write(f"{self.filename}: {fn}\n")

        if fn is None:
            file.close()
            return True

        if fn == 'META-INF/MANIFEST.MF':
            jj = JavaJar()
            s = StringIO()
            while True:
                d = file.read(-1)
                if d is None:
                    continue
                if len(d) == 0:
                    break
                s.write(d.decode('utf8', errors='replace'))
            s.seek(0, 0)
            file.close()
            jj.parse_manifest(s)
            self.exports = jj.exports
            self.imports = jj.imports
            self.manifest = jj.manifest
            return False
        elif self.recurse_jars and fn.endswith('.jar'):
            try:
                b = BytesIO()
                while True:
                    d = file.read(-1)
                    if d is None:
                        continue
                    if len(d) == 0:
                        break
                    b.write(d)
                self.rec = None
                b.seek(0, 0)
                with zip.ZipFile(b) as zf:
                    save_packages = self.packages
                    self.packages = {}
                    save_exports = self.exports
                    self.exports = None
                    save_imports = self.imports
                    self.imports = None
                    save_manifest = self.manifest
                    self.manifest = None
                    save_digests = self.digests
                    self.digests = {}
                    save_pom = self.pom
                    self.pom = None

                    save_dynamic = self.dynamic
                    self.dynamic = set()
                    save_ref1 = self.reflections
                    self.reflections = set()
                    save_ref2 = self.reflected
                    self.reflected = {}

                    save_child = self.child_info
                    self.child_info = []

                    for f in zf.infolist():
                        with zf.open(f, 'r') as h:
                            try:
                                self.process(h, f.filename, None, None)
                            except Exception as e:
                                sys.stderr.write(f"{fn}: {f.filename} {e}\n")
                                traceback.print_exc(file=sys.stderr)

                    self.collect_info(False)

                    self.packages = save_packages
                    self.exports = save_exports
                    self.imports = save_imports
                    self.manifest = save_manifest
                    self.digests = save_digests
                    self.pom = save_pom
                    self.reflections = save_ref1
                    self.reflected = save_ref2
                    self.child_info = save_child
                    self.dynamic = save_dynamic
                    if self.rec is not None:
                        self.child_info.append(self.rec)
                        self.rec = None
            except Exception as e:
                sys.stderr.write(f"{fn}: {e}\n")

        elif fn.endswith('.class'):
            jc = JavaClass()

            tb = 0
            h = sha256()
            while True:
                d = file.read(-1)

                if d is None:
                    continue

                if len(d) == 0:
                    break

                h.update(d)
                tb += len(d)
                try:
                    if jc.loadIncremental(d):
                        break
                except Exception as e:
                    sys.stderr.write(f"{fn}: {e}\n")
                    file.close()
                    return False

            flags = jc.get_flags()

            #
            # Skip module "classes"
            #
            if (flags & 0x8000) == 0x8000:
                file.close()
                return

            pkg = None
            try:
                pkg = jc.getPackageName()
            except Exception as e:
                sys.stderr.write(f"Corrupt class file: {fn} {e}\n")
                return False

            if pkg is not None:
                pkg = ".".join(pkg.split("/"))
            else:
                pkg = ''

            if pkg == '' and pkg :
                pkg = jc.className()

            if pkg not in self.packages:
                self.packages[pkg] = set()

            d = h.digest().hex()
            if pkg not in self.digests:
                self.digests[pkg] = {}

            self.digests[pkg][fn] = d

            try:
                s = jc.classSuper()
                if s is not None and s != 'java/lang/Object':
                    x = s.split('/')
                    x.pop()
                    x = ".".join(x)
                    if pkg != '':
                        self.packages[pkg].add(x)
            except:
                pass


            try:
                for c, m, s, what in jc.getReferences():
                    x = c.split('/')
                    x.pop()
                    x = ".".join(x)
                    while len(x) > 0 and (x[0] == '[' or x[0] == 'L'):
                        x = x[1:]
                    if x != '':
                        if pkg != '':
                            if pkg != x:
                                self.packages[pkg].add(x)
                        else:
                            self.extern.add(x)
            except Exception as e:
                sys.stderr.write(f"Corrupt class file: {fn}: {e}\n")
                pass


            for anno in jc.annotations():
                x = anno.split('.')
                x.pop()
                x = ".".join(x)
                if pkg != '':
                    if pkg != x:
                        self.packages[pkg].add(x)
                else:
                    self.extern.add(x)

            for f in jc.fields():
                s = f['signature']
                if s[0] != 'L':
                    continue
                pcn = s[1:-1]
                pcn = ".".join(pcn.split('/')[0:-1])
                if pkg != '':
                    if pkg != pcn:
                        self.packages[pkg].add(pcn)
                else:
                    self.extern.add(pcn)


            for m in jc.methods():

                for s in m['typesignatures']:
                    if s[0] != 'L':
                        continue
                    pcn = s[1:-1]
                    pcn = ".".join(pcn.split('/')[0:-1])
                    if pkg != '':
                        if pkg != pcn:
                            self.packages[pkg].add(pcn)
                    else:
                        self.extern.add(pcn)
                
                if 'Code' not in m['attr']:
                    continue

                bytecode = m['attr']['Code']['code']

                stk = []
                frame = [None] * 32


                for inst, ops, sin, sout in jc.instructions(bytecode):
                    #if debug:
                    #sys.stderr.write(f"{inst} {ops} {sin} {sout} {len(stk)}\n")
                    if inst not in [18, 19, 20, 184, 182]:
                        if inst in [186, 185, 183]:  # various invokes
                            # 183: invokespecial
                            # 185: invokeinterface
                            # 186: invokedynamic
                            #
                            # invokestatic handled separately
                            #------------------------------------------------
                            # Figure out how many parameters in call
                            # in order to maintain stack
                            ndx = (ops[0] << 8) | ops[1]
                            #sys.stderr.write(f"{m['fullname']} -> {inst} {ops}: ")
                            rv, sin = self.get_pcount(jc, ndx)
                            if rv is None:  # Void return type
                                sout = 0
                            else:
                                sout = 1
                        while sin > 0 and len(stk) > 0:
                            stk.pop()
                            sin -= 1
                        while sout > 0:
                            stk.append(None)
                            sout -= 1

                        continue
                    if inst == 18:  # ldc
                        what, value = jc.getConstantPool(ops[0])
                        if what == 's':
                            stk.append(value)
                        else:
                            stk.append(None)
                    elif inst == 19: # ldc_w
                        ndx = (ops[0] << 8) | ops[1]
                        what, value = jc.getConstantPool(ndx)
                        if what == 's':
                            stk.append(value)
                        else:
                            stk.append(None)
                    elif inst == 20: # ldc2_w
                        stk.append(None)  # This can't be a string
                    elif inst == 58: # astore
                        ndx = ops[0]
                        frame[ndx] = stk.pop()
                    elif inst in [0x4b, 0x4c, 0x4d, 0x4e]: # astore_#
                        ndx = inst - 0x4b
                        frame[ndx] = stk.pop()
                    elif inst == 25: # aload
                        ndx = ops[0]
                        stk.append(frame[ndx])
                    elif inst in [0x2a, 0x2b, 0x2c, 0x2d]: # aload_#
                        ndx = inst - 0x2a
                        stk.append(frame[ndx])
                    elif inst == 182: # invokevirtual
                        ndx = (ops[0] << 8) | ops[1]
                        rv, sin = self.get_pcount(jc, ndx)
                        what, value = jc.getConstantPool(ndx)
                        svalues = []

                        sin += 1

                        if len(stk) < sin:
                            sys.stderr.write(f"{sin} {len(stk)} i={inst} {value}\n")
                            sys.stderr.write(f"Insufficient stack values\n")
                            sys.stderr.write(f"{m['fullname']}\n")
                            sys.stderr.write("Populating with None values\n")
                            while len(stk) < sin:
                                stk.append(None)
                        while sin > 0:   # and len(stk) > 0:
                            v = stk.pop()
                            svalues.append(v)
                            sin -= 1
                        svalues = list(reversed(svalues))
                        if rv is not None:
                            # Go ahead and push a None call return value
                            stk.append(None)
                        if what == 'M':
                            mname, sig = value.split(',')
                            vmethods = self.class_loaders['virtual']
                            if mname in vmethods:
                                if sig in vmethods[mname]:
                                    # Add one to account for object handle
                                    argp = vmethods[mname][sig] + 1
                                    if argp is not None and len(svalues) > argp:
                                        arg = svalues[argp]
                                    else:
                                        arg = None
                                    if arg is not None:
                                        x = arg.split('.')
                                        x.pop()
                                        v = ".".join(x)
                                        if pkg != '':
                                            if pkg not in self.reflected:
                                                self.reflected[pkg] = set()
                                            self.reflected[pkg].add(v)
                                        else:
                                            self.reflections.add(v)
                                    else:
                                        self.dynamic.add((pkg, fn))
                                        
                    elif inst == 184: # invokestatic
                        ndx = (ops[0] << 8) | ops[1]
                        rv, sin = self.get_pcount(jc, ndx)
                        what, value = jc.getConstantPool(ndx)
                        svalues = []

                        if len(stk) < sin:
                            sys.stderr.write(f"{sin} {len(stk)} i={inst} {value}\n")
                            sys.stderr.write(f"Insufficient stack values\n")
                            sys.stderr.write(f"{m['fullname']}\n")
                            sys.stderr.write("Populating with None values\n")
                            while len(stk) < sin:
                                stk.append(None)
                        while sin > 0:   # and len(stk) > 0:
                            v = stk.pop()
                            svalues.append(v)
                            sin -= 1
                        svalues = list(reversed(svalues))
                        if rv is not None:
                            # Go ahead and push a None call return value
                            stk.append(None)
                        if what == 'M':
                            mname, sig = value.split(',')
                            smethods = self.class_loaders['static']
                            if mname in smethods:
                                if sig in smethods[mname]:
                                    argp = smethods[mname][sig]
                                    if argp is not None and  len(svalues) > argp:
                                        arg = svalues[argp]
                                    else:
                                        arg = None
                                    if arg is not None:
                                        x = arg.split('.')
                                        x.pop()
                                        v = ".".join(x)
                                        if pkg != '':
                                            if pkg not in self.reflected:
                                                self.reflected[pkg] = set()
                                            self.reflected[pkg].add(v)
                                        else:
                                            self.reflections.add(v)
                                    else:
                                        self.dynamic.add((pkg, fn))

            file.close()
            return False
        elif fn.endswith('.jar'):
            file.close()
            return False
        elif fn.endswith("/pom.xml") and fn.startswith('META-INF/'):
            x = b''
            while True:
                d = file.read(-1)
                if d is None:
                    continue
                if len(d) == 0:
                    break
                x += d

            x = x.decode('utf8')

            h = POM(filename=fn)
            try:
                sax.parseString(x, h)
            except Exception as e:
                sys.stderr.write(f"{fn} Exception parsing pom.xml: {e}\n")
                file.close()
                return False

            try:
                s = xmltodict.parse(x)
                h.rec['pom'] = s
            except:
                pass

            if len(h.rec['licenses']) == 0:
                del h.rec['licenses']

            self.pom = h.rec

            file.close()
            return False

        file.close()
        return False

    def get_pcount(self, jc, ndx):
        what, value = jc.getConstantPool(ndx)
        mname, tsig = value.split(',')
        rv, args = jc.getArgs(tsig)
        #sys.stderr.write(f"{mname} {tsig} {rv} {len(args)}\n")
        return rv, len(args)

    def finish(self):
        self.collect_info(True)

    def collect_info(self, record):

        for p in self.packages:
            r = {
                'uses': list(self.packages[p])
            }
            if p in self.digests:
                r['digests'] = self.digests[p]

            self.packages[p] = r

        if len(self.extern) != 0:
            r = {
                'uses': list(self.extern)
            }
            if len(self.reflections) != 0:
                r['reflected'] = list(self.reflections)

            self.packages['unpackaged'] = r

        for p in self.reflected:
            if p not in self.packages:
                self.packages[p] = {}
            self.packages[p]['reflected'] = list(self.reflected[p])

        for pkg, fn in self.dynamic:
            if p not in self.packages:
                self.packages[p] = {}
            self.packages[p].setdefault('unresolved_dynamic', []).append(fn)

        rec = {}
        rec['packages'] = self.packages

        if self.exports is not None:
            rec['exports'] = self.exports
        if self.imports is not None:
            rec['imports'] = self.imports
        if self.manifest is not None:
            rec['manifest'] = self.manifest

        if self.pom is not None:
            rec['pom'] = self.pom

        rec = self.pkg_tags_remap(rec)
        if len(self.child_info) != 0:
            rec['jars'] = self.child_info

        if not record:
            rec['filename'] = self.filename
            self.rec = rec
        else:
            attr = json.dumps(rec)
            print(attr)
        return

    def dispatch(self, data):
        if data is not None:
            self.filedata.write(data)
        else:
            self.finish()
        return True

    def pkg_tags_remap(self, tags):
        tags['pkg-type'] = 'jar'
        manifest = tags.get('manifest')
        if manifest:
            for k, map_k in ATTR_MAP.items():
                v = manifest.get(k)
                if v is not None:
                    if callable(map_k):
                        map_k = map_k(v)
                    tags[map_k] = v

        return tags
