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
from versa.util import duplicate_statements, OrderedJsonEncoder
from versa.driver import memory
#from versa.pipeline import context as versacontext

from bibframe import MARC, POSTPROCESS_AS_INSTANCE
from bibframe import BF_INIT_TASK, BF_INPUT_TASK, BF_INPUT_XREF_TASK, BF_MARCREC_TASK, BF_MATRES_TASK, BF_FINAL_TASK
from bibframe.util import materialize_entity
from bibframe.isbnplus import isbn_list, compute_ean13_check
from . import transform_set, BOOTSTRAP_PHASE, DEFAULT_MAIN_PHASE, PYBF_BOOTSTRAP_TARGET_REL, VTYPE_REL
from .util import WORK_TYPE, INSTANCE_TYPE, subfields
from .marcpatterns import TRANSFORMS, bfcontext
from .marcworkidpatterns import WORK_HASH_TRANSFORMS, WORK_HASH_INPUT
from .marcextra import transforms as default_special_transforms

#re https://www.loc.gov/marc/bibliographic/ecbdcntf.html
#$6 [linking tag]-[occurrence number]/[script identification code]/[field orientation code]
LINKAGE_PAT = re.compile('(\d\d\d)(-\d\d)?(/..)?(/r)?')


MARCXML_NS = "http://www.loc.gov/MARC21/slim"

NON_ISBN_CHARS = re.compile('\D')

NEW_RECORD = 'http://bibfra.me/purl/versa/' + 'newrecord'

# Namespaces

BL = 'http://bibfra.me/vocab/lite/'
ISBNNS = MARC

MARC_O6_SCRIPT_CODES = {
    '(3': 'arabic',
    '(B': 'latin',
    '$1': 'cjk',
    '(N': 'cyrillic',
    '(S': 'greek',
    '(2': 'hebrew'
}

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
            for k, v in subfields(link[ATTRIBUTES], sf):
                yield (code, v)

        #Check for control field
        links = model.match(None, MARCXML_NS + '/control/' + tag)
        for link in links:
            yield code, link[TARGET]


ISBN_REL = I(iri.absolutize('isbn', ISBNNS))
ISBN_VTYPE_REL = I(iri.absolutize('isbnType', ISBNNS))

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
    workid = params['default-origin']
    ids = params['ids']
    plugins = params['plugins']

    INSTANTIATES_REL = I(iri.absolutize('instantiates', vocabbase))

    isbns = list(( val for code, val in marc_lookup(input_model, '020$a')))
    logger.debug('Raw ISBNS:\t{0}'.format(isbns))

    # sorted to remove non-determinism which interferes with canonicalization
    normalized_isbns = sorted(list(isbn_list(isbns, logger=logger)))

    subscript = ord('a')
    instance_ids = []
    logger.debug('Normalized ISBN:\t{0}'.format(normalized_isbns))
    if normalized_isbns:
        for inum, itype in normalized_isbns:
            ean13 = compute_ean13_check(inum)
            data = [['instantiates', workid], [ISBNNS + 'isbn', ean13]]
            instanceid = materialize_entity('Instance', ctx_params=params, model_to_update=output_model, data=data, loop=loop)
            if entbase: instanceid = I(iri.absolutize(instanceid, entbase))

            output_model.add(I(instanceid), ISBN_REL, ean13)
            output_model.add(I(instanceid), INSTANTIATES_REL, I(workid))
            if itype: output_model.add(I(instanceid), ISBN_VTYPE_REL, itype)
            existing_ids.add(instanceid)
            instance_ids.append(instanceid)
    else:
        #If there are no ISBNs, we'll generate a default Instance
        data = [['instantiates', workid]]
        instanceid = materialize_entity('Instance', ctx_params=params, model_to_update=output_model, data=data, loop=loop)
        instanceid = I(iri.absolutize(instanceid, entbase)) if entbase else I(instanceid)
        output_model.add(I(instanceid), INSTANTIATES_REL, I(workid))
        existing_ids.add(instanceid)
        instance_ids.append(instanceid)

    #output_model.add(instance_ids[0], I(iri.absolutize('instantiates', vocabbase)), I(workid))
    #output_model.add(I(instance_ids[0]), VTYPE_REL, I(iri.absolutize('Instance', vocabbase)))

    return instance_ids


def instance_postprocess(params, skip_relationships=None):
    skip_relationships = list(skip_relationships) or []
    instanceids = params['instanceids']
    model = params['output_model']
    vocabbase = params['vocabbase']
    skip_relationships.extend([ISBN_REL, ISBN_VTYPE_REL, I(iri.absolutize('instantiates', vocabbase))])
    def dupe_filter(o, r, t, a):
        #Filter out ISBN relationships
        return (r, t) != (VTYPE_REL, I(iri.absolutize('Instance', vocabbase))) \
            and r not in skip_relationships
    if len(instanceids) > 1:
        base_instance_id = instanceids[0]
        for instanceid in instanceids[1:]:
            duplicate_statements(model, base_instance_id, instanceid, rfilter=dupe_filter)
    return


#FIXME: Generalize/merge with gather_targetid_data
def gather_workid_data(model, origin):
    '''
    Called after a first pass has been made to derive a BIBFRAME model sufficient to
    Compute a hash for the work, a task undertaken by this function
    '''
    data = []
    for rel in WORK_HASH_INPUT:
        for link in model.match(origin, rel):
            data.append([link[RELATIONSHIP], link[TARGET]])
    return data


def gather_targetid_data(model, origin, orderings=None):
    '''
    Gather the identifying info needed to create a hash for the main described resource,
    based on the minimal BIBFRAME model from the bootstrap phase
    '''
    data = []
    for rel in (orderings or []):
        for link in model.match(origin, rel):
            data.append([link[RELATIONSHIP], link[TARGET]])
    return data


#XXX Generalize by using URIs for phase IDs
def process_marcpatterns(params, transforms, input_model, phase_target):
    output_model = params['output_model']
    if phase_target == BOOTSTRAP_PHASE:
        input_model_iter = params['input_model']
    else:
        # Need to sort our way through the input model so that the materializations occur
        # at the same place each time, otherwise canonicalization fails due to the
        # addition of the subfield context (at the end of materialize())

        # XXX Is the int() cast necessary? If not we could do key=operator.itemgetter(0)
        input_model_iter = sorted(list(params['input_model']), key=lambda x: int(x[0]))
    params['to_postprocess'] = []
    for lid, marc_link in input_model_iter:
        origin, taglink, val, attribs = marc_link
        origin = params.get('default-origin', origin)
        #params['logger'].debug('PHASE {} ORIGIN: {}\n'.format(phase_target, origin))
        if taglink == MARCXML_NS + '/leader':
            params['leader'] = leader = val
            continue
        #Sort out attributes
        params['indicators'] = indicators = { k: v for k, v in attribs.items() if k.startswith('ind') }
        params['subfields'] = curr_subfields = subfields(attribs)
        curr_subfields_keys = [ tup[0] for tup in curr_subfields ]
        if taglink.startswith(MARCXML_NS + '/extra/') or 'tag' not in attribs: continue
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
                params['field008'] = val
            if phase_target != BOOTSTRAP_PHASE:
                params['transform_log'].append((tag, key))
                params['fields_used'].append((tag,))
        elif taglink.startswith(MARCXML_NS + '/data'):
            indicator_list = ((attribs.get('ind1') or ' ')[0].replace(' ', '#'), (attribs.get('ind2') or ' ')[0].replace(' ', '#'))
            key = 'tag-' + tag
            #logger.debug('indicators: ', repr(indicators))
            #indicator_list = (indicators['ind1'], indicators['ind2'])
            if phase_target != BOOTSTRAP_PHASE: params['fields_used'].append(tuple([tag] + curr_subfields_keys))

        #This is where we check each incoming MARC link to see if it matches a transform into an output link (e.g. renaming 001 to 'controlCode')
        to_process = []
        #Start with most specific matches, then to most general

        # "?" syntax in lookups is a single char wildcard
        #First with subfields, with & without indicators:
        for k, v in curr_subfields:
            #if indicator_list == ('#', '#'):
            lookups = [
                '{0}-{1}{2}${3}'.format(tag, indicator_list[0], indicator_list[1], k),
                '{0}-?{2}${3}'.format(tag, indicator_list[0], indicator_list[1], k),
                '{0}-{1}?${3}'.format(tag, indicator_list[0], indicator_list[1], k),
                '{0}${1}'.format(tag, k),
            ]
            for lookup in lookups:
                if lookup in transforms:
                    to_process.append((transforms[lookup], v, lookup))
                else:
                    # don't report on subfields for which a code-transform exists,
                    # disregard wildcards
                    if phase_target != BOOTSTRAP_PHASE and not tag in transforms and '?' not in lookup:

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
                to_process.append((transforms[lookup], val, lookup))

        if phase_target != BOOTSTRAP_PHASE and subfields_results_len == len(to_process) and not curr_subfields:
            # Count as dropped if subfields were not processed and theer were no matches on non-subfield lookups
            params['dropped_codes'].setdefault(tag,0)
            params['dropped_codes'][tag] += 1

        mat_ent = functools.partial(materialize_entity, ctx_params=params, loop=params['loop'])

        #Apply all the handlers that were found
        for funcinfo, val, lookup in to_process:
            #Support multiple actions per lookup
            funcs = funcinfo if isinstance(funcinfo, tuple) else (funcinfo,)

            for func in funcs:
                extras = {
                    'origins': params['origins'],
                    'match-spec': lookup,
                    'indicators': indicators,
                    'logger': params['logger'],
                    'lookups': params['lookups'],
                    'postprocessing': [],
                    'inputns': MARC,
                    'abort-signal': False,
                }
                #Build Versa processing context
                #Should we include indicators?
                #Should we be passing in taglink rather than tag?
                ctx = bfcontext((origin, tag, val, attribs), input_model,
                                    output_model, extras=extras,
                                    base=params['vocabbase'], idgen=mat_ent,
                                    existing_ids=params['existing_ids'])
                func(ctx)
                params['to_postprocess'].extend(ctx.extras['postprocessing'])
                if ctx.extras['abort-signal']:
                    return False

        if phase_target != BOOTSTRAP_PHASE and not to_process:
            #Nothing else has handled this data field; go to the fallback
            fallback_rel_base = '../marcext/tag-' + tag
            if not curr_subfields:
                #Fallback for control field: Captures MARC tag & value
                output_model.add(I(origin), I(iri.absolutize(fallback_rel_base, params['vocabbase'])), val)
            for k, v in curr_subfields:
                #Fallback for data field: Captures MARC tag, indicators, subfields & value
                fallback_rel = '../marcext/{0}-{1}{2}-{3}'.format(
                    fallback_rel_base, indicator_list[0].replace('#', 'X'),
                    indicator_list[1].replace('#', 'X'), k)
                #params['transform_log'].append((code, fallback_rel))
                try:
                    output_model.add(I(origin), I(iri.absolutize(fallback_rel, params['vocabbase'])), v)
                except ValueError as e:
                    control_code = list(marc_lookup(input_model, '001')) or ['NO 001 CONTROL CODE']
                    dumb_title = list(marc_lookup(input_model, '245$a')) or ['NO 245$a TITLE']
                    params['logger'].warning('{}\nSkipping statement for {}: "{}"'.format(e, control_code[0], dumb_title[0]))

    #For now do not run special transforms if in a custom phase
    #XXX: Needs discussion
    if phase_target in (BOOTSTRAP_PHASE, DEFAULT_MAIN_PHASE):
        #params['logger'].debug('PHASE {}\n'.format(phase_target))
        extra_stmts = set() # prevent duplicate statements
        special_transforms = params['transforms'].specials
        for origin, k, v in itertools.chain(
                    special_transforms.process_leader(params),
                    special_transforms.process_006(params['fields006'], params),
                    special_transforms.process_007(params['fields007'], params),
                    special_transforms.process_008(params['field008'], params)):
            v = v if isinstance(v, tuple) else (v,)
            for item in v:
                o = origin or I(params['default-origin'])
                if o and (o, k, item) not in extra_stmts:
                    output_model.add(o, k, item)
                    extra_stmts.add((o, k, item))
    return True

