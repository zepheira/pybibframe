'''
marc2bfrdf -v -o /tmp/ph1.ttl -s /tmp/ph1.stats.js -b http://example.org test/resource/princeton-holdings1.xml 2> /tmp/ph1.log

'''

import re
import os
import json
import functools
import logging
import itertools
import asyncio
from collections import defaultdict, OrderedDict

from bibframe.contrib.datachefids import idgen#, FROM_EMPTY_64BIT_HASH

from amara3 import iri

from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES
from versa.util import simple_lookup, OrderedJsonEncoder
from versa.driver import memory
from versa.pipeline import *

from bibframe import MARC
from bibframe.reader.util import WORKID, IID
from bibframe import BF_INIT_TASK, BF_INPUT_TASK, BF_MARCREC_TASK, BF_MATRES_TASK, BF_FINAL_TASK
from bibframe.isbnplus import isbn_list, compute_ean13_check
from bibframe.reader.marcpatterns import TRANSFORMS, bfcontext
from bibframe.reader.marcextra import transforms as default_extra_transforms


MARCXML_NS = "http://www.loc.gov/MARC21/slim"

NON_ISBN_CHARS = re.compile('\D')

NEW_RECORD = 'http://bibfra.me/purl/versa/' + 'newrecord'

# Namespaces

BL = 'http://bibfra.me/vocab/lite/'
ISBNNS = MARC

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


ISBN_REL = I(iri.absolutize('isbn', ISBNNS))
ISBN_TYPE_REL = I(iri.absolutize('isbnType', ISBNNS))

