import time

class LoggedList(list):
    '''
    Used to capture the order in which subfields are added to the Versa input model
    '''
    def __init__(self, *args, **kwargs):
        super(LoggedList, self).__init__(*args, **kwargs)
        self.log = []
        if len(args) > 0:
            self.log.append((args[0][0], time.time())) # capture initialization value and time

    def append(self, item):
        super(LoggedList, self).append(item)
        self.log.append((item, time.time()))

def merge_list_logs(d):
    '''
    Given a dict, return the sorted, merged log of all values which
    contain a log (primarily LoggedList)

    >>> d = {}
    >>> d['b']=LoggedList(['goodbye'])
    >>> d['a']=LoggedList(['hello'])
    >>> d['c']=LoggedList(['bonjour'])
    >>> d['a'].append('au revoir')
    >>> list(merge_list_logs(d))
    [('b', 'goodbye', 0), ('a', 'hello', 0), ('c', 'bonjour', 0), ('a', 'au revoir', 1)]
    >>> d['b'].append('ciao')
    >>> list(merge_list_logs(d))
    [('b', 'goodbye', 0), ('a', 'hello', 0), ('c', 'bonjour', 0), ('a', 'au revoir', 1), ('b', 'ciao', 1)]
    '''

    full_log = []
    for k in d.keys():
        if hasattr(d[k], 'log') and hasattr(d[k].log, '__iter__'):
            full_log.extend((k, val, ind) for ind, val in enumerate(d[k].log))

    full_log.sort(key=lambda x: x[1][1]) # sort by time

    yield from ((k,v[0],i) for (k,v,i) in full_log)


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
    stage1 = memory.connection(attr_cls=OrderedDict)
    stage2 = memory.connection(attr_cls=OrderedDict)
    stage3 = memory.connection(attr_cls=OrderedDict)
    jsonload(stage1, stream)
    hashmap = {}
    #One pass for origins
    dummy = repr(stage1) #Mysterious bug (presumably in jsonload): attributes lose all their contents without this line
    for (rid, (o, r, t, a)) in stage1:
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

