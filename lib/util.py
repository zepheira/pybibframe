import time
import logging
import json

from amara3 import iri

from versa.util import duplicate_statements, OrderedJsonEncoder
from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES

from bibframe import BF_INIT_TASK, BF_INPUT_TASK, BF_INPUT_XREF_TASK, BF_MARCREC_TASK, BF_MATRES_TASK, BF_FINAL_TASK
from bibframe.contrib.datachefids import idgen

BL = 'http://bibfra.me/vocab/lite/'
TYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))

# XXX: Possibly move to Versa proper, as well as some of the other canonical / ordered Versa bits
from versa.driver import memory
from versa.util import jsondump, jsonload
from collections import OrderedDict

def hash_neutral_model(stream):
    '''
    >>> VJSON = """[
    ["DoVM1hvc","http://bibfra.me/purl/versa/type","http://bibfra.me/vocab/lite/Person",{"@target-type": "@iri-ref"}],
    ["DoVM1hvc","http://bibfra.me/vocab/lite/date","1878-1967.",{}],
    ["DoVM1hvc","http://bibfra.me/vocab/lite/name","Sandburg, Carl,",{}],
    ["DoVM1hvc","http://bibfra.me/vocab/marcext/sf-a","Sandburg, Carl,",{}],
    ["DoVM1hvc","http://bibfra.me/vocab/marcext/sf-d","1878-1967.",{}],
    ["Ht2FQsIY","http://bibfra.me/purl/versa/type","http://bibfra.me/vocab/lite/Instance",{"@target-type": "@iri-ref"}],
    ["Ht2FQsIY","http://bibfra.me/vocab/lite/instantiates","XsrrgYIS",{"@target-type": "@iri-ref"}],
    ["XsrrgYIS","http://bibfra.me/purl/versa/type","http://bibfra.me/vocab/lite/Work",{"@target-type": "@iri-ref"}],
    ["XsrrgYIS","http://bibfra.me/purl/versa/type","http://bibfra.me/vocab/marc/Books",{"@target-type": "@iri-ref"}],
    ["XsrrgYIS","http://bibfra.me/purl/versa/type","http://bibfra.me/vocab/marc/LanguageMaterial",{"@target-type": "@iri-ref"}],
    ["XsrrgYIS","http://bibfra.me/vocab/lite/creator","DoVM1hvc",{"@target-type": "@iri-ref"}],
    ["XsrrgYIS","http://bibfra.me/vocab/marc/natureOfContents","encyclopedias",{}],
    ["XsrrgYIS","http://bibfra.me/vocab/marc/natureOfContents","legal articles",{}],
    ["XsrrgYIS","http://bibfra.me/vocab/marc/natureOfContents","surveys of literature",{}],
    ["XsrrgYIS","http://bibfra.me/vocab/marcext/tag-008","920219s1993 caua j 000 0 eng",{}]
    ]"""
    >>> from io import StringIO, BytesIO
    >>> s = StringIO(VJSON)
    >>> from bibframe.util import hash_neutral_model
    >>> hashmap, model = hash_neutral_model(s)
    >>> hashmap
    {'XsrrgYIS': '@R0', 'DoVM1hvc': '@R1', 'Ht2FQsIY': '@R2'}
    >>> [ (o, r, t, a) for (rid, (o, r, t, a)) in model ][0] #Safe ordering for memory model only, mind you
    ('@R1', 'http://bibfra.me/vocab/lite/name', 'Sandburg, Carl,', OrderedDict())
    '''
    stage1 = memory.connection()
    stage2 = memory.connection()
    stage3 = memory.connection()
    jsonload(stage1, stream)
    hashmap = {}
    #One pass for origins
    dummy = repr(stage1) #Mysterious bug (presumably in jsonload): attributes lose all their contents without this line
    for (rid, (o, r, t, a)) in sorted(stage1, key=lambda x:x[1][0]): # sort by resource id
        hash_neutral_origin = hashmap.setdefault(o, '@R{}'.format(len(hashmap)))
        stage2.add(hash_neutral_origin, r, t, a)
    del stage1 #clean up
    #Another pass for targets
    for (rid, (o, r, t, a)) in sorted(stage2):
        hash_neutral_target = t
        if a.get("@target-type") == "@iri-ref":
            hash_neutral_target = hashmap.get(t, t)
        stage3.add(o, r, hash_neutral_target, a)
    return hashmap, stage3


#FIXME: Avoid mangling data arg without too much perf hit
def materialize_entity(etype, ctx_params=None, model_to_update=None, data=None, addtype=True, loop=None, logger=logging):
    '''
    Routine for creating a BIBFRAME resource. Takes the entity (resource) type and a data mapping
    according to the resource type. Implements the Libhub Resource Hash Convention
    As a convenience, if a vocabulary base is provided, concatenate it to etype and the data keys

    data - list of key/value pairs used to compute the hash. If empty the hash will be a default for the entity type
            WARNING: THIS FUNCTION MANGLES THE data ARG
    '''
    ctx_params = ctx_params or {}
    vocabbase = ctx_params.get('vocabbase', BL)
    entbase = ctx_params.get('entbase')
    existing_ids = ctx_params.get('existing_ids', set())
    plugins = ctx_params.get('plugins')
    logger = ctx_params.get('logger', logging)
    output_model = ctx_params.get('output_model')
    ids = ctx_params.get('ids', idgen(entbase))
    if vocabbase and not iri.is_absolute(etype):
        etype = vocabbase + etype
    params = {'logger': logger}

    data = data or []
    if addtype: data.insert(0, [TYPE_REL, etype])
    data_full =  [ ((vocabbase + k if not iri.is_absolute(k) else k), v) for (k, v) in data ]
    plaintext = json.dumps(data_full, separators=(',', ':'), cls=OrderedJsonEncoder)

    eid = ids.send(plaintext)

    if model_to_update:
        model_to_update.add(I(eid), TYPE_REL, I(etype))

    params['materialized_id'] = eid
    params['first_seen'] = eid in existing_ids
    params['plaintext'] = plaintext
    for plugin in plugins or ():
        #Not using yield from
        if BF_MATRES_TASK in plugin:
            for p in plugin[BF_MATRES_TASK](loop, output_model, params): pass
        #logger.debug("Pending tasks: %s" % asyncio.Task.all_tasks(loop))
    return eid
