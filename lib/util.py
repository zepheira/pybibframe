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
