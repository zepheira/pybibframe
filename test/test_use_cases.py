'''

Requires http://pytest.org/ e.g.:

pip install pytest

----
'''

import sys
import logging
import asyncio
import difflib
from io import StringIO, BytesIO

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader.marcxml import bfconvert

import pytest

#Move to a test utils module
import os, inspect
def module_path(local_function):
   ''' returns the module path without the use of __file__.  Requires a function defined 
   locally in the module.
   from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
   return os.path.abspath(inspect.getsourcefile(local_function))

#hack to locate test resource (data) files regardless of from where nose was run
RESOURCEPATH = os.path.normpath(os.path.join(module_path(lambda _: None), '../resource/'))

def file_diff(s_orig, s_new):
    diff = difflib.unified_diff(s_orig.split('\n'), s_new.split('\n'))
    return '\n'.join(list(diff))

def run_one(name, entbase=None, config=None, loop=None, canonical=True):
    m = memory.connection()
    m_expected = memory.connection()
    s = StringIO()

    with open(os.path.join(RESOURCEPATH, name+'.mrx'), 'rb') as indoc:
        bfconvert(indoc, model=m, out=s, config=config, canonical=canonical, loop=loop)
        s.seek(0)
        jsonload(m, s)

    with open(os.path.join(RESOURCEPATH, name+'.versa')) as indoc:
        jsonload(m_expected, indoc)

    assert m == m_expected, "Discrepancies found for {0}:\n{1}".format(name, file_diff(repr(m_expected), repr(m)))


NAMES = ['gunslinger', 'egyptskulls', 'kford-holdings1', 'timathom-140716', 'joycebcat-140613']

@pytest.mark.parametrize('name', NAMES)
def test_usecases(name):
    #Use a new event loop per test instance, and so one call of bfconvert per test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    config = None
    run_one(name, config=config, loop=loop)

def test_model_consumed():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    m = memory.connection()
    with open(os.path.join(RESOURCEPATH, 'multiple-authlinks.xml'), 'rb') as indoc:
        bfconvert([indoc], entbase='http://example.org/', model=m, config=None, verbose=False, loop=loop)

    assert m.size() == 0, 'Model not consumed:\n'+repr(m)


if __name__ == '__main__':
    raise SystemExit("use py.test")
