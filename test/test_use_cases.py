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

import pytest

from amara3.inputsource import factory, inputsource

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader import bfconvert
from bibframe.util import hash_neutral_model


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

    fname = os.path.join(RESOURCEPATH, name+'.mrx')
    #bfconvert(factory(open(fname, 'rb')), model=m, out=s, config=config, canonical=canonical, loop=loop)
    #raise(Exception(repr(inputsource(open(fname, 'rb')))))

    bfconvert([inputsource(open(fname, 'rb'))], model=m, out=s, config=config, canonical=canonical, loop=loop)
    s.seek(0)
    hashmap, m = hash_neutral_model(s)
    hashmap = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap.items() ]))

    with open(os.path.join(RESOURCEPATH, name+'.versa')) as indoc:
        hashmap_expected, m_expected = hash_neutral_model(indoc)
        hashmap_expected = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap_expected.items() ]))

    assert hashmap == hashmap_expected, "Changes to hashes found for {0}:\n{1}\n\nActual model structure diff:\n{2}".format(name, file_diff(hashmap_expected, hashmap), file_diff(repr(m_expected), repr(m)))
    assert m == m_expected, "Discrepancies found for {0}:\n{1}".format(name, file_diff(repr(m_expected), repr(m)))


NAMES = [ 'gunslinger',
          'egyptskulls',
          'kford-holdings1',
          'timathom-140716',
          'joycebcat-140613',
          'zweig-tiny',
          'zweig' # test of folding between different unique() statements
        ]

#NAMES = ['zweig-tiny']


@pytest.mark.parametrize('name', NAMES)
def DISABLE_test_usecases(name):
    #Use a new event loop per test instance, and so one call of bfconvert per test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    config = None
    run_one(name, config=config, loop=loop)


def test_model_consumed():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    m = memory.connection()
    fname = os.path.join(RESOURCEPATH, 'multiple-authlinks.mrx')
    #bfconvert([inputsource(open(fname, 'rb'))], entbase='http://example.org/', model=m, config=None, verbose=False, loop=loop)
    bfconvert([open(fname, 'rb')], entbase='http://example.org/', model=m, config=None, verbose=False, loop=loop)

    assert m.size() == 0, 'Model not consumed:\n'+repr(m)


if __name__ == '__main__':
    raise SystemExit("use py.test")
