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
from bibframe.contrib.datachefids import idgen

#from amara.lib import U
from amara3 import iri
#from amara import namespaces
#from amara3.util import coroutine

from versa import I, VERSA_BASEIRI
from versa.util import simple_lookup

from bibframe import BFZ, BFLC, g_services
from bibframe import BF_INIT_TASK, BF_MARCREC_TASK, BF_FINAL_TASK
from bibframe.isbnplus import isbn_list
from bibframe.reader.marcpatterns import MATERIALIZE, MATERIALIZE_VIA_ANNOTATION, FIELD_RENAMINGS, INSTANCE_FIELDS, ANNOTATIONS_FIELDS
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


def instancegen(isbns):
    '''
    Default handling of the idea of splitting a MARC record with FRBR Work info as well as instances signalled by ISBNs
    '''
    base_instance_id = instance_item['id']
    instance_ids = []
    subscript = ord('a')
    for subix, (inum, itype) in enumerate(isbn_list(isbns)):
        subitem = instance_item.copy()
        subitem['isbn'] = inum
        subitem['id'] = base_instance_id + (unichr(subscript + subix) if subix else '')
        if itype: subitem['isbnType'] = itype
        instance_ids.append(subitem['id'])
        new_instances.append(subitem)


#FIXME: Stuff to be made thread local
T_prior_materializedids = set()

RESOURCE_TYPE = 'marcrType'

def marc_lookup(rec, fieldspecs):
    result = []
    lookup_helper = dict(( f.split('$') for f in fieldspecs ))
    #dict((target_code, target_sf = fieldspec.split('$')
    for row in rec:
        if row[0] == DATAFIELD:
            rowtype, code, xmlattrs, subfields = row
            if code in lookup_helper:
                result.append(subfields.get(lookup_helper[code], ''))
    return result


RECORD_HASH_KEY_FIELDS = [
    '130$a', '240$a', '240$b', '240$c', '240$h', '245$a', '246$a', '246$i', '830$a', #Title info
    '100$a', '100$d', '100$q', '110$a', '110$c', '110$d', '111$a', '110$c', '110$d', #Creator info
    '700$a', '700$d', '710$a', '710$b', '710$d', #Contributor info
    '600$a', '610$a', '611$a', '650$a', '650$x', '651$a', '615$a', '690$a' #Subject info
]


#FIXME: Rather than making so many passes over the record via marc_lookup, set up multi-lookup for single pass
def record_hash_key(rec):
    return ''.join(marc_lookup(rec, RECORD_HASH_KEY_FIELDS))


