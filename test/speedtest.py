#!/usr/bin/env python
'''

----
'''

import sys
import logging
import asyncio
import timeit
import io
from io import StringIO, BytesIO

from amara3.inputsource import factory, inputsource

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader import bfconvert
from bibframe.util import hash_neutral_model

import bibframe.plugin


#Move to a test utils module
import os, inspect
def module_path(local_function):
   ''' returns the module path without the use of __file__.  Requires a function defined
   locally in the module.
   from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
   return os.path.abspath(inspect.getsourcefile(local_function))

#hack to locate test resource (data) files regardless of from where this was run
RESOURCEPATH = os.path.normpath(os.path.join(module_path(lambda _: None), '../../test/resource/'))

NLOOPS = 100

def run_one(name, entbase=None, config=None, variation=''):
    m = memory.connection()
    m_expected = memory.connection()
    s = StringIO()

    fpath = os.path.join(RESOURCEPATH, name+'.mrx')
    instream = BytesIO(open(fpath, 'rb').read())

    print('Running {} ...'.format('('+variation+')' if variation else ''), fpath)

    def main():
        #Need a new event loop per timeit iteration
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(None);
        instream.seek(io.SEEK_SET)
        bfconvert(instream, model=m, out=s, config=config, loop=loop)

    global_space = globals()
    global_space.update(locals())
    timing = timeit.timeit('main()', setup='', number=NLOOPS, globals=global_space)
    print('{} loops, best of 3: {:.2f} sec per loop.'.format(NLOOPS, timing))


NAMES = [ 'gunslinger',
          'egyptskulls',
          'kford-holdings1',
          'timathom-140716',
          'joycebcat-140613',
          'zweig-tiny',
          'zweig' # test of folding between different unique() statements
        ]

def run():
    for name in NAMES:
        config = None
        run_one(name, config=config, variation='')
        config =  {
            "plugins": [ {
                "id": "http://bibfra.me/tool/pybibframe#labelizer",
                "lookup": {
                    "http://bibfra.me/vocab/lite/Instance": [ {
                        "properties": [ "http://bibfra.me/vocab/lite/titleStatement" ]
                    },
                    {
                        "separator": '=',
                        "wrapper": '[]',
                        "marcOrder": True,
                        "properties": [ "http://bibfra.me/vocab/lite/title",
                                        "http://bibfra.me/vocab/marc/titleRemainder",
                                        "http://bibfra.me/vocab/lite/medium",
                                        "http://bibfra.me/vocab/marc/titleStatement" ]
                    } ]
                },
                "default-label": "!UNKNOWN LABEL"
            } ]
        }
        run_one(name, config=config, variation='with marc_order')

run()
