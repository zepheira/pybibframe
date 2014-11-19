'''
Sample config JSON stanza:

{
    "plugins": [
        {"id": "http://bibfra.me/tool/pybibframe#labelizer",
        "lookup": {"Work": "title", "Instance": "title", "Agent": "name", "Person": "name", "Organization": "name", "Place": "name", "Collection": "name", "Meeting": "name", "Topic": "name", "Geographic": "name", "Genre": "name"}
        }
    ]
}

Already built into demo config:

marc2bf -c test/resource/democonfig.json --mod=bibframe.plugin test/resource/gunslinger.marc.xml

'''

import os
import json
import itertools
import asyncio

from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET
from versa.util import simple_lookup

from amara3 import iri

from bibframe import BFZ, BFLC, g_services, BF_INIT_TASK, BF_MARCREC_TASK, BF_FINAL_TASK

RDF_NAMESPACE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDFS_NAMESPACE = 'http://www.w3.org/2000/01/rdf-schema#'

VTYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))
RDFS_LABEL = RDFS_NAMESPACE + 'label'

#A plug-in is a series of callables, each of which handles a phase of
#Process

#The only phase predefined for all plug-ins is BF_INIT_TASK

#One convenient way to organize the Plug-in is as a class
#In this case we want to create a separate instance for each full processing event loop
class labelizer(object):
    PLUGIN_ID = 'http://bibfra.me/tool/pybibframe#labelizer'
    def __init__(self, pinfo, config=None):
        #print ('BF_INIT_TASK', linkreport.PLUGIN_ID)
        self._config = config or {}
        #If you need state maintained throughout a full processing loop, you can use instance attributes
        #Now set up the other plug-in phases
        pinfo[BF_MARCREC_TASK] = self.handle_record_links
        pinfo[BF_MATRES_TASK] = self.handle_materialized_resource
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
        #Get the configured vocabulary base IRI
        vocabbase = params['vocabbase']
        for cls, prop in self._config['lookup'].items():
            for link in model.match(None, VTYPE_REL, I(iri.absolutize(cls, vocabbase))):
                #simple_lookup() is a little helper for getting a property from a resource
                val = simple_lookup(model, link[ORIGIN], I(iri.absolutize(prop, vocabbase)))
                if val:
                    model.add(link[ORIGIN], I(RDFS_LABEL), val)
        return

    @asyncio.coroutine
    def handle_materialized_resource(self, loop, model, params):
        '''
        Task coroutine of the main event loop for MARC conversion, called whenever a new resource is materialized
        In this case generate the report of links encountered in the MARC/XML
        
        loop - async processing loop
        
        You can set the value of params['renamed_materialized_id'] to rename the resource
        '''
        eid = params['materialized_id']
        first_seen = params['first_seen']
        logger = params['logger']
        logger.debug('Materialized resource with ID {0}{1}'.format(eid, ' (first encounter)' if first_seen else ''))
        return

    @asyncio.coroutine
    def finalize(self, loop):
        '''
        Task coroutine of the main event loop for MARC conversion, called to finalize processing
        In this case generate the report of links encountered in the MARC/XML
        
        loop - async processing loop
        '''
        return


PLUGIN_INFO = {labelizer.PLUGIN_ID: {BF_INIT_TASK: labelizer}}

