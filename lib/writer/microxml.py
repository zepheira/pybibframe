'''
'''

import re
import os
import logging
import itertools

from amara3 import iri

from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET
from versa.iriref import iriref

from bibframe import BFZ, BFLC

VTYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))
VLABEL_REL = I(iri.absolutize('label', VERSA_BASEIRI))

WORKCLASS = iri.absolutize('Work', BFZ)
INSTANCECLASS = iri.absolutize('Instance', BFZ)
INSTANCEREL = iri.absolutize('hasInstance', BFZ)

def process(source, xmlw, to_ignore=None, logger=logging):
    '''
    Take an in-memory BIBFRAME model and convert it into a MicroXML document
    '''
    #Hoover up everything with a type
    for stmt in source.match(None, VTYPE_REL, None):
        rid = stmt[ORIGIN]
        logger.debug(rid)
        rtype = stmt[RELATIONSHIP]
        if not (to_ignore and rid in to_ignore):
            attrs = {'id': rid, 'type': rtype}
            rgi = rtype.rsplit('/', 1)[-1]
            xmlw.start_element(rgi, attrs)
            rels = {}
            for o, r, t, a in source.match(rid):
                if r == VTYPE_REL: continue
                rels.setdefault(r, []).append((t, a))
            for r, vals in rels.items():
                for val, attrs in vals:
                    attrs = {'full': r}
                    vgi = r.rsplit('/', 1)[-1]
                    if type(val) is iriref:
                        attrs['href'] = val
                        xmlw.start_element(vgi, attrs)
                        xmlw.end_element(vgi)
                    else:
                        xmlw.start_element(vgi, attrs)
                        xmlw.text(str(val))
                        xmlw.end_element(vgi)
            xmlw.end_element(rgi)

    return
