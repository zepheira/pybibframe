'''
Sample config JSON stanza:

{
    "plugins": [
        {"id": "http://bibfra.me/tool/pybibframe#labelizer",
        "lookup": {
            "http://bibfra.me/vocab/lite/Work": "http://bibfra.me/vocab/lite/title",
            "http://bibfra.me/vocab/lite/Instance": "http://bibfra.me/vocab/lite/title",
            "http://bibfra.me/vocab/lite/Agent": "http://bibfra.me/vocab/lite/name",
            "http://bibfra.me/vocab/lite/Person": "http://bibfra.me/vocab/lite/name",
            "http://bibfra.me/vocab/lite/Organization": "http://bibfra.me/vocab/lite/name",
            "http://bibfra.me/vocab/lite/Place": "http://bibfra.me/vocab/lite/name",
            "http://bibfra.me/vocab/lite/Collection": "http://bibfra.me/vocab/lite/name",
            "http://bibfra.me/vocab/lite/Meeting": "http://bibfra.me/vocab/lite/name",
            "http://bibfra.me/vocab/lite/Topic": "http://bibfra.me/vocab/lite/name",
            "http://bibfra.me/vocab/lite/Form": "http://bibfra.me/vocab/lite/name",
            "http://bibfra.me/vocab/lite/Foobar": [" $","http://bibfra.me/vocab/lite/title","http://bibfra.me/vocab/lite/name"]
            }
        "default-label": "UNKNOWN LABEL"
        },
    ]
}

Tuple notation in lookup configuration is used to join multiple properties in order, using the
first item as the separator ('' for no separator). If the separator ends with a "$" then
then the original ordering present in the MARC record will be used instead of the order of
the given properties, and the properties will be used purely as a filter. The "$" is ignored
as part of the separator.

Already built into demo config:

marc2bf -c test/resource/democonfig.json --mod=bibframe.plugin test/resource/gunslinger.marc.xml

'''

import os
import json
import itertools
import asyncio

from itertools import tee, zip_longest

from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET
from versa.util import simple_lookup

from amara3 import iri

from bibframe import BFZ, BFLC, g_services, BF_INIT_TASK, BF_MARCREC_TASK, BF_MATRES_TASK, BF_FINAL_TASK

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
        #Get the configured default vocabulary base IRI
        vocabbase = params['vocabbase']
        for obj,_r,typ,_a in model.match(None, VTYPE_REL, None):
            # build labels based on model order, iterating over every property of
            # every resource, and building the label if that property is consulted 
            prop = self._config['lookup'].get(typ)
            if prop is None: continue

            props = prop if isinstance(prop, list) else ['', prop]

            def pairwise(iterable):
                a, b = tee(iterable)
                next(b, None)
                return zip_longest(a, b)

            label = ''
            marc_order = False
            sep = props[0] # separator
            if sep.endswith('$'):
                link_stream = pairwise((l for l in model.match(obj, None, None) if l[1] in props[1:]))
                sep = sep[:-1]
            else:
                link_stream = pairwise((l for p in props[1:] for l in model.match(obj, p, None)))

            #print("LABELIZING {} of type {}".format(obj, typ))
            for (link1, link2) in link_stream:

                _o1,rel1,target1,_a1 = link1
                _o2,rel2,target2,_a2 = link2 if link2 is not None else (None, None, None, None)

                label += target1
                if rel2 == rel1:
                    label += ' | '
                elif rel2 is not None:
                    label += sep
                #print("current label", label)

            if len(label) > 0:
                model.add(obj, I(RDFS_LABEL), label)
            elif 'default-label' in self._config:
                model.add(obj, I(RDFS_LABEL), self._config['default-label'])

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

