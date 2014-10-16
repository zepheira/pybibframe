'''
marc2bfrdf -v -o /tmp/ph1.ttl -s /tmp/ph1.stats.js -b http://example.org test/resource/princeton-holdings1.xml 2> /tmp/ph1.log

'''

import re
import os
import json
import time
import logging
import string
import itertools
import asyncio

#from datachef.ids import simple_hashstring
from bibframe.contrib.datachefids import idgen, FROM_EMPTY_HASH

#from amara.lib import U
from amara3 import iri
#from amara import namespaces
#from amara3.util import coroutine

from versa import I, VERSA_BASEIRI
from versa.util import simple_lookup
from versa.pipeline import *

from bibframe.reader.util import initialize
from bibframe import BFZ, BFLC, g_services
from bibframe import BF_INIT_TASK, BF_MARCREC_TASK, BF_FINAL_TASK
from bibframe.isbnplus import isbn_list
from bibframe.reader.marcpatterns import TRANSFORMS, bfcontext
from bibframe.reader.marcextra import process_leader, process_008

LEADER = 0
CONTROLFIELD = 1
DATAFIELD = 2

#canonicalize_isbns
#from btframework.augment import lucky_viaf_template, lucky_idlc_template, DEFAULT_AUGMENTATIONS

FALINKFIELD = '856'
#CATLINKFIELD = '010a'
CATLINKFIELD = 'LCCN'
CACHEDIR = os.path.expanduser('~/tmp')

NON_ISBN_CHARS = re.compile('\D')

NEW_RECORD = 'http://bibfra.me/purl/versa/' + 'newrecord'

def invert_dict(d):
    #http://code.activestate.com/recipes/252143-invert-a-dictionary-one-liner/#c3
    #See also: http://pypi.python.org/pypi/bidict
        #Though note: http://code.activestate.com/recipes/576968/#c2
    inv = {}
    for k, v in d.items():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv


TYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))


def isbn_instancegen(params):
    '''
    Default handling of the idea of splitting a MARC record with FRBR Work info as well as instances signalled by ISBNs


    '''
    #Handle ISBNs re: https://foundry.zepheira.com/issues/1976
    entbase = params['entbase']
    model = params['model']
    vocabbase = params['vocabbase']
    logger = params['logger']
    ids = params['ids']
    rec = params['rec']
    existing_ids = params['existing_ids']
    workid = params['workid']

    isbns = marc_lookup(rec, ['020$a'])
    logger.debug('Raw ISBNS:\t{0}'.format(isbns))

    normalized_isbns = list(isbn_list(isbns, logger=logger))

    subscript = ord('a')
    instance_ids = []
    logger.debug('Normalized ISBN:\t{0}'.format(normalized_isbns))
    if normalized_isbns:
        for subix, (inum, itype) in enumerate(normalized_isbns):
            instanceid = ids.send(['Instance', workid, inum])
            if entbase: instanceid = I(iri.absolutize(instanceid, entbase))

            model.add(I(instanceid), I(iri.absolutize('isbn', vocabbase)), inum)
            #subitem['id'] = instanceid + (unichr(subscript + subix) if subix else '')
            if itype: model.add(I(instanceid), I(iri.absolutize('isbnType', vocabbase)), itype)
            instance_ids.append(instanceid)
    else:
        instanceid = ids.send(['Instance', workid])
        if entbase: instanceid = I(iri.absolutize(instanceid, entbase))
        model.add(I(instanceid), TYPE_REL, I(iri.absolutize('Instance', vocabbase)))
        existing_ids.add(instanceid)
        instance_ids.append(instanceid)

    for instanceid in instance_ids:
        model.add(instanceid, I(iri.absolutize('instantiates', vocabbase)), I(workid))
        model.add(I(instanceid), TYPE_REL, I(iri.absolutize('Instance', vocabbase)))

    return instance_ids


def instance_postprocess(params):
    instanceids = params['instanceids']
    model = params['model']
    if len(instanceids) > 1:
        base_instance_id = instanceids[0]
        for instanceid in instanceids[1:]:
            duplicate_statements(model, base_instance_id, instanceid)
    return


def marc_lookup(rec, fieldspecs):
    result = []
    lookup_helper = dict(( f.split('$') for f in fieldspecs ))
    #dict((target_code, target_sf = fieldspec.split('$')
    for row in rec:
        if row[0] == DATAFIELD:
            rowtype, code, xmlattrs, subfields = row
            if code in lookup_helper:
                result.extend(subfields.get(lookup_helper[code], ''))
    return result