def isbn_instancegen(params, loop, model):
    '''
    Default handling of the idea of splitting a MARC record with FRBR Work info as well as instances signalled by ISBNs

    According to Vicki Instances can be signalled by 007, 020 or 3XX, but we stick to 020 for now
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
    ids = params['ids']
    plugins = params['plugins']

    isbns = list(( val for code, val in marc_lookup(input_model, '020$a')))
    logger.debug('Raw ISBNS:\t{0}'.format(isbns))

    # sorted to remove non-determinism which interferes with canonicalization
    normalized_isbns = sorted(list(isbn_list(isbns, logger=logger)))

    subscript = ord('a')
    instance_ids = []
    logger.debug('Normalized ISBN:\t{0}'.format(normalized_isbns))
    if normalized_isbns:
        for inum, itype in normalized_isbns:
            instanceid = materialize_entity('Instance', ctx_params=params, loop=loop, update_model=True, instantiates=workid, isbn=inum)
            if entbase: instanceid = I(iri.absolutize(instanceid, entbase))

            output_model.add(I(instanceid), ISBN_REL, compute_ean13_check(inum))
            output_model.add(I(instanceid), I(iri.absolutize('instantiates', vocabbase)), I(workid))
            if itype: output_model.add(I(instanceid), ISBN_TYPE_REL, itype)
            existing_ids.add(instanceid)
            instance_ids.append(instanceid)
    else:
        #If there are no ISBNs, we'll generate a default Instance
        instanceid = materialize_entity('Instance', ctx_params=params, loop=loop, update_model=True, instantiates=workid)
        if entbase: instanceid = I(iri.absolutize(instanceid, entbase))
        output_model.add(I(instanceid), I(iri.absolutize('instantiates', vocabbase)), I(workid))
        existing_ids.add(instanceid)
        instance_ids.append(instanceid)

    #output_model.add(instance_ids[0], I(iri.absolutize('instantiates', vocabbase)), I(workid))
    #output_model.add(I(instance_ids[0]), TYPE_REL, I(iri.absolutize('Instance', vocabbase)))

    return instance_ids


def instance_postprocess(params):
    instanceids = params['instanceids']
    model = params['output_model']
    vocabbase = params['vocabbase']
    def dupe_filter(o, r, t, a):
        #Filter out ISBN relationships
        return (r, t) != (TYPE_REL, I(iri.absolutize('Instance', vocabbase))) \
            and r not in (ISBN_REL, ISBN_TYPE_REL, I(iri.absolutize('instantiates', vocabbase)))
    if len(instanceids) > 1:
        base_instance_id = instanceids[0]
        for instanceid in instanceids[1:]:
            duplicate_statements(model, base_instance_id, instanceid, rfilter=dupe_filter)
    return

# special thanks to UCD, NLM, GW

RECORD_HASH_KEY_FIELDS = [
    '006', '008',  # work related fixed length field(s)
    '130$a', '130$f', '130$n', '130$o', '130$p', '130$l', '130$s',
    '240$a', '240$f', '240$n', '240$o', '240$p', '240$l', # key uniform title info
    '245$a', '245$b', '245$c', '245$n', '245$p', '245$f', '245$k', # Title info
    '246$a', '246$b', '246$f', # Title variation info
    '250$a', '250$b', # key edition
    '100$a', '100$d', '110$a', '110$d', '111$a', '111$d', # key creator info
    '700$a', '700$d', '710$a', '710$d', '711$a', '711$d', # key contributor info
    '600$a', '610$a', '611$a', '650$a', '651$a',  # key subject info
]

def record_hash_key(model):
    #Creating the hash with a delimeter between input fields just makes even slighter the collision risk
    return '|'.join(sorted(list( val for code, val in marc_lookup(model, RECORD_HASH_KEY_FIELDS))))


def materialize_entity(etype, ctx_params=None, unique=None, loop=None, update_model=False, **data):
    '''
    Routine for creating a BIBFRAME resource. Takes the entity (resource) type and a data mapping
    according to the resource type. Implements the Libhub Resource Hash Convention
    As a convenience, if a vocabulary base is provided, concatenate it to etype and the data keys
    '''
    ctx_params = ctx_params or {}
    vocabbase = ctx_params.get('vocabbase', BL)
    existing_ids = ctx_params.get('existing_ids')
    plugins = ctx_params.get('plugins')
    logger = ctx_params.get('logger', logging)
    output_model = ctx_params.get('output_model')
    ids = ctx_params.get('ids')
    if vocabbase:
        etype = vocabbase + etype
    params = {'logger': logger}
    data_full = { vocabbase + k: v for (k, v) in data.items() }
    # nobody likes non-deterministic ids! ordering matters to hash()
    data_full = OrderedDict(sorted(data_full.items(), key=lambda x: x[0]))
    plaintext = json.dumps([etype, data_full], cls=OrderedJsonEncoder)

    if data_full or unique:
        #We only have a type; no other distinguishing data. Generate a random hash
        if unique is None:
            eid = ids.send(plaintext)
        else:
            eid = ids.send([plaintext, unique])
    else:
        eid = next(ids)

    if update_model:
        output_model.add(I(eid), TYPE_REL, I(etype))

    params['materialized_id'] = eid
    params['first_seen'] = eid in existing_ids
    for plugin in plugins or ():
        #Not using yield from
        if BF_MATRES_TASK in plugin:
            for p in plugin[BF_MATRES_TASK](loop, output_model, params): pass
        #logger.debug("Pending tasks: %s" % asyncio.Task.all_tasks(loop))
    return eid


@asyncio.coroutine
def record_handler( loop, model, entbase=None, vocabbase=BL, limiting=None,
                    plugins=None, ids=None, postprocess=None, out=None,
                    logger=logging, transforms=TRANSFORMS,
                    extra_transforms=default_extra_transforms(),
                    canonical=False, **kwargs):
    '''
    loop - asyncio event loop
    model - the Versa model for the record
    entbase - base IRI used for IDs of generated entity resources
    limiting - mutable pair of [count, limit] used to control the number of records processed
    '''
    _final_tasks = set() #Tasks for the event loop contributing to the MARC processing

    plugins = plugins or []
    if ids is None: ids = idgen(entbase)

    #FIXME: For now always generate instances from ISBNs, but consider working this through the plugins system
    instancegen = isbn_instancegen

    existing_ids = set()
    #Start the process of writing out the JSON representation of the resulting Versa
    if out and not canonical: out.write('[')
    first_record = True

    try:
        while True:
            input_model = yield
            leader = None
            #Add work item record, with actual hash resource IDs based on default or plugged-in algo
            #FIXME: No plug-in support yet
            params = {'input_model': input_model, 'output_model': model, 'logger': logger, 'entbase': entbase, 'vocabbase': vocabbase, 'ids': ids, 'existing_ids': existing_ids, 'plugins': plugins}
            workhash = record_hash_key(input_model)
            workid = materialize_entity('Work', ctx_params=params, loop=loop, hash=workhash)
            is_folded = workid in existing_ids
            existing_ids.add(workid)
            control_code = list(marc_lookup(input_model, '001')) or ['NO 001 CONTROL CODE']
            dumb_title = list(marc_lookup(input_model, '245$a')) or ['NO 245$a TITLE']
            logger.debug('Control code: {0}'.format(control_code[0]))
            logger.debug('Uniform title: {0}'.format(dumb_title[0]))
            logger.debug('Work hash result: {0} from \'{1}\''.format(workid, 'Work' + workhash))

            if entbase:
                workid = I(iri.absolutize(workid, entbase))
            else:
                workid = I(workid)

            folded = [workid] if is_folded else []

            model.add(workid, TYPE_REL, I(iri.absolutize('Work', vocabbase)))

            params['workid'] = workid
            params['folded'] = folded

            #Figure out instances
            params['materialize_entity'] = materialize_entity
            instanceids = instancegen(params, loop, model)
            if instanceids:
                instanceid = instanceids[0]

            params['leader'] = None
            params['workid'] = workid
            params['instanceids'] = instanceids
            params['folded'] = folded
            params['transforms'] = [] # set()
            params['fields_used'] = []
            params['dropped_codes'] = {}
            #Defensive coding against missing leader or 008
            field008 = leader = None
            params['fields006'] = fields006 = []
            params['fields007'] = fields007 = []
            #Prepare cross-references (i.e. 880s)
            #XXX: Figure out a way to declare in TRANSFRORMS? We might have to deal with non-standard relationship designators: https://github.com/lcnetdev/marc2bibframe/issues/83
            xrefs = {}
            remove_links = set()
            add_links = []
            for lid, marc_link in input_model:
                origin, taglink, val, attribs = marc_link
                if taglink == MARCXML_NS + '/leader' or taglink.startswith(MARCXML_NS + '/data/9'):
                    #900 fields are local and might not follow the general xref rules
                    params['leader'] = leader = val
                    continue
                tag = attribs['tag']
                for xref in attribs.get('6', []):
                    xref_parts = xref.split('-')
                    if len(xref_parts) != 2:
                        logger.warning('Skipping invalid $6: "{}" for {}: "{}"'.format(xref, control_code[0], dumb_title[0]))
                        continue

                    xreftag, xrefid = xref_parts
                    #Locate the matching taglink
                    if tag == '880' and xrefid.startswith('00'):
                        #Special case, no actual xref, just the non-roman text
                        #Rule for 880s: merge in & add language indicator
                        langinfo = xrefid.split('/')[-1]
                        #Not using langinfo, really, at present because it seems near useless. Eventually we can handle by embedding a lang indicator token into attr values for later postprocessing
                        attribs['tag'] = xreftag
                        add_links.append((origin, MARCXML_NS + '/data/' + xreftag, val, attribs))

                    links = input_model.match(None, MARCXML_NS + '/data/' + xreftag)
                    for link in links:
                        #6 is the cross-reference subfield
                        for dest in link[ATTRIBUTES].get('6', []):
                            if [tag, xrefid] == dest.split('/')[0].split('-'):
                                if tag == '880':
                                    #880s will be handled by merger via xref, so take out for main loop
                                    #XXX: This does, however, make input_model no longer a true representation of the input XML. Problem?
                                    remove_links.add(lid)

                                if xreftag == '880':
                                    #Rule for 880s: merge in & add language indicator
                                    langinfo = dest.split('/')[-1]
                                    #Not using langinfo, really, at present because it seems near useless. Eventually we can handle by embedding a lang indicator token into attr values for later postprocessing
                                    remove_links.add(lid)
                                    copied_attribs = attribs.copy()
                                    for k, v in link[ATTRIBUTES].items():
                                        if k[:3] not in ('tag', 'ind'):
                                            copied_attribs.setdefault(k, []).extend(v)
                                    add_links.append((origin, taglink, val, copied_attribs))

            for lid in remove_links:
                input_model.remove(lid)

            for linfo in add_links:
                input_model.add(*linfo)

            # hook for plugins interested in the input model
            for plugin in plugins:
                if BF_INPUT_TASK in plugin:
                    yield from plugin[BF_INPUT_TASK](loop, input_model, params)

            # need to sort our way through the input model so that the materializations occur
            # at the same place each time, otherwise canonicalization fails due to the
            # addition of the subfield context (at the end of materialize())
            for lid, marc_link in sorted(list(input_model), key=lambda x: int(x[0])):
                origin, taglink, val, attribs = marc_link
                if taglink == MARCXML_NS + '/leader':
                    params['leader'] = leader = val
                    continue
                #Sort out attributes
                params['indicators'] = indicators = { k: v for k, v in attribs.items() if k.startswith('ind') }
                params['subfields'] = subfields = { k: v for k, v in attribs.items() if k[:3] not in ('tag', 'ind') }
                params['code'] = tag = attribs['tag']
                if taglink.startswith(MARCXML_NS + '/control'):
                    #No indicators on control fields. Turn them off, in effect
                    indicator_list = ('#', '#')
                    key = 'tag-' + tag
                    if tag == '006':
                        params['fields006'].append(val)
                    if tag == '007':
                        params['fields007'].append(val)
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

                #This is where we check each incoming MARC link to see if it matches a transform into an output link (e.g. renaming 001 to 'controlCode')
                to_process = []
                #Start with most specific matches, then to most general

                # "?" syntax in lookups is a single char wildcard
                #First with subfields, with & without indicators:
                for k, v in subfields.items():
                    #if indicator_list == ('#', '#'):
                    lookups = [
                        '{0}-{1}{2}${3}'.format(tag, indicator_list[0], indicator_list[1], k),
                        '{0}-?{2}${3}'.format(tag, indicator_list[0], indicator_list[1], k),
                        '{0}-{1}?${3}'.format(tag, indicator_list[0], indicator_list[1], k),
                        '{0}${1}'.format(tag, k),
                    ]
                    for valitems in v:
                        for lookup in lookups:
                            if lookup in transforms:
                                to_process.append((transforms[lookup], valitems))
                            else:
                                # don't report on subfields for which a code-transform exists,
                                # disregard wildcards
                                if not tag in transforms and '?' not in lookup:

                                    params['dropped_codes'].setdefault(lookup,0)
                                    params['dropped_codes'][lookup] += 1

                #Now just the tag, with & without indicators
                lookups = [
                    '{0}-{1}{2}'.format(tag, indicator_list[0], indicator_list[1]),
                    '{0}-?{2}'.format(tag, indicator_list[0], indicator_list[1]),
                    '{0}-{1}?'.format(tag, indicator_list[0], indicator_list[1]),
                    tag,
                ]

                #Remember how many lookups were successful based on subfields
                subfields_results_len = len(to_process)
                for lookup in lookups:
                    if lookup in transforms:
                        to_process.append((transforms[lookup], val))

                if subfields_results_len == len(to_process) and not subfields:
                    # Count as dropped if subfields were not processed and theer were no matches on non-subfield lookups
                    params['dropped_codes'].setdefault(tag,0)
                    params['dropped_codes'][tag] += 1

                mat_ent = functools.partial(materialize_entity, ctx_params=params, loop=loop)
                #Apply all the handlers that were found
                for funcinfo, val in to_process:
                    #Support multiple actions per lookup
                    funcs = funcinfo if isinstance(funcinfo, tuple) else (funcinfo,)

                    for func in funcs:
                        extras = { WORKID: workid, IID: instanceid }
                        #Build Versa processing context
                        #Should we include indicators?
                        #Should we be passing in taglik rather than tag?
                        ctx = bfcontext((origin, tag, val, subfields), input_model, model, extras=extras, base=vocabbase, idgen=mat_ent, existing_ids=existing_ids)
                        func(ctx)

                if not to_process:
                    #Nothing else has handled this data field; go to the fallback
                    fallback_rel_base = '../marcext/tag-' + tag
                    if not subfields:
                        #Fallback for control field: Captures MARC tag & value
                        model.add(I(workid), I(iri.absolutize(fallback_rel_base, vocabbase)), val)
                    for k, v in subfields.items():
                        #Fallback for data field: Captures MARC tag, indicators, subfields & value
                        fallback_rel = '../marcext/{0}-{1}{2}-{3}'.format(
                            fallback_rel_base, indicator_list[0].replace('#', 'X'),
                            indicator_list[1].replace('#', 'X'), k)
                        #params['transforms'].append((code, fallback_rel))
                        for valitem in v:
                            try:
                                model.add(I(workid), I(iri.absolutize(fallback_rel, vocabbase)), valitem)
                            except ValueError as e:
                                logger.warning('{}\nSkipping statement for {}: "{}"'.format(e, control_code[0], dumb_title[0]))

            extra_stmts = set() # prevent duplicate statements
            for origin, k, v in itertools.chain(
                        extra_transforms.process_leader(params),
                        extra_transforms.process_006(fields006, params),
                        extra_transforms.process_007(fields007, params),
                        extra_transforms.process_008(field008, params)):
                v = v if isinstance(v, tuple) else (v,)
                for item in v:
                    o = origin or I(workid)
                    if (o,k,item) not in extra_stmts:
                        model.add(o, k, item)
                        extra_stmts.add((o, k, item))

            instance_postprocess(params)

            logger.debug('+')

            for plugin in plugins:
                #Each plug-in is a task
                #task = asyncio.Task(plugin[BF_MARCREC_TASK](loop, relsink, params), loop=loop)
                if BF_MARCREC_TASK in plugin:
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


def duplicate_statements(model, oldorigin, neworigin, rfilter=None):
    '''
    Take links with a given origin, and create duplicate links with the same information but a new origin

    :param model: Versa model to be updated
    :param oldres: resource IRI to be duplicated
    :param newres: origin resource IRI for duplication
    :return: None
    '''
    for link in model.match(oldorigin):
        o, r, t, a = link
        if rfilter is None or rfilter(o, r, t, a):
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
