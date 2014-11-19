'''
Sample config JSON stanza:

{
    "plugins": [
        {"id": "http://bibfra.me/tool/pybibframe#linkreport",
        "output-file": "/tmp/linkreport.html"}
    ]
}

Already built into demo config:

marc2bf -c test/resource/democonfig.json --mod=bibframe.plugin test/resource/gunslinger.marc.xml

'''

import os
import json
import itertools
import asyncio

from versa import I, ORIGIN, RELATIONSHIP, TARGET
from versa.util import simple_lookup

from amara3 import iri

from bibframe import BFZ, BFLC, g_services, BF_INIT_TASK, BF_MARCREC_TASK, BF_FINAL_TASK

ISBN_REL = I(iri.absolutize('isbn', BFZ))
TITLE_REL = I(iri.absolutize('title', BFZ))

BFHOST = 'bibfra.me'

#A plug-in is a series of callables, each of which handles a phase of
#Process

#The only phase predefined for all plug-ins is BF_INIT_TASK

#One convenient way to organize the Plug-in is as a class
#In this case we want to create a separate instance for each full processing event loop
class linkreport(object):
    PLUGIN_ID = 'http://bibfra.me/tool/pybibframe#linkreport'
    def __init__(self, pinfo, config=None):
        #print ('BF_INIT_TASK', linkreport.PLUGIN_ID)
        self._config = config or {}
        #If you need state maintained throughout a full processing loop, you can use instance attributes
        self._links_found = set()
        self._outstr = ''
        #Now set up the other plug-in phases
        pinfo[BF_MARCREC_TASK] = self.handle_record_links
        pinfo[BF_FINAL_TASK] = self.finalize
        return

    #acyncio.Task is used to manage the tasks, so it's a good idea to use the standard decorator
    #if you don't know what that means you should still be OK just using the sample syntax below as is, and just writign a regular function
    #But you can squeeze out a lot of power by getting to know the wonders of asyncio.Task
    @asyncio.coroutine
    def handle_record_links(self, loop, model, params):
        '''
        Task coroutine of the main event loop for MARC conversion, called with 
        In this case update a report of links encountered in the MARC/XML

        model -- raw Versa model with converted resource information from the MARC details from each MARC/XML record processed
        params -- parameters passed in from processing:
            params['workid']: ID of the work constructed from the MARC record
            params['instanceid']: list of IDs of instances constructed from the MARC record
        '''
        #print ('BF_MARCREC_TASK', linkreport.PLUGIN_ID)
        items = {}
        #Get the title
        #First get the work ID
        workid = params['workid']
        #simple_lookup() is a little helper for getting a property from a resource
        title = simple_lookup(model, workid, TITLE_REL)
        #Get the ISBN, just pick the first one
        isbn = ''
        if params['instanceids']:
            inst1 = params['instanceids'][0]
            isbn = simple_lookup(model, inst1, ISBN_REL)

        envelope = '<div id="{0}" isbn="{1}"><title>{2}</title>\n'.format(workid, isbn, title)
        #iterate over all the relationship targets to see which is a link
        for stmt in model.match():
            if iri.matches_uri_syntax(stmt[TARGET]) and iri.split_uri_ref(stmt[TARGET])[1] != BFHOST:
                self._links_found.add(stmt[TARGET])
                envelope += '<a href="{0}">{0}</a>\n'.format(stmt[TARGET], stmt[TARGET])
        envelope += '</div>\n'
        self._outstr += envelope
        #print ('DONE BF_MARCREC_TASK', linkreport.PLUGIN_ID)
        return

    @asyncio.coroutine
    def finalize(self, loop):
        '''
        Task coroutine of the main event loop for MARC conversion, called to finalize processing
        In this case generate the report of links encountered in the MARC/XML
        
        loop - async processing loop
        '''
        #print ('BF_FINAL_TASK', linkreport.PLUGIN_ID)
        with open(self._config['output-file'], "w") as outf:
            outf.write(self._outstr)
        return


PLUGIN_INFO = {linkreport.PLUGIN_ID: {BF_INIT_TASK: linkreport}}