@asyncio.coroutine
def record_handler(loop, relsink, entbase=None, vocabbase=BFZ, limiting=None, plugins=None, ids=None, postprocess=None, out=None, logger=logging, **kwargs):
    '''
    loop - asyncio event loop
    entbase - base IRI used for IDs of generated entity resources
    limiting - mutable pair of [count, limit] used to control the number of records processed
    '''
    _final_tasks = set() #Tasks for the event loop contributing to the MARC processing
    
    plugins = plugins or []
    if ids is None: ids = idgen(entbase)
    #FIXME: Use thread local storage rather than function attributes

    #A few code modularization functions pulled into local context as closures
    def process_materialization(lookup, subfields, code=None):
        materializedid = ids.send(repr(tuple(subfields.items())))
        if entbase: materializedid = I(iri.absolutize(materializedid, entbase))
        #The extra_props are parameters inherent to a particular MARC field/subfield for purposes of linked data representation
        if code is None: code = lookup
        (subst, extra_props) = MATERIALIZE[lookup]
        if RESOURCE_TYPE in extra_props:
            relsink.add(I(materializedid), TYPE_REL, I(iri.absolutize(extra_props[RESOURCE_TYPE], vocabbase)))
        #logger.debug((lookup, subfields, extra_props))

        if materializedid not in T_prior_materializedids:
            #Just bundle in the subfields as they are, to avoid throwing out data. They can be otherwise used or just stripped later on
            #for k, v in itertools.chain((('marccode', code),), subfields.items(), extra_props.items()):
            for k, v in itertools.chain(subfields.items(), extra_props.items()):
                if k == RESOURCE_TYPE: continue
                fieldname = 'subfield-' + k
                if code + k in FIELD_RENAMINGS:
                    fieldname = FIELD_RENAMINGS[code + k]
                    if len(k) == 1: params['transforms'].append((code + k, fieldname)) #Only if proper MARC subfield
                    #params['transforms'].append((code + k, FIELD_RENAMINGS.get(sflookup, sflookup)))
                relsink.add(I(materializedid), iri.absolutize(fieldname, vocabbase), v)
            T_prior_materializedids.add(materializedid)

        return materializedid, subst

    #FIXME: test correct MARC transforms info for annotations
    def process_annotation(anntype, subfields, extra_annotation_props):
        #Separate annotation subfields from object subfields
        object_subfields = subfields.copy()
        annotation_subfields = {}
        for k, v in subfields.items():
            if code + k in ANNOTATIONS_FIELDS:
                annotation_subfields[k] = v
                del object_subfields[k]
            params['transforms'].append((code + k, code + k))

        #objectid = next(idg)
        #object_props.update(object_subfields)

        annotationid = ids.send(repr((code,) + tuple(subfields.items())))
        if entbase: annotationid = I(iri.absolutize(annotationid, entbase))
        relsink.add(I(annotationid), TYPE_REL, I(iri.absolutize(anntype, vocabbase)))
        for k, v in itertools.chain(annotation_subfields.items(), extra_annotation_props.items()):
            relsink.add(I(annotationid), I(iri.absolutize(k, vocabbase)), v)

        #Return enough info to generate the main origin/object relationship. The annotation is taken care of at this point
        return annotationid, object_subfields

    #Start the process of writing out the JSON representation of the resulting Versa
    out.write('[')
    first_record = True
    try:
        while True:
            rec = yield
            leader = None
            #Add work item record, with actual hash resource IDs based on default or plugged-in algo
            #FIXME: No plug-in support yet
            workhash = record_hash_key(rec)
            workid = ids.send('Work:' + workhash)
            logger.debug('Uniform title from 245$a: {0}'.format(marc_lookup(rec, ['245$a'])))
            logger.debug('Work hash result: {0} from \'{1}\''.format(workid, 'Work' + workhash))

            if entbase: workid = I(iri.absolutize(workid, entbase))
            relsink.add(I(workid), TYPE_REL, I(iri.absolutize('Work', vocabbase)))
            instanceid = ids.send('Instance:' + record_hash_key(rec))
            if entbase: instanceid = I(iri.absolutize(instanceid, entbase))
            #logger.debug((workid, instanceid))
            params = {'workid': workid}

            relsink.add(I(instanceid), TYPE_REL, I(iri.absolutize('Instance', vocabbase)))
            #relsink.add((instanceid, iri.absolutize('leader', PROPBASE), leader))
            #Instances are added below
            #relsink.add(I(workid), I(iri.absolutize('hasInstance', vocabbase)), I(instanceid))

            #for service in g_services: service.send(NEW_RECORD, relsink, workid, instanceid)

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
                    key = 'tag-' + code

                    handled = False
                    params['subfields'] = subfields
                    params['fields_used'].append(tuple([code] + list(subfields.keys())))

                    if subfields:
                        lookup = code
                        #See if any of the field codes represents a reference to an object which can be materialized

                        if code in MATERIALIZE:
                            materializedid, subst = process_materialization(code, subfields)
                            origin = instanceid if code in INSTANCE_FIELDS else workid
                            params['transforms'].append((code, subst))
                            relsink.add(I(origin), I(iri.absolutize(subst, vocabbase)), I(materializedid))
                            logger.debug('.')
                            handled = True

                        if code in MATERIALIZE_VIA_ANNOTATION:
                            #FIXME: code comments for extra_object_props & extra_annotation_props
                            (subst, anntype, extra_annotation_props) = MATERIALIZE_VIA_ANNOTATION[code]
                            annotationid, object_subfields = process_annotation(anntype, subfields, extra_annotation_props)

                            origin = instanceid if code in INSTANCE_FIELDS else workid
                            objectid = ids.send(repr((code,) + tuple(subfields.items())))
                            if entbase: objectid = I(iri.absolutize(objectid, entbase))

                            params['transforms'].append((code, subst))
                            relsink.add(I(origin), I(iri.absolutize(subst, vocabbase)), I(objectid), {I(iri.absolutize('annotation', vocabbase)): I(annotationid)})

                            for k, v in itertools.chain((('marccode', code),), object_subfields.items()):
                            #for k, v in itertools.chain(('marccode', code), object_subfields.items(), extra_object_props.items()):
                                relsink.add(I(objectid), I(iri.absolutize(k, vocabbase)), v)

                            logger.debug('.')
                            handled = True

                        #See if any of the field+subfield codes represents a reference to an object which can be materialized
                        if not handled:
                            for k, v in subfields.items():
                                lookup = code + k
                                if lookup in MATERIALIZE:
                                    #XXX At first glance you'd think you can always derive code from lookup (e.g. lookup[:3] but what if e.g. someone trims the left zero fill on the codes in the serialization?
                                    materializedid, subst = process_materialization(lookup, subfields, code=code)
                                    origin = instanceid if code in INSTANCE_FIELDS else workid
                                    params['transforms'].append((lookup, subst))
                                    relsink.add(I(origin), I(iri.absolutize(subst, vocabbase)), I(materializedid))

                                    #Is the MARC code part of the hash computation for the materiaalized object ID? Surely not!
                                    #materializedid = hashid((code,) + tuple(subfields.items()))
                                    logger.debug('.')
                                    handled = True

                                else:
                                    field_name = 'tag-' + lookup
                                    if lookup in FIELD_RENAMINGS:
                                        field_name = FIELD_RENAMINGS[lookup]
                                    #Handle the simple field_name substitution of a label name for a MARC code
                                    origin = instanceid if code in INSTANCE_FIELDS else workid
                                    #logger.debug(repr(I(iri.absolutize(field_name, vocabbase))))
                                    params['transforms'].append((lookup, field_name))
                                    relsink.add(I(origin), I(iri.absolutize(field_name, vocabbase)), v)

                    #if val:
                    #    origin = instanceid if code in INSTANCE_FIELDS else workid
                    #    relsink.add(I(origin), I(iri.absolutize(key, vocabbase)), val)

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


            #reduce lists of just one item
            #for k, v in work_item.items():
            #    if type(v) is list and len(v) == 1:
            #        work_item[k] = v[0]
            #work_sink.send(work_item)


            #Handle ISBNs re: https://foundry.zepheira.com/issues/1976
            ISBN_FIELD = 'tag-020'
            isbn_links = relsink.match(subj=instanceid, pred=iri.absolutize(ISBN_FIELD, vocabbase))
            isbns = [ s[2] for s in isbn_links ]
            logger.debug('ISBNS: {0}'.format(list(isbn_list(isbns))))
            other_instance_ids = []
            subscript = ord('a')
            newid = None
            for subix, (inum, itype) in enumerate(isbn_list(isbns)):
                newid = ids.send(instanceid + inum)
                if entbase: newid = I(iri.absolutize(newid, entbase))

                duplicate_statements(relsink, instanceid, newid)
                relsink.add(I(newid), I(iri.absolutize('isbn', vocabbase)), inum)
                #subitem['id'] = instanceid + (unichr(subscript + subix) if subix else '')
                if itype: relsink.add(I(newid), I(iri.absolutize('isbnType', vocabbase)), itype)
                other_instance_ids.append(newid)

            if not other_instance_ids:
                #Make sure it's created as an instance even if it has no ISBN
                relsink.add(I(workid), I(iri.absolutize('hasInstance', vocabbase)), I(instanceid))
                params.setdefault('instanceids', []).append(instanceid)

            for iid in other_instance_ids:
                relsink.add(I(workid), I(iri.absolutize('hasInstance', vocabbase)), I(iid))
                params.setdefault('instanceids', []).append(iid)

            #if newid is None: #No ISBN specified
            #    send_instance(ninst)

            #ix += 1
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

            if not first_record: out.write(',\n')
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
        out.write(']')

        if not plugins: loop.stop()
        for plugin in plugins:
            #Each plug-in is a task
            task = asyncio.Task(plugin[BF_FINAL_TASK](loop), loop=loop)
            _final_tasks.add(task)
            def task_done(task):
                #print('Task done: ', task)
                _final_tasks.remove(task)
                if len(_final_tasks) == 0:
                    #print("_final_tasks is empty, stopping loop.")
                    #loop = asyncio.get_event_loop()
                    loop.stop()
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

