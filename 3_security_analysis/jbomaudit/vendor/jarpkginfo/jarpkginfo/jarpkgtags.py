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
import os

import zipfile as zip

try: 
    from .jarinfo import JarHandler
except:
    from jarinfo import JarHandler

def main():
    JarHandler.enable_recursion()

    for fn in sys.argv[1:]:
        if fn.endswith('.class'):
            jh=JarHandler("A")
            with open(fn, 'rb') as h:
                jh.process(h, fn, None, None)
            continue
        with zip.ZipFile(fn) as zf:
            jh = JarHandler(fn)
            for f in zf.infolist():
                with zf.open(f, 'r') as h:
                    jh.process(h, f.filename, None, None)
            jh.finish()

if __name__ == '__main__':
    main()