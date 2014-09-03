'''

Requires http://pytest.org/ e.g.:

pip install pytest

----
'''

import sys
import logging

from versa.driver import memory
from versa.util import jsondump

from bibframe.reader.marcxml import bfconvert

#Move to a test utils module
import os, inspect
def module_path(local_function):
   ''' returns the module path without the use of __file__.  Requires a function defined 
   locally in the module.
   from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
   return os.path.abspath(inspect.getsourcefile(local_function))

#hack to locate test resource (data) files regardless of from where nose was run
RESOURCEPATH = os.path.normpath(os.path.join(module_path(lambda _: None), '../resource/'))

def test_basic_marc1():
    #logging.debug('MARC BASICS PART 1')
    m = memory.connection()
    indoc = open(os.path.join(RESOURCEPATH, 'multiple-authlinks.xml'))
    bfconvert([indoc], entbase='http://example.org/', model=m, config=None, verbose=False, logger=logging)

    jsondump(m, sys.stderr)
    #logging.debug(recs)
    assert m == ()


if __name__ == '__main__':
    raise SystemExit("use py.test")

