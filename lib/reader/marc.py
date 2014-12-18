'''
marc2bfrdf -v -o /tmp/ph1.ttl -s /tmp/ph1.stats.js -b http://example.org test/resource/princeton-holdings1.xml 2> /tmp/ph1.log

'''

import re
import os
import json
import logging
import itertools
import asyncio
from collections import defaultdict, OrderedDict

#from datachef.ids import simple_hashstring
from bibframe.contrib.datachefids import idgen, FROM_EMPTY_HASH

#from amara.lib import U
from amara3 import iri
#from amara import namespaces
#from amara3.util import coroutine

from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES
from versa.util import simple_lookup, OrderedJsonEncoder
from versa.driver import memory
from versa.pipeline import *

from bibframe.reader.util import WORKID, IID
from bibframe import BFZ, BFLC, g_services
from bibframe import BF_INIT_TASK, BF_MARCREC_TASK, BF_MATRES_TASK, BF_FINAL_TASK
from bibframe.isbnplus import isbn_list
from bibframe.reader.marcpatterns import TRANSFORMS, bfcontext
from bibframe.reader.marcextra import transforms as extra_transforms


MARCXML_NS = "http://www.loc.gov/MARC21/slim"

NON_ISBN_CHARS = re.compile('\D')

NEW_RECORD = 'http://bibfra.me/purl/versa/' + 'newrecord'

# Namespaces 

BL = 'http://bibfra.me/vocab/lite/'
ISBNNS = 'http://bibfra.me/vocab/rda/'

TYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))

def invert_dict(d):
    #http://code.activestate.com/recipes/252143-invert-a-dictionary-one-liner/#c3
    #See also: http://pypi.python.org/pypi/bidict
        #Though note: http://code.activestate.com/recipes/576968/#c2
    inv = {}
    for k, v in d.items():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv


def marc_lookup(model, codes):
    #Note: should preserve code order in order to maintain integrity when used for hash input
    if isinstance(codes, str):
        codes = [codes]
    for code in codes:
        tag, sf = code.split('$') if '$' in code else (code, None)
        #Check for data field
        links = model.match(None, MARCXML_NS + '/data/' + tag)
        for link in links:
            for result in link[ATTRIBUTES].get(sf, []):
                yield (code, result)

        #Check for control field
        links = model.match(None, MARCXML_NS + '/control/' + tag)
        for link in links:
            yield code, link[TARGET]


def isbn_instancegen(params):
    '''
    Default handling of the idea of splitting a MARC record with FRBR Work info as well as instances signalled by ISBNs


    '''
    #Handle ISBNs re: https://foundry.zepheira.com/issues/1976
    entbase = params['entbase']
    output_model = params['output_model']
    input_model = params['input_model']
    vocabbase = params['vocabbase']
    logger = params['logger']
    materialize_entity = params['materialize_entity']
    existing_ids = params['existing_ids']
    workid = params['workid']
    
    isbns = list(( val for code, val in marc_lookup(input_model, '020$a')))
    logger.debug('Raw ISBNS:\t{0}'.format(isbns))

    # sorted to remove non-determinism which interferes with canonicalization
    normalized_isbns = sorted(list(isbn_list(isbns, logger=logger)))

    subscript = ord('a')
    instance_ids = []
    logger.debug('Normalized ISBN:\t{0}'.format(normalized_isbns))
    if normalized_isbns:
        for subix, (inum, itype) in enumerate(normalized_isbns):
            #XXX Do we use vocabbase? Probably since if they are substituting a new vocab base, we assume they're substituting semantics entirely
            instanceid = materialize_entity(iri.absolutize('Instance', vocabbase), instantiates=workid, isbn=inum, existing_ids=existing_ids)
            #ids.send(['', ])
            if entbase: instanceid = I(iri.absolutize(instanceid, entbase))

            # output_model.add(I(instanceid), I(iri.absolutize('isbn', vocabbase)), inum)
            output_model.add(I(instanceid), I(iri.absolutize('isbn', ISBNNS)), inum)
            #subitem['id'] = instanceid + (unichr(subscript + subix) if subix else '')
            if itype: output_model.add(I(instanceid), I(iri.absolutize('isbnType', ISBNNS)), itype)
            existing_ids.add(instanceid)
            instance_ids.append(instanceid)
    else:
        instanceid = materialize_entity(iri.absolutize('Instance', vocabbase), instantiates=workid, existing_ids=existing_ids)
        if entbase: instanceid = I(iri.absolutize(instanceid, entbase))
        output_model.add(I(instanceid), TYPE_REL, I(iri.absolutize('Instance', vocabbase)))
        existing_ids.add(instanceid)
        instance_ids.append(instanceid)

    output_model.add(instance_ids[0], I(iri.absolutize('instantiates', vocabbase)), I(workid))
    output_model.add(I(instance_ids[0]), TYPE_REL, I(iri.absolutize('Instance', vocabbase)))

    return instance_ids


