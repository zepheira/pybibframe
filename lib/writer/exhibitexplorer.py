'''
'''

import re
import sys
import logging
import itertools

#from datachef.ids import simple_hashstring

from amara3 import iri

from versa import SUBJECT, RELATIONSHIP, VALUE, I, VERSA_BASEIRI
from bibframe import BFZ, BFLC, BL

WORKCLASS = iri.absolutize('Work', BL)
INSTANCECLASS = iri.absolutize('Instance', BL)

TYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))

def process(source, work_sink, instance_sink, objects_sink, annotations_sink, logger=logging):
    '''
    Take an in-memory BIBFRAME model and emit it in Exhibit-based explorer ready form

    '''
    subobjs = subobjects(objects_sink)
    anns = annotations(annotations_sink)
    @coroutine
    def receive_items():
        '''
        Receives each resource bundle and processes it by creating an item
        dict which is then forwarded to the sink
        '''
        ix = 1
        while True:
            workid = yield
            #Extract the statements about the work
            wstmts = source.match(workid)
            rawid = u'_' + str(ix)

            work_item = {
                u'id': u'work' + rawid,
                u'label': rawid,
                #u'label': u'{0}, {1}'.format(row['TPNAML'], row['TPNAMF']),
                u'type': u'WorkRecord',
            }

            #Instance starts with same as work, with leader added
            instance_item = {
                u'leader': leader,
            }
            instance_item.update(work_item)
            instance_item[u'id'] = u'instance' + rawid
            instance_item[u'type'] = u'InstanceRecord'
            work_item[u'instance'] = u'instance' + rawid

            for cf in rec.xml_select(u'ma:controlfield', prefixes=PREFIXES):
                key = u'cftag_' + U(cf.xml_select(u'@tag'))
                val = U(cf)
                if list(cf.xml_select(u'ma:subfield', prefixes=PREFIXES)):
                    for sf in cf.xml_select(u'ma:subfield', prefixes=PREFIXES):
                        code = U(sf.xml_select(u'@code'))
                        sfval = U(sf)
                        #For now assume all leader fields are instance level
                        instance_item[key + code] = sfval
                else:
                    #For now assume all leader fields are instance level
                    instance_item[key] = val

            for df in rec.xml_select(u'ma:datafield', prefixes=PREFIXES):
                code = U(df.xml_select(u'@tag'))
                key = u'dftag_' + code
                val = U(df)
                if list(df.xml_select(u'ma:subfield', prefixes=PREFIXES)):
                    subfields = dict(( (U(sf.xml_select(u'@code')), U(sf)) for sf in df.xml_select(u'ma:subfield', prefixes=PREFIXES) ))
                    lookup = code
                    #See if any of the field codes represents a reference to an object which can be materialized
                    handled = False
                    if code in MATERIALIZE:
                        (subst, extra_props) = MATERIALIZE[code]
                        props = {u'marccode': code}
                        props.update(extra_props)
                        #props.update(other_properties)
                        props.update(subfields)
                        #work_item[FIELD_RENAMINGS.get(code, code)] = subid
                        subid = subobjs.add(props)
                        if code in INSTANCE_FIELDS:
                            instance_item.setdefault(subst, []).append(subid)
                        elif code in WORK_FIELDS:
                            work_item.setdefault(subst, []).append(subid)

                        handled = True

                    if code in MATERIALIZE_VIA_ANNOTATION:
                        (subst, extra_object_props, extra_annotation_props) = MATERIALIZE_VIA_ANNOTATION[code]
                        object_props = {u'marccode': code}
                        object_props.update(extra_object_props)
                        #props.update(other_properties)

                        #Separate annotation subfields from object subfields
                        object_subfields = subfields.copy()
                        annotation_subfields = {}
                        for k, v in object_subfields.items():
                            if code+k in ANNOTATIONS_FIELDS:
                                annotation_subfields[k] = v
                                del object_subfields[k]

                        object_props.update(object_subfields)
                        objectid = subobjs.add(object_props)

                        ann_props = {subst: objectid, u'on_work': work_item[u'id'], u'on_instance': instance_item[u'id'],}
                        ann_props.update(extra_annotation_props)
                        ann_props.update(annotation_subfields)
                        annid = anns.add(ann_props)
                        #Note, even though we have the returned annotation ID we do not use it. No link back from work/instance to annotation

                        print >> sys.stderr, '.',

                        if code in INSTANCE_FIELDS:
                            instance_item.setdefault('annotation', []).append(annid)
                        elif code in WORK_FIELDS:
                            work_item.setdefault('annotation', []).append(annid)

                        #The actual subfields go to the annotations sink
                        #annotations_props = {u'annotates': instance_item[u'id']}
                        #annotations_props.update(props)
                        #subid = subobjs.add(annotations_props, annotations_sink)
                        #The reference is from the instance ID
                        #instance_item.setdefault(subst, []).append(subid)

                        handled = True


                        #work_item.setdefault(FIELD_RENAMINGS.get(code, code), []).append(subid)

                    #See if any of the field+subfield codes represents a reference to an object which can be materialized
                    if not handled:
                        for k, v in subfields.items():
                            lookup = code + k
                            if lookup in MATERIALIZE:
                                (subst, extra_props) = MATERIALIZE[lookup]
                                props = {u'marccode': code, k: v}
                                props.update(extra_props)
                                #print >> sys.stderr, lookup, k, props,
                                subid = subobjs.add(props)
                                if lookup in INSTANCE_FIELDS or code in INSTANCE_FIELDS:
                                    instance_item.setdefault(subst, []).append(subid)
                                elif lookup in WORK_FIELDS or code in WORK_FIELDS:
                                    work_item.setdefault(subst, []).append(subid)
                                handled = True

                            else:
                                field_name = u'dftag_' + lookup
                                if lookup in FIELD_RENAMINGS:
                                    field_name = FIELD_RENAMINGS[lookup]
                                #Handle the simple field_nameitution of a label name for a MARC code
                                if lookup in INSTANCE_FIELDS or code in INSTANCE_FIELDS:
                                    instance_item.setdefault(field_name, []).append(v)
                                elif lookup in WORK_FIELDS or code in WORK_FIELDS:
                                    work_item.setdefault(field_name, []).append(v)


                #print >> sys.stderr, lookup, key
                elif not handled:
                    if code in INSTANCE_FIELDS:
                        instance_item[key] = val
                    elif code in WORK_FIELDS:
                        work_item[key] = val
                else:
                    if code in INSTANCE_FIELDS:
                        instance_item[key] = val
                    elif code in WORK_FIELDS:
                        work_item[key] = val

            #link = work_item.get(u'cftag_008')


            #Handle ISBNs re: https://foundry.zepheira.com/issues/1976
            new_instances = []


            if not new_instances:
                #Make sure it's created as an instance even if it has no ISBN
                new_instances.append(instance_item)
                instance_ids.append(base_instance_id)

            work_item[u'instance'] = instance_ids

            special_properties = {}
            for k, v in process_leader(leader):
                special_properties.setdefault(k, set()).add(v)

            for k, v in process_008(instance_item[u'cftag_008']):
                special_properties.setdefault(k, set()).add(v)

            #We get some repeated values out of leader & 008 processing, and we want to
            #Remove dupes so we did so by working with sets then converting to lists
            for k, v in special_properties.items():
                special_properties[k] = list(v)

            instance_item.update(special_properties)

            #reduce lists of just one item
            for k, v in work_item.items():
                if type(v) is list and len(v) == 1:
                    work_item[k] = v[0]
            work_sink.send(work_item)

            def send_instance(instance):
                for k, v in instance.items():
                    if type(v) is list and len(v) == 1:
                        instance[k] = v[0]
                instance_sink.send(instance)

            for ninst in new_instances:
                send_instance(ninst)

            #stub_item = {
            #    u'id': rawid,
            #    u'label': rawid,
            #    u'type': u'MarcRecord',
            #}

            #stub_sink.send(stub_item)
            ix += 1
            print >> sys.stderr, '+',

        return

    target = receive_items()

    for stmt in source.match(None, TYPE_REL, WORKCLASS):
        workid = stmt[SUBJECT]
        target.send(workid)

    target.close()
    return