unused_flag = object()

@asyncio.coroutine
def record_handler( loop, model, entbase=None, vocabbase=BL, limiting=None,
                    plugins=None, ids=None, postprocess=None, out=None,
                    logger=logging, transforms=TRANSFORMS,
                    special_transforms=unused_flag,
                    canonical=False, model_factory=memory.connection,
                    lookups=None, **kwargs):
    '''
    loop - asyncio event loop
    model - the Versa model for the record
    entbase - base IRI used for IDs of generated entity resources
    limiting - mutable pair of [count, limit] used to control the number of records processed
    '''
    #Deprecated legacy API support
    if isinstance(transforms, dict) or special_transforms is not unused_flag:
        warnings.warn('Please switch to using bibframe.transforms_set', PendingDeprecationWarning)
        special_transforms = special_transforms or default_special_transforms()
        transforms = transform_set(transforms)
        transforms.specials = special_transforms

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
            params = {
                'input_model': input_model, 'logger': logger,
                #'input_model': input_model, 'output_model': model, 'logger': logger,
                'entbase': entbase, 'vocabbase': vocabbase, 'ids': ids,
                'existing_ids': existing_ids, 'plugins': plugins, 'transforms': transforms,
                'materialize_entity': materialize_entity, 'leader': leader, 'lookups': lookups or {},
                'loop': loop
            }

            # Earliest plugin stage, with an unadulterated input model
            for plugin in plugins:
                if BF_INPUT_TASK in plugin:
                    yield from plugin[BF_INPUT_TASK](loop, input_model, params)

            #Prepare cross-references (i.e. 880s)
            #See the "$6 - Linkage" section of https://www.loc.gov/marc/bibliographic/ecbdcntf.html
            #XXX: Figure out a way to declare in TRANSFORMS? We might have to deal with non-standard relationship designators: https://github.com/lcnetdev/marc2bibframe/issues/83
            xrefs = {}
            remove_links = set()
            add_links = []

            xref_link_tag_workaround = {}
            for lid, marc_link in input_model:
                origin, taglink, val, attribs = marc_link
                if taglink == MARCXML_NS + '/leader' or taglink.startswith(MARCXML_NS + '/data/9'):
                    #900 fields are local and might not follow the general xref rules
                    params['leader'] = leader = val
                    continue
                #XXX Do other fields with a 9 digit (not just 9XX) also need to be skipped?
                if taglink.startswith(MARCXML_NS + '/extra/') or 'tag' not in attribs: continue
                this_tag = attribs['tag']
                #if this_tag == '100': import pdb; pdb.set_trace()
                for xref in attribs.get('6', []):
                    matched = LINKAGE_PAT.match(xref)
                    this_taglink, this_occ, this_scriptid, this_rtl = matched.groups() if matched else (None, None, None, None)
                    if not this_taglink and occ:
                        control_code = list(marc_lookup(input_model, '001')) or ['NO 001 CONTROL CODE']
                        dumb_title = list(marc_lookup(input_model, '245$a')) or ['NO 245$a TITLE']
                        logger.warning('Skipping invalid $6: "{}" for {}: "{}"'.format(xref, control_code[0], dumb_title[0]))
                        continue

                    if this_tag == this_taglink:
                        #Pretty sure this is an erroneous self-link, but we've seen this in the wild (e.g. QNL). Issue warning & do the best we can linking via occurrence
                        #Note: the resulting workround (lookup table from occurence code to the correct tag) will not work in cases of linking from any tag higher in ordinal value than 880 (if such a situation is even possible)
                        logger.warning('Invalid input: erroneous self-link $6: "{}" from "{}". Trying to work around.'.format(xref, this_tag))
                        if this_tag != '880':
                            xref_link_tag_workaround[this_occ] = this_tag

                    #FIXME: Remove this debugging if statament at some point
                    if scriptid or rtl:
                        logger.debug('Language info specified in subfield 6, {}'.format(xref))

                    #Locate the matching taglink
                    if this_tag == '880' and this_occ == '00':
                        #Special case, no actual xref, used to separate scripts in a record (re Multiscript Records)
                        #FIXME: Not really handled right now. Presume some sort of merge dynamics will need to be implemented
                        attribs['tag'] = this_taglink
                        add_links.append((origin, MARCXML_NS + '/data/' + this_taglink, val, attribs))

                    if xref_link_tag_workaround:
                        if this_tag == '880':
                            this_taglink = xref_link_tag_workaround.get(this_occ)

                    links = input_model.match(None, MARCXML_NS + '/data/' + this_taglink)
                    for that_link in links:
                        #6 is the cross-reference subfield
                        for that_ref in link[ATTRIBUTES].get('6', []):
                            matched = LINKAGE_PAT.match(that_ref)
                            that_taglink, that_occ, that_scriptid, that_rtl = matched.groups() if matched else (None, None, None, None)
                            #if not that_tag and that_occ:
                            #    control_code = list(marc_lookup(input_model, '001')) or ['NO 001 CONTROL CODE']
                            #    dumb_title = list(marc_lookup(input_model, '245$a')) or ['NO 245$a TITLE']
                            #    logger.warning('Skipping invalid $6: "{}" for {}: "{}"'.format(to_ref, control_code[0], dumb_title[0]))
                            #    continue
                            if ([that_taglink, that_occ] == [this_tag, this_occ]) or (xref_link_tag_workaround and that_occ == this_occ):
                                if this_tag == '880':
                                    #This is an 880, which we'll handle by integrating back into the input model using the correct tag, flagged to show the relationship
                                    remove_links.add(lid)

                                if that_taglink == '880':
                                    #Rule for 880s: duplicate but link more robustly
                                    copied_attribs = attribs.copy()
                                    for k, v in that_link[ATTRIBUTES].items():
                                        if k[:3] not in ('tag', 'ind'):
                                            copied_attribs.setdefault(k, []).extend(v)
                                    add_links.append((origin, MARCXML_NS + '/data/' + this_tag, val, copied_attribs))

            input_model.remove(remove_links)
            input_model.add_many(add_links)

            # hook for plugins interested in the xref-resolved input model
            for plugin in plugins:
                if BF_INPUT_XREF_TASK in plugin:
                    yield from plugin[BF_INPUT_XREF_TASK](loop, input_model, params)

            #Do one pass to establish work hash
            #XXX Should crossrefs precede this?
            bootstrap_dummy_id = next(params['input_model'].match())[ORIGIN]
            logger.debug('Entering bootstrap phase. Dummy ID: {}'.format(bootstrap_dummy_id))

            params['default-origin'] = bootstrap_dummy_id
            params['instanceids'] = [bootstrap_dummy_id + '-instance']
            params['output_model'] = model_factory()

            params['field008'] = leader = None
            params['fields006'] = fields006 = []
            params['fields007'] = fields007 = []
            params['to_postprocess'] = []

            params['origins'] = {WORK_TYPE: bootstrap_dummy_id, INSTANCE_TYPE: params['instanceids'][0]}

            #First apply special patterns for determining the main target resources
            curr_transforms = transforms.compiled[BOOTSTRAP_PHASE]

            ok = process_marcpatterns(params, curr_transforms, input_model, BOOTSTRAP_PHASE)
            if not ok: continue #Abort current record if signalled

            bootstrap_output = params['output_model']
            temp_main_target = main_type = None
            for o, r, t, a in bootstrap_output.match(None, PYBF_BOOTSTRAP_TARGET_REL):
                #FIXME: We need a better designed way of determining fallback to bib
                if t is not None: temp_main_target, main_type = o, t

            #Switch to the main output model for processing
            params['output_model'] = model

            if temp_main_target is None:
                #If no target was set explicitly fall back to the transforms registered for the biblio phase
                #params['logger'].debug('WORK HASH ORIGIN {}\n'.format(bootstrap_dummy_id))
                #params['logger'].debug('WORK HASH MODEL {}\n'.format(repr(bootstrap_output)))
                workid_data = gather_workid_data(bootstrap_output, bootstrap_dummy_id)
                workid = materialize_entity('Work', ctx_params=params, data=workid_data, loop=loop)
                logger.debug('Entering default main phase, Work ID: {0}'.format(workid))

                is_folded = workid in existing_ids
                existing_ids.add(workid)

                control_code = list(marc_lookup(input_model, '001')) or ['NO 001 CONTROL CODE']
                dumb_title = list(marc_lookup(input_model, '245$a')) or ['NO 245$a TITLE']
                logger.debug('Work hash data: {0}'.format(repr(workid_data)))
                logger.debug('Control code: {0}'.format(control_code[0]))
                logger.debug('Uniform title: {0}'.format(dumb_title[0]))
                logger.debug('Work ID: {0}'.format(workid))

                workid = I(iri.absolutize(workid, entbase)) if entbase else I(workid)
                folded = [workid] if is_folded else []

                model.add(workid, VTYPE_REL, I(iri.absolutize('Work', vocabbase)))

                params['default-origin'] = workid
                params['folded'] = folded

                #Figure out instances
                instanceids = instancegen(params, loop, model)
                params['instanceids'] = instanceids or [None]

                main_transforms = transforms.compiled[DEFAULT_MAIN_PHASE]
                params['origins'] = {WORK_TYPE: workid, INSTANCE_TYPE: params['instanceids'][0]}
                phase_target = DEFAULT_MAIN_PHASE
            else:
                targetid_data = gather_targetid_data(bootstrap_output, temp_main_target, transforms.orderings[main_type])
                #params['logger'].debug('Data for resource: {}\n'.format([main_type] + targetid_data))
                targetid = materialize_entity(main_type, ctx_params=params, data=targetid_data, loop=loop)
                logger.debug('Entering specialized phase, Target resource ID: {}, type: {}'.format(targetid, main_type))

                is_folded = targetid in existing_ids
                existing_ids.add(targetid)
                #Determine next transform phase
                main_transforms = transforms.compiled[main_type]
                params['origins'] = {main_type: targetid}
                params['default-origin'] = targetid
                phase_target = main_type
                model.add(I(targetid), VTYPE_REL, I(main_type))

            params['transform_log'] = [] # set()
            params['fields_used'] = []
            params['dropped_codes'] = {}
            #Defensive coding against missing leader or 008
            params['field008'] = leader = None
            params['fields006'] = fields006 = []
            params['fields007'] = fields007 = []
            params['to_postprocess'] = []

            ok = process_marcpatterns(params, main_transforms, input_model, phase_target)
            if not ok: continue #Abort current record if signalled

            skipped_rels = set()
            for op, rels, rid in params['to_postprocess']:
                for rel in rels: skipped_rels.add(rel)
                if op == POSTPROCESS_AS_INSTANCE:
                    if params['instanceids'] == [None]:
                        params['instanceids'] = [rid]
                    else:
                        params['instanceids'].append(rid)
            instance_postprocess(params, skip_relationships=skipped_rels)

            logger.debug('+')

            #XXX At this point there must be at least one record with a Versa type

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
