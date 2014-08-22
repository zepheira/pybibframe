from enum import Enum #https://docs.python.org/3.4/library/enum.html

from versa.pipeline import *
from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES

def normalizeparse(text_in):
    return slugify(text_in, False)
    #return datachef.slugify(value)


class action(Enum):
    replace = 1


class origin_class(Enum):
    work = 1
    instance = 2


class base_transformer(object):
    def __init__(self, use_origin):
        self._use_origin = use_origin
        return

    def initialize(self, hashidgen, existing_ids):
        self._hashidgen = hashidgen
        self._existing_ids = existing_ids
        return

    #Functions that take a prototype link set and generate a transformed link set

    def rename(self, rel=None):
        '''
        Update the label of the relationship to be added to the link space
        '''
        def _rename(ctx, workid, iid):
            new_o = {origin_class.work: workid, origin_class.instance: iid}[self._use_origin]
            newlinkset = []
            #Just work with the first provided statement, for now
            (o, r, t, a) = ctx.linkset[0]
            newlinkset.append((I(new_o), I(iri.absolutize(rel, ctx.base)), t, {}))
            return newlinkset
        return _rename

    def materialize(self, typ, rel, unique=None, mr_properties=None):
        '''
        Create a new resource related to the origin
        '''
        mr_properties = mr_properties or {}
        def _materialize(ctx, workid, iid):
            new_o = {origin_class.work: workid, origin_class.instance: iid}[self._use_origin]
            newlinkset = []
            #Just work with the first provided statement, for now
            (o, r, t, a) = ctx.linkset[0]
            if unique is not None:
                objid = self._hashidgen.send([typ] + unique(ctx))
            else:
                objid = next(self._hashidgen)
            newlinkset.append((I(new_o), I(iri.absolutize(rel, ctx.base)), I(objid), {}))
            if objid not in self._existing_ids:
                if typ: newlinkset.append((I(objid), VTYPE_REL, I(iri.absolutize(typ, ctx.base)), {}))
                for k, v in mr_properties.items():
                    if callable(v):
                        v = v(ctx)
                    if v is not None:
                        newlinkset.append((I(objid), I(iri.absolutize(k, ctx.base)), v, {}))
                self._existing_ids.add(objid)
            return newlinkset
        return _materialize


def all_subfields(ctx):
    '''
    Utility to return a hash from all subfields mentioned in the MARC prototype link

    :param ctx: Versa context used in processing (e.g. includes the prototype link
    :return: Tuple of key/value tuples from the attributes; suitable for hashing
    '''
    return sorted(list(ctx.linkset[0][ATTRIBUTES].items()))


def subfield(key):
    '''
    Action function generator to look up a MARC subfield at processing time based on the given prototype linkset

    :param key: Key for looking up desired subfield value
    :return: Versa action function to do the actual work
    '''
    def _subfield(ctx):
        '''
        Versa action function Utility to return a hash from all subfields mentioned in the MARC prototype link

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        return ctx.linkset[0][ATTRIBUTES].get(key)
    return _subfield


fromwork = base_transformer(origin_class.work)
frominstance = base_transformer(origin_class.instance)

def initialize(hashidgen=None, existing_ids=None):
    fromwork.initialize(hashidgen, existing_ids)
    frominstance.initialize(hashidgen, existing_ids)

