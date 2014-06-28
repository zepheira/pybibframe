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

from datachef.ids import simple_hashstring

#from amara.lib import U
from amara3 import iri
#from amara import namespaces
from amara3.util import coroutine

from versa import I, VERSA_BASEIRI

from bibframe import BFZ, BFLC, g_services
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

LABEL_REL = I(iri.absolutize('label', BFZ))

def invert_dict(d):
    #http://code.activestate.com/recipes/252143-invert-a-dictionary-one-liner/#c3
    #See also: http://pypi.python.org/pypi/bidict
        #Though note: http://code.activestate.com/recipes/576968/#c2
    inv = {}
    for k, v in d.items():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv

#One of the records gives us:

#http://hdl.loc.gov/loc.mss/eadmss.ms009216

#Which links for METS download to:

#http://hdl.loc.gov/loc.mss/eadmss.ms009216.4

#Which redirects to:

#http://findingaids.loc.gov/mastermets/mss/2009/ms009216.xml

#PREFIXES = {'ma': 'http://www.loc.gov/MARC21/slim', 'me': 'http://www.loc.gov/METS/'}

TYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))


def idgen(idbase):
    '''
    Generate a IRI
    '''
    #Simple tumbler for now, possibly switch to random number, with some sort of sequence override for unit testing
    ix = 0
    while True:
        yield iri.absolutize(str(ix), idbase) if idbase else str(ix)
        ix += 1


def hashid(idbase, key):
    '''
    Generate an IRI as a hash of given information
    '''
    h = simple_hashstring(key)
    return iri.absolutize(h, idbase) if idbase else str(h)


#iri.absolutize('label', PROPBASE),
#{"@context": "http://copia.ogbuji.net#_metadata"}


def instancegen(isbns):
    '''
    Default handling of the idea of splitting a MARC record with FRBR Work info as well as instances signalled by ISBNs
    '''
    base_instance_id = instance_item['id']
    instance_ids = []
    subscript = ord('a')
    for subix, (inum, itype) in enumerate(isbn_list(isbns)):
        #print >> sys.stderr, subix, inum, itype
        subitem = instance_item.copy()
        subitem['isbn'] = inum
        subitem['id'] = base_instance_id + (unichr(subscript + subix) if subix else '')
        if itype: subitem['isbnType'] = itype
        instance_ids.append(subitem['id'])
        new_instances.append(subitem)


#FIXME: Stuff to be made thread local
T_prior_materializedids = set()

RESOURCE_TYPE = 'marcrType'

def handle_collection(recs, relsink, idbase, ids=None, logger=logging):
    '''

    '''
    if ids is None: ids = idgen(idbase)
    for rec in recs:
        process_record(rec, relsink, idbase, ids, logger)
    return