def instance_postprocess(params):
    instanceids = params['instanceids']
    model = params['output_model']
    if len(instanceids) > 1:
        base_instance_id = instanceids[0]
        for instanceid in instanceids[1:]:
            duplicate_statements(model, base_instance_id, instanceid)
    return


RECORD_HASH_KEY_FIELDS = [
    '130$a', '240$a', '240$b', '240$c', '240$h', '245$a', '245$b', '245$n', '245$p', '246$a', '246$i', '246$n', '246$p', '830$a', #Title info
    '250$a', '250$b', #Edition
    '100$a', '100$d', '100$q', '110$a', '110$c', '110$d', '111$a', '110$c', '110$d', #Creator info
    '700$a', '700$d', '710$a', '710$b', '710$d', #Contributor info
    '600$a', '610$a', '611$a', '650$a', '650$x', '651$a', '615$a', '690$a' #Subject info
]


def record_hash_key(model):
    #Creating the hash with a delimeter between input fields just makes even slighter the collision risk
    return '|'.join(sorted(list( val for code, val in marc_lookup(model, RECORD_HASH_KEY_FIELDS))))


@asyncio.coroutine
def record_handler(loop, model, entbase=None, vocabbase=BL, limiting=None, plugins=None,
                   ids=None, postprocess=None, out=None, logger=logging, transforms=TRANSFORMS, extra_transforms=extra_transforms(), canonical=False, **kwargs):
    '''
    loop - asyncio event loop
    model - the Versa model for the record
    entbase - base IRI used for IDs of generated entity resources
    limiting - mutable pair of [count, limit] used to control the number of records processed
    '''
    _final_tasks = set() #Tasks for the event loop contributing to the MARC processing
    
    plugins = plugins or []
    if ids is None: ids = idgen(entbase)

    #FIXME: For now always generate instances from ISBNs, but consider working this through th plugins system
    instancegen = isbn_instancegen

    existing_ids = set()
    #Start the process of writing out the JSON representation of the resulting Versa
    if out and not canonical: out.write('[')
    first_record = True

    def materialize_entity(etype, vocabbase=vocabbase, existing_ids=existing_ids, unique=None, **data):
        '''
        Routine for creating a BIBFRAME resource. Takes the entity (resource) type and a data mapping
        according to the resource type. Implements the Libhub Resource Hash Convention
        As a convenience, if a vocabulary base is provided, concatenate it to etype and the data keys
        '''
        params = {}
        etype = vocabbase + etype
        data_full = { vocabbase + k: v for (k, v) in data.items() }
        # nobody likes non-deterministic ids! ordering matters to hash()
        data_full = OrderedDict(sorted(data_full.items(), key=lambda x: x[0]))
        plaintext = json.dumps([etype, data_full],cls=OrderedJsonEncoder)

        if data_full or unique:
            #We only have a type; no other distinguishing data. Generate a random hash
            if unique is None:
                eid = ids.send(plaintext)
            else:
                eid = ids.send([plaintext, unique])
        else:
            eid = next(ids)
        params['materialized_id'] = eid
        params['first_seen'] = eid in existing_ids
        for plugin in plugins:
            #Not using yield from
            if BF_MATRES_TASK in plugin:
                for p in plugin[BF_MATRES_TASK](loop, model, params): pass
            #logger.debug("Pending tasks: %s" % asyncio.Task.all_tasks(loop))
        return eid

    try:
        while True:
            input_model = yield
            leader = None
            #Add work item record, with actual hash resource IDs based on default or plugged-in algo
            #FIXME: No plug-in support yet
            workhash = record_hash_key(input_model)
            workid = materialize_entity(iri.absolutize('Work', BL), hash=workhash, existing_ids=existing_ids)
            is_folded = workid in existing_ids
            existing_ids.add(workid)
            dumb_title = list(marc_lookup(input_model, '245$a')) or ['NO 245$a TITLE']
            logger.debug('Uniform title from 245$a: {0}'.format(dumb_title[0]))
            logger.debug('Work hash result: {0} from \'{1}\''.format(workid, 'Work' + workhash))

            if entbase:
                workid = I(iri.absolutize(workid, entbase))
            else:
                workid = I(workid)

            folded = [workid] if is_folded else []

            model.add(workid, TYPE_REL, I(iri.absolutize('Work', BL)))

            #params = {'workid': workid, 'rec': rec, 'logger': logger, 'input_model': input_model, 'output_model': model, 'entbase': entbase, 'vocabbase': vocabase, 'ids': ids, 'existing_ids': existing_ids, 'folded': folded}
            params = {'workid': workid, 'input_model': input_model, 'logger': logger, 'input_model': input_model, 'output_model': model, 'entbase': entbase, 'vocabbase': BL, 'ids': ids, 'existing_ids': existing_ids, 'folded': folded}

            #Figure out instances
            params['materialize_entity'] = materialize_entity
            instanceids = instancegen(params)
            if instanceids:
                instanceid = instanceids[0]

            params['instanceids'] = instanceids
            params['transforms'] = [] # set()
            params['fields_used'] = []
            params['dropped_codes'] = {}
            #Defensive coding against missing leader or 008
            field008 = leader = None
            #Prepare cross-references (i.e. 880s)
            #XXX: Figure out a way to declare in TRANSFRORMS? We might have to deal with non-standard relationship designators: https://github.com/lcnetdev/marc2bibframe/issues/83
            xrefs = {}
            remove_links = []
            add_links = []
            for lid, marc_link in input_model:
                origin, taglink, val, attribs = marc_link
                if taglink == MARCXML_NS + '/leader' or taglink.startswith(MARCXML_NS + '/data/9'):
                    #900 fields are local and might not follow the general xref rules
                    params['leader'] = leader = val
                    continue
                tag = attribs['tag']
                for xref in attribs.get('6', []):
                    xreftag, xrefid = xref.split('-')
                    #Locate the matching taglink
                    links = input_model.match(None, MARCXML_NS + '/data/' + xreftag)
                    for link in links:
                        for dest in link[ATTRIBUTES].get('6', []):
                            if [tag, xrefid] == dest.split('/')[0].split('-'):
                                if tag == '880':
                                    #880s will be handled by merger via xref, so take out for main loop
                                    #XXX: This does, however, make input_model no longer a true representation of the input XML. Problem?
                                    remove_links.append(lid)

                                if xreftag == '880':
                                    #Rule for 880s: merge in & add language indicator
                                    langinfo = dest.split('/')[-1]
                                    #Not using langinfo, really, at present because it seems near useless. Eventually we can handle by embedding a lang indicator token into attr values for later postprocessing
                                    remove_links.append(lid)
                                    for k, v in link[ATTRIBUTES].items():
                                        if k[:3] not in ('tag', 'ind'):
                                            attribs.setdefault(k, []).extend(v)
                                    add_links.append((origin, taglink, val, attribs))

            for lid in remove_links:
                input_model.remove(lid)

            for linfo in add_links:
                input_model.add(*linfo)

            for lid, marc_link in input_model:
                origin, taglink, val, attribs = marc_link
                if taglink == MARCXML_NS + '/leader':
                    params['leader'] = leader = val
                    continue
                #Sort out attributes
                params['indicators'] = indicators = { k: v for k, v in attribs.items() if k.startswith('ind') }
                params['subfields'] = subfields = { k: v for k, v in attribs.items() if k[:3] not in ('tag', 'ind') }
                params['code'] = tag = attribs['tag']
                if taglink.startswith(MARCXML_NS + '/control'):
                    key = 'tag-' + tag
                    if tag == '008':
                        params['field008'] = field008 = val
                    params['transforms'].append((tag, key))
                    params['fields_used'].append((tag,))
                elif taglink.startswith(MARCXML_NS + '/data'):
                    indicator_list = ((attribs.get('ind1') or ' ')[0].replace(' ', '#'), (attribs.get('ind2') or ' ')[0].replace(' ', '#'))
                    key = 'tag-' + tag
                    #logger.debug('indicators: ', repr(indicators))
                    #indicator_list = (indicators['ind1'], indicators['ind2'])
                    params['fields_used'].append(tuple([tag] + list(subfields.keys())))

                    #This is where we check each incoming MARC link to see if it matches a transform into an output link (e.g. renaming 020 to 'isbn')
                    to_process = []
                    if indicator_list != ('#', '#'):
                        #One or other indicator is set, so let's check the transforms against those
                        lookup = '{0}-{1}{2}'.format(*((tag,) + indicator_list))
                    for k, v in subfields.items():
                        lookup = '{0}${1}'.format(tag, k)
                        for valitems in v:
                            if lookup in transforms:
                                to_process.append((transforms[lookup], valitems))
                            else:
                                if not tag in transforms: # don't report on subfields for which a code-transform exists
                                    params['dropped_codes'].setdefault(lookup,0)
                                    params['dropped_codes'][lookup] += 1

                    if tag in transforms:
                        to_process.append((transforms[tag], ''))
                    else:
                        if not subfields: # don't count as dropped if subfields were processed
                            params['dropped_codes'].setdefault(tag,0)
                            params['dropped_codes'][tag] += 1

                    #Apply all the handlers that were found
                    for funcinfo, val in to_process:
                        #Support multiple actions per lookup
                        funcs = funcinfo if isinstance(funcinfo, tuple) else (funcinfo,)

                        for func in funcs:
                            extras = { WORKID: workid, IID: instanceid }
                            #Build Versa processing context
                            #Should we include indicators?
                            #Should we be passing in taglik rather than tag?
                            ctx = bfcontext((origin, tag, val, subfields), input_model, model, extras=extras, base=vocabbase, idgen=materialize_entity, existing_ids=existing_ids)
                            func(ctx)

                    if not to_process:
                        #Nothing else has handled this data field; go to the fallback
                        fallback_rel_base = 'tag-' + tag
                        #How about indicators?
                        for k, v in subfields.items():
                            fallback_rel = fallback_rel_base + k
                            #params['transforms'].append((code, fallback_rel))
                            for valitem in v:
                                model.add(I(workid), I(iri.absolutize(fallback_rel, vocabbase)), valitem)


            extra_stmts = set() # prevent duplicate statements
            for origin, k, v in itertools.chain(
                        extra_transforms.process_leader(leader, workid, instanceid),
                        extra_transforms.process_008(field008, workid, instanceid)):
                v = v if isinstance(v, tuple) else (v,)
                for item in v:
                    o = origin or I(instanceid)
                    if (o,k,item) not in extra_stmts:
                        model.add(o, k, item)
                        extra_stmts.add((o, k, item))

            instance_postprocess(params)

            logger.debug('+')

            for plugin in plugins:
                #Each plug-in is a task
                #task = asyncio.Task(plugin[BF_MARCREC_TASK](loop, relsink, params), loop=loop)
                yield from plugin[BF_MARCREC_TASK](loop, model, params)
                logger.debug("Pending tasks: %s" % asyncio.Task.all_tasks(loop))
                #FIXME: This blocks and thus serializes the plugin operation, rather than the desired coop scheduling approach
                #For some reason seting to async task then immediately deferring to next task via yield from sleep leads to the "yield from wasn't used with future" error (Not much clue at: https://codereview.appspot.com/7396044/)
                #yield from asyncio.Task(asyncio.sleep(0.01), loop=loop)
                #yield from asyncio.async(asyncio.sleep(0.01))
                #yield from asyncio.sleep(0.01) #Basically yield to next task

            #Can we somehow move this to passed-in postprocessing?
            if out and not canonical and not first_record: out.write(',\n')
            if out:
                if not canonical:
                    first_record = False
                    last_chunk = None
                    #Using iterencode avoids building a big JSON string in memory, or having to resort to file pointer seeking
                    #Then again builds a big list in memory, so still working on opt here
                    for chunk in json.JSONEncoder().iterencode([ link for link in model ]):
                        if last_chunk is None:
                            last_chunk = chunk[1:]
                        else:
                            out.write(last_chunk)
                            last_chunk = chunk
                    if last_chunk: out.write(last_chunk[:-1])
            #FIXME: Postprocessing should probably be a task too
            if postprocess: postprocess()
            #limiting--running count of records processed versus the max number, if any
            limiting[0] += 1
            if limiting[1] is not None and limiting[0] >= limiting[1]:
                break
    except GeneratorExit:
        logger.debug('Completed processing {0} record{1}.'.format(limiting[0], '' if limiting[0] == 1 else 's'))
        if out and not canonical: out.write(']')

        #if not plugins: loop.stop()
        for plugin in plugins:
            #Each plug-in is a task
            func = plugin.get(BF_FINAL_TASK)
            if not func: continue
            task = asyncio.Task(func(loop), loop=loop)
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

