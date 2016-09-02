'''
Sample config JSON stanza:

{
    "plugins": [
        {"id": "http://bibfra.me/tool/pybibframe#labelizer",
        "lookup": {
            "http://bibfra.me/vocab/lite/Foobar": {
                "separator": " ",
                "marcOrder": True,
                "properties": ["http://bibfra.me/vocab/lite/title","http://bibfra.me/vocab/lite/name"]
            },
            "http://bibfra.me/vocab/lite/Grobnitz": [ {
                    "separator": "lambda ctx: '-' if ctx['nextProperty'] == "http://bibfra.me/vocab/lite/name" else ' '"],
                    "wrapper": "lambda ctx: '[]' if 'medium' in ctx['currentProperty'] else None",
                    "multivalSeparator": " | ",
                    "marcOrder": True,
                    "properties": ["http://bibfra.me/vocab/lite/title","http://bibfra.me/vocab/lite/name"]
                },
                {
                    "separator": ' ',
                    "marcOrder": True,
                    "properties": ["http://bibfra.me/vocab/lite/p1", "http://bibfra.me/vocab/lite/p2"]
                }
            }
        "default-label": "UNKNOWN LABEL"
        },
    ]
}

The configuration is specified using a dictionary with type URIs as keys, and one or more
rule dictionaries as values (a single rule dict requires no list enclosure).  If the
first rule dictionary fails to produce a label, the next rule dictionary is used. If at
the end of this process no label has been produced, the label specified in "default-label"
will be returned. Each rule dictionary can contain these keys; "separator" which
specifies the string used to separate property values, "multivalSeparator" which specifies the
separator used when the property value is multi-valued, "wrapper" which specifies
a string of length two whose respective characters will be used to wrap the property value,
"marcOrder" a boolean that indicates whether the properties values should be ordered as
they were encountered in the MARC if True (otherwise the order in the "properties" key
will be used), and "properties" containing the list of property URIs.

"separator" and "wrapper" can be callables that return strings when provided a context
dictionary describing the state of the labelizing process. The four keys in the context
are currentProperty, currentValue, nextProperty, and nextValue.

Note that as the configuration needs to be represented as JSON, the callables are
encapsulated as strings. As non-callables are also strings, there's ambiguity there
that we resolve by asserting that any string longer than 5 characters will be
treated as a callable. Of course, if this configuration is consumed as a Python
dictionary, then the values can be actual callables.

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

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip_longest(a, b)

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
            rule = self._config['lookup'].get(typ)
            if rule is None: continue

            rules = rule if isinstance(rule, list) else [rule]

            label = ''
            for rule in rules:

                def chunk_eval(s):
                    # used when configuration is stored in JSON and one of these labelizer instructions is an eval-able string
                    # a known Python injection attack vector, so mentioned in README
                    if isinstance(s, str) and len(s) > 5:
                        s = eval(s, {'I': I}, locals())
                    return s

                marc_order = rule.get('marcOrder', False)
                separator = chunk_eval(rule.get('separator', ' '))
                wrapper = chunk_eval(rule.get('wrapper', None))
                multivalsep = chunk_eval(rule.get('multivalSeparator', ' | '))
                props = rule.get('properties', [])

                if marc_order:
                    link_stream = pairwise((l for l in model.match(obj, None, None) if l[1] in props))
                else:
                    link_stream = pairwise((l for p in props for l in model.match(obj, p, None)))

                #print("LABELIZING {} of type {}".format(obj, typ))
                for (link1, link2) in link_stream:

                    _o1,rel1,target1,_a1 = link1
                    _o2,rel2,target2,_a2 = link2 if link2 is not None else (None, None, None, None)

                    ctx = {
                        'currentProperty': rel1,
                        'currentValue': target1,
                        'nextProperty': rel2,
                        'nextValue': target2,
                    }

                    _wrapper = wrapper(ctx) if callable(wrapper) else wrapper
                    if _wrapper:
                        target1 = _wrapper[0]+target1+_wrapper[1]

                    label += target1
                    if rel2 == rel1:
                        _multivalsep = multivalsep(ctx) if callable(multivalsep) else multivalsep
                        label += _multivalsep
                    elif rel2 is not None:
                        _separator = separator(ctx) if callable(separator) else separator
                        label += _separator
                    #print("current label", label)

                if label:
                    model.add(obj, I(RDFS_LABEL), label)
                    break # we've found a rule that produces a label, so skip other rules

                label = ''

            if not label and 'default-label' in self._config:
                # if we've gone through all rules and not produced a label, yield specified default
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