@coroutine
def record_handler(relsink, idbase, limiting=None, plugins=None, ids=None, postprocess=None, out=None, logger=logging, **kwargs):
    '''
    idbase - base IRI used for IDs of generated resources
    limiting - mutable pair of [count, limit] used to control the number of records processed
    '''
    plugins = plugins or []
    if ids is None: ids = idgen(idbase)
    #FIXME: Use thread local storage rather than function attributes

    #A few code modularization functions pulled into local context as closures
    def process_materialization(lookup, subfields, code=None):
        materializedid = hashid(idbase, tuple(subfields.items()))
        #The extra_props are parameters inherent to a particular MARC field/subfield for purposes of linked data representation
        if code is None: code = lookup
        (subst, extra_props) = MATERIALIZE[lookup]
        if RESOURCE_TYPE in extra_props:
            relsink.add(I(materializedid), TYPE_REL, I(iri.absolutize(extra_props[RESOURCE_TYPE], BFZ)))
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
                relsink.add(I(materializedid), iri.absolutize(fieldname, BFZ), v)
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

        annotationid = next(ids)
        relsink.add(I(annotationid), TYPE_REL, I(iri.absolutize(anntype, BFZ)))
        for k, v in itertools.chain(annotation_subfields.items(), extra_annotation_props.items()):
            relsink.add(I(annotationid), I(iri.absolutize(k, BFZ)), v)

        #Return enough info to generate the main subject/object relationship. The annotation is taken care of at this point
        return annotationid, object_subfields

    #Start the process of writing out the JSON representation of the resulting Versa
    out.write('[')
    first_record = True
    try:
        while True:
            rec = yield
            #for plugin in plugins:
            #    plugin.send(dict(rec=rec))
            leader = None
            #Add work item record
            workid = next(ids)
            relsink.add(I(workid), TYPE_REL, I(iri.absolutize('Work', BFZ)))
            instanceid = next(ids)
            #logger.debug((workid, instanceid))
            params = {'workid': workid, 'model': relsink}

            relsink.add(I(instanceid), TYPE_REL, I(iri.absolutize('Instance', BFZ)))
            #relsink.add((instanceid, iri.absolutize('leader', PROPBASE), leader))
            #Instances are added below
            #relsink.add(I(workid), I(iri.absolutize('hasInstance', BFZ)), I(instanceid))

            #for service in g_services: service.send(NEW_RECORD, relsink, workid, instanceid)

            params['transforms'] = [] # set()
            params['fields_used'] = []
            for row in rec:
                code = None

                if row[0] == LEADER:
                    params['leader'] = leader = row[1]
                elif row[0] == CONTROLFIELD:
                    code, val = row[1].strip(), row[2]
                    key = 'tag-' + code
                    if code == '008':
                        params['field008'] = field008 = val
                    params['transforms'].append((code, key))
                    relsink.add(I(instanceid), I(iri.absolutize(key, BFZ)), val)
                    params['fields_used'].append((code,))
                elif row[0] == DATAFIELD:
                    code, xmlattrs, subfields = row[1].strip(), row[2], row[3]
                    key = 'tag-' + code

                    handled = False
                    subfields = dict(( (sf[0].strip(), sf[1]) for sf in subfields ))
                    params['subfields'] = subfields
                    params['fields_used'].append(tuple([code] + list(subfields.keys())))

                    if subfields:
                        lookup = code
                        #See if any of the field codes represents a reference to an object which can be materialized

                        if code in MATERIALIZE:
                            materializedid, subst = process_materialization(code, subfields)
                            subject = instanceid if code in INSTANCE_FIELDS else workid
                            params['transforms'].append((code, subst))
                            relsink.add(I(subject), I(iri.absolutize(subst, BFZ)), I(materializedid))
                            logger.debug('.')
                            handled = True

                        if code in MATERIALIZE_VIA_ANNOTATION:
                            #FIXME: code comments for extra_object_props & extra_annotation_props
                            (subst, anntype, extra_annotation_props) = MATERIALIZE_VIA_ANNOTATION[code]
                            annotationid, object_subfields = process_annotation(anntype, subfields, extra_annotation_props)

                            subject = instanceid if code in INSTANCE_FIELDS else workid
                            objectid = next(ids)
                            params['transforms'].append((code, subst))
                            relsink.add(I(subject), I(iri.absolutize(subst, BFZ)), I(objectid), {I(iri.absolutize('annotation', BFZ)): I(annotationid)})

                            for k, v in itertools.chain((('marccode', code),), object_subfields.items()):
                            #for k, v in itertools.chain(('marccode', code), object_subfields.items(), extra_object_props.items()):
                                relsink.add(I(objectid), I(iri.absolutize(k, BFZ)), v)

                            logger.debug('.')
                            handled = True

                        #See if any of the field+subfield codes represents a reference to an object which can be materialized
                        if not handled:
                            for k, v in subfields.items():
                                lookup = code + k
                                if lookup in MATERIALIZE:
                                    #XXX At first glance you'd think you can always derive code from lookup (e.g. lookup[:3] but what if e.g. someone trims the left zero fill on the codes in the serialization?
                                    materializedid, subst = process_materialization(lookup, subfields, code=code)
                                    subject = instanceid if code in INSTANCE_FIELDS else workid
                                    params['transforms'].append((lookup, subst))
                                    relsink.add(I(subject), I(iri.absolutize(subst, BFZ)), I(materializedid))

                                    #Is the MARC code part of the hash computation for the materiaalized object ID? Surely not!
                                    #materializedid = hashid((code,) + tuple(subfields.items()))
                                    logger.debug('.')
                                    handled = True

                                else:
                                    field_name = 'tag-' + lookup
                                    if lookup in FIELD_RENAMINGS:
                                        field_name = FIELD_RENAMINGS[lookup]
                                    #Handle the simple field_name substitution of a label name for a MARC code
                                    subject = instanceid if code in INSTANCE_FIELDS else workid
                                    #logger.debug(repr(I(iri.absolutize(field_name, BFZ))))
                                    params['transforms'].append((lookup, field_name))
                                    relsink.add(I(subject), I(iri.absolutize(field_name, BFZ)), v)

                    #print >> sys.stderr, lookup, key
                    #if val:
                    #    subject = instanceid if code in INSTANCE_FIELDS else workid
                    #    relsink.add(I(subject), I(iri.absolutize(key, BFZ)), val)

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
                    relsink.add(I(instanceid), I(iri.absolutize(k, BFZ)), item)


            #reduce lists of just one item
            #for k, v in work_item.items():
            #    if type(v) is list and len(v) == 1:
            #        work_item[k] = v[0]
            #work_sink.send(work_item)


            #Handle ISBNs re: https://foundry.zepheira.com/issues/1976
            ISBN_FIELD = 'tag-020'
            isbn_stmts = relsink.match(subj=instanceid, pred=iri.absolutize(ISBN_FIELD, BFZ))
            isbns = [ s[2] for s in isbn_stmts ]
            logger.debug('ISBNS: {0}'.format(list(isbn_list(isbns))))
            other_instance_ids = []
            subscript = ord('a')
            newid = None
            for subix, (inum, itype) in enumerate(isbn_list(isbns)):
                #print >> sys.stderr, subix, inum, itype
                newid = next(ids)
                duplicate_statements(relsink, instanceid, newid)
                relsink.add(I(newid), I(iri.absolutize('isbn', BFZ)), inum)
                #subitem['id'] = instanceid + (unichr(subscript + subix) if subix else '')
                if itype: relsink.add(I(newid), I(iri.absolutize('isbnType', BFZ)), itype)
                other_instance_ids.append(newid)

            if not other_instance_ids:
                #Make sure it's created as an instance even if it has no ISBN
                relsink.add(I(workid), I(iri.absolutize('hasInstance', BFZ)), I(instanceid))
                params.setdefault('instanceids', []).append(instanceid)

            for iid in other_instance_ids:
                relsink.add(I(workid), I(iri.absolutize('hasInstance', BFZ)), I(iid))
                params.setdefault('instanceids', []).append(iid)

            #if newid is None: #No ISBN specified
            #    send_instance(ninst)

            #ix += 1
            logger.debug('+')

            for plugin in plugins:
                plugin.send(params)

            #Can't really use this because it include outer []
            #jsondump(relsink, out)

            if not first_record: out.write(',\n')
            first_record = False
            last_chunk = None
            #Using iterencode avoids building a big JSON string in memory, or having to resort to file pointer seeking
            #Then again builds a big list in memory, so still working on opt here
            for chunk in json.JSONEncoder().iterencode([ stmt for stmt in relsink ]):
                if last_chunk is None:
                    last_chunk = chunk[1:]
                else:
                    out.write(last_chunk)
                    last_chunk = chunk
            if last_chunk: out.write(last_chunk[:-1])
            if postprocess: postprocess(rec)
            if limiting[1] is not None:
                limiting[0] += 1
                if limiting[0] >= limiting[1]:
                    break
        logger.debug('Completed processing {0} record{1}.'.format(limiting[0], '' if limiting[0] == 1 else 's'))
    except GeneratorExit:
        out.write(']')
    return


def duplicate_statements(model, oldsubject, newsubject):
    for stmt in model.match(oldsubject):
        s, p, o, a = stmt
        model.add(I(newsubject), p, o, a)
    return