RECORD_HASH_KEY_FIELDS = [
    '130$a', '240$a', '240$b', '240$c', '240$h', '245$a', '245$b', '245$n', '245$p', '246$a', '246$i', '246$n', '246$p', '830$a', #Title info
    #'130$a', '240$a', '240$b', '240$c', '240$h', '245$a', '246$a', '246$i', '250$a', '250$b', '830$a', #Title info
    '100$a', '100$d', '100$q', '110$a', '110$c', '110$d', '111$a', '110$c', '110$d', #Creator info
    '700$a', '700$d', '710$a', '710$b', '710$d', #Contributor info
    '600$a', '610$a', '611$a', '650$a', '650$x', '651$a', '615$a', '690$a' #Subject info
]


def record_hash_key(rec):
    return ''.join(marc_lookup(rec, RECORD_HASH_KEY_FIELDS))


@asyncio.coroutine
def record_handler(loop, relsink, entbase=None, vocabbase=BFZ, limiting=None, plugins=None,
                   ids=None, postprocess=None, out=None, logger=logging, transforms=TRANSFORMS, **kwargs):
    '''
    loop - asyncio event loop
    entbase - base IRI used for IDs of generated entity resources
    limiting - mutable pair of [count, limit] used to control the number of records processed
    '''
    _final_tasks = set() #Tasks for the event loop contributing to the MARC processing
    
    plugins = plugins or []
    if ids is None: ids = idgen(entbase)

    #FIXME: For now always generate instances from ISBNs, but consider working this through th plugins system
    instancegen = isbn_instancegen

    existing_ids = set()
    initialize(hashidgen=ids, existing_ids=existing_ids)
    #Start the process of writing out the JSON representation of the resulting Versa
    if out: out.write('[')
    first_record = True
    try:
        while True:
            rec = yield
            leader = None
            #Add work item record, with actual hash resource IDs based on default or plugged-in algo
            #FIXME: No plug-in support yet
            workhash = record_hash_key(rec)
            workid = ids.send('Work:' + workhash)
            existing_ids.add(workid)
            logger.debug('Uniform title from 245$a: {0}'.format(marc_lookup(rec, ['245$a'])))
            logger.debug('Work hash result: {0} from \'{1}\''.format(workid, 'Work' + workhash))

            if entbase: workid = I(iri.absolutize(workid, entbase))
            relsink.add(I(workid), TYPE_REL, I(iri.absolutize('Work', vocabbase)))

            params = {'workid': workid, 'rec': rec, 'logger': logger, 'model': relsink, 'entbase': entbase, 'vocabbase': vocabbase, 'ids': ids, 'existing_ids': existing_ids}

            #Figure out instances
            instanceids = instancegen(params)
            if instanceids:
                instanceid = instanceids[0]

            params['instanceids'] = instanceids
            params['transforms'] = [] # set()
            params['fields_used'] = []
            for row in rec:
                code = None

                if row[0] == LEADER:
                    params['leader'] = leader = row[1]
                elif row[0] == CONTROLFIELD:
                    code, val = row[1], row[2]
                    key = 'tag-' + code
                    if code == '008':
                        params['field008'] = field008 = val
                    params['transforms'].append((code, key))
                    relsink.add(I(instanceid), I(iri.absolutize(key, vocabbase)), val)
                    params['fields_used'].append((code,))
                elif row[0] == DATAFIELD:
                    code, xmlattrs, subfields = row[1], row[2], row[3]
                    #xmlattribs include are indicators
                    indicators = ((xmlattrs.get('ind1') or ' ')[0].replace(' ', '#'), (xmlattrs.get('ind2') or ' ')[0].replace(' ', '#'))
                    key = 'tag-' + code

                    handled = False
                    params['subfields'] = subfields
                    params['indicators'] = indicators
                    params['fields_used'].append(tuple([code] + list(subfields.keys())))

                    to_process = []
                    #logger.debug(repr(indicators))
                    if indicators != ('#', '#'):
                        #One or other indicator is set, so let's check the transforms against those
                        lookup = '{0}-{1}{2}'.format(*((code,) + indicators))
                    for k, v in subfields.items():
                        lookup = '{0}${1}'.format(code, k)
                        for valitems in v:
                            if lookup in transforms: to_process.append((transforms[lookup], valitems))

                    if code in transforms:
                        to_process.append((transforms[code], ''))
                    else:
                        params.setdefault('dropped_codes',{}).setdefault(code,0)
                        params['dropped_codes'][code] += 1

                    #if code == '100':
                    #    logger.debug(to_process)

                    #Apply all the handlers that were found
                    for funcinfo, val in to_process:
                        #Support multiple actions per lookup
                        funcs = funcinfo if isinstance(funcinfo, tuple) else (funcinfo,)
                        #Build Versa processing context
                        for func in funcs:
                            ctx = bfcontext(workid, code, [(workid, code, val, subfields)], relsink, base=vocabbase, hashidgen=ids, existing_ids=existing_ids)
                            new_stmts = func(ctx, workid, instanceid)
                            #XXX: Use add_many?
                            for s in new_stmts: relsink.add(*s)

                    if not to_process:
                        #Nothing else has handled this data field; go to the fallback
                        fallback_rel_base = 'tag-' + code
                        for k, v in subfields.items():
                            fallback_rel = fallback_rel_base + k
                            #params['transforms'].append((code, fallback_rel))
                            for valitem in v:
                                relsink.add(I(workid), I(iri.absolutize(fallback_rel, vocabbase)), valitem)

                params['code'] = code

            special_properties = {}
            for k, v in process_leader(leader):
                special_properties.setdefault(k, set()).add(v)

            for k, v in process_008(field008):
                special_properties.setdefault(k, set()).add(v)
            params['special_properties'] = special_properties

            #We get some repeated values out of leader & 008 processing, and we want to
            #Remove dupes so we did so by working with sets then converting to lists
            for k, v in special_properties.items():
                special_properties[k] = list(v)
                for item in v:
                #logger.debug(v)
                    relsink.add(I(instanceid), I(iri.absolutize(k, vocabbase)), item)

            instance_postprocess(params)

            logger.debug('+')

            for plugin in plugins:
                #Each plug-in is a task
                #task = asyncio.Task(plugin[BF_MARCREC_TASK](loop, relsink, params), loop=loop)
                yield from plugin[BF_MARCREC_TASK](loop, relsink, params)
                logger.debug("Pending tasks: %s" % asyncio.Task.all_tasks(loop))
                #FIXME: This blocks and thus serializes the plugin operation, rather than the desired coop scheduling approach
                #For some reason seting to async task then immediately deferring to next task via yield from sleep leads to the "yield from wasn't used with future" error (Not much clue at: https://codereview.appspot.com/7396044/)
                #yield from asyncio.Task(asyncio.sleep(0.01), loop=loop)
                #yield from asyncio.async(asyncio.sleep(0.01))
                #yield from asyncio.sleep(0.01) #Basically yield to next task

            #Can we somehow move this to passed-in postprocessing?
            if out and not first_record: out.write(',\n')
            if out:
                first_record = False
                last_chunk = None
                #Using iterencode avoids building a big JSON string in memory, or having to resort to file pointer seeking
                #Then again builds a big list in memory, so still working on opt here
                for chunk in json.JSONEncoder().iterencode([ link for link in relsink ]):
                    if last_chunk is None:
                        last_chunk = chunk[1:]
                    else:
                        out.write(last_chunk)
                        last_chunk = chunk
                if last_chunk: out.write(last_chunk[:-1])
            #FIXME: Postprocessing should probably be a task too
            if postprocess: postprocess(rec)
            #limiting--running count of records processed versus the max number, if any
            limiting[0] += 1
            if limiting[1] is not None and limiting[0] >= limiting[1]:
                break
    except GeneratorExit:
        logger.debug('Completed processing {0} record{1}.'.format(limiting[0], '' if limiting[0] == 1 else 's'))
        if out: out.write(']')

        #if not plugins: loop.stop()
        for plugin in plugins:
            #Each plug-in is a task
            task = asyncio.Task(plugin[BF_FINAL_TASK](loop), loop=loop)
            _final_tasks.add(task)
            def task_done(task):
                #print('Task done: ', task)
                _final_tasks.remove(task)
                #logger.debug((plugins))
                #if plugins and len(_final_tasks) == 0:
                    #print("_final_tasks is empty, stopping loop.")
                    #loop = asyncio.get_event_loop()
                #    loop.stop()
            #Once all the plug-in tasks are done, all the work is done
            task.add_done_callback(task_done)
        #print('DONE')
        #raise

    return


def duplicate_statements(model, oldorigin, neworigin):
    '''
    Take links with a given origin, and create duplicate links with the same information but a new origin

    :param model: Versa model to be updated
    :param oldres: resource IRI to be duplicated
    :param newres: origin resource IRI for duplication
    :return: None
    '''
    for link in model.match(oldorigin):
        o, r, t, a = link
        model.add(I(neworigin), r, t, a)
    return


def replace_entity_resource(model, oldres, newres):
    '''
    Replace one entity in the model with another with the same links

    :param model: Versa model to be updated
    :param oldres: old/former resource IRI to be replaced
    :param newres: new/replacement resource IRI
    :return: None
    '''
    oldrids = set()
    for rid, link in model:
        if link[ORIGIN] == oldres or link[TARGET] == oldres or oldres in link[ATTRIBUTES].values():
            oldrids.add(rid)
            new_link = (newres if o == oldres else o, r, newres if t == oldres else t, dict((k, newres if v == oldres else v) for k, v in a.items()))
            model.add(*new_link)
    model.delete(oldrids)
    return

