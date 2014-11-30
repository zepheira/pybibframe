'''

Requires http://pytest.org/ e.g.:

pip install pytest

----
'''

import sys
import logging
import asyncio
import unittest
from io import StringIO

from versa.driver import memory
from versa.util import jsondump, jsonload

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

class BasicTest(unittest.TestCase):
    '''
    Use a new event loop per test, and so one call of bfconvert per test
    '''

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def test_model_consumed(self):
        m = memory.connection()
        with open(os.path.join(RESOURCEPATH, 'multiple-authlinks.xml')) as indoc:
            bfconvert([indoc], entbase='http://example.org/', model=m, config=None, verbose=False, loop=self.loop)

        assert m.size() == 0, 'Model not consumed: '+repr(m)

    def test_simple_verify(self,name='gunslinger'):
        m = memory.connection()
        m_expected = memory.connection()
        s = StringIO()
        with open(os.path.join(RESOURCEPATH, name+'.mrx')) as indoc:
            bfconvert(indoc, model=m, out=s, canonical=True, loop=self.loop)
            s.seek(0)
            jsonload(m, s)

        with open(os.path.join(RESOURCEPATH, name+'.versa')) as indoc:
            jsonload(m_expected, indoc)

        with open('m-'+name,'w') as indoc:
            indoc.write(repr(m))
        with open('me-'+name,'w') as indoc:
            indoc.write(repr(m_expected))
        assert m==m_expected, "Discrepancy found in {0}".format(name)

    def test_simple_verify2(self):
        self.test_simple_verify(name='egyptskulls')

    def test_simple_verify3(self):
        self.test_simple_verify(name='kford-holdings1')

if __name__ == '__main__':
    raise SystemExit("use py.test")
