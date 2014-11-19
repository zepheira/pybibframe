from enum import Enum #https://docs.python.org/3.4/library/enum.html

from versa.pipeline import *
from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES

from bibframe.contrib.datachefids import slugify, idgen, FROM_EMPTY_HASH
from bibframe import BFZ

PYBF_BASE = '"http://bibfra.me/tool/pybibframe/transforms#'
WORKID = PYBF_BASE + 'workid'
IID = PYBF_BASE + 'iid'

#FIXME: Make proper use of subclassing (implementation derivation)
class bfcontext(context):
    def __init__(self, current_link, input_model, output_model, base=None, extras=None, idgen=None, existing_ids=None, logger=None):
        self.current_link = current_link
        self.input_model = input_model
        self.output_model = output_model
        self.base = base
        self.extras = extras or {}
        self.idgen = idgen
        self.existing_ids = existing_ids
        self.logger = logger
        return

    def copy(self, current_link=None, input_model=None, output_model=None, base=None, extras=None, idgen=None, existing_ids=None, logger=None):
        current_link = current_link if current_link else self.current_link
        input_model = input_model if input_model else self.input_model
        output_model = output_model if output_model else self.output_model
        base = base if base else self.base
        extras = extras if extras else self.extras
        idgen = idgen if idgen else self.idgen
        existing_ids = existing_ids if existing_ids else self.existing_ids
        logger = logger if logger else self.logger
        return bfcontext(current_link, input_model, output_model, base=base, extras=extras, idgen=idgen, existing_ids=existing_ids, logger=logger)


class action(Enum):
    replace = 1


class origin_class(Enum):
    work = 1
    instance = 2


class base_transformer(object):
    def __init__(self, use_origin):
        self._use_origin = use_origin
        return

    #Functions that take a prototype link set and generate a transformed link set

    def rename(self, rel=None, res=False):
        '''
        Update the label of the relationship to be added to the link space
        '''
        def _rename(ctx):
            workid, iid = ctx.extras[WORKID], ctx.extras[IID]
            new_o = {origin_class.work: workid, origin_class.instance: iid}[self._use_origin]
            #Just work with the first provided statement, for now
            (o, r, t, a) = ctx.current_link
            if res:
                try:
                    t = I(t)
                except ValueError:
                    return []
            ctx.output_model.add(I(new_o), I(iri.absolutize(rel, ctx.base)), t, {})
            return
        return _rename

    def materialize(self, typ, rel, unique=None, mr_properties=None):
        '''
        Create a new resource related to the origin
        '''
        mr_properties = mr_properties or {}
        def derive_origin(ctx):
            '''
            Given a pipeline transform context, derive an origin for generated Versa links
            from whether we're meant to deal with work or instance rules
            '''
            workid, iid = ctx.extras[WORKID], ctx.extras[IID]
            return {origin_class.work: workid, origin_class.instance: iid}[self._use_origin]
        #Now delegate to the actual materialize funtion to do the work
        return materialize(typ, rel, derive_origin=derive_origin, unique=unique, mr_properties=mr_properties)


def all_subfields(ctx):
    '''
    Utility to return a hash from all subfields mentioned in the MARC prototype link

    :param ctx: Versa context used in processing (e.g. includes the prototype link
    :return: Tuple of key/value tuples from the attributes; suitable for hashing
    '''
    #result = [ valitem for keys, values in ctx.linkset[0][ATTRIBUTES].items() for valitem in values ]
    #print(result)
    #for valitem in ctx.linkset[0][ATTRIBUTES].items():
    #    result.extend(valitem)
        #sorted(functools.reduce(lambda a, b: a.extend(b), ))
    #ctx.logger('GRIPPO' + repr(sorted(functools.reduce(lambda a, b: a.extend(b), ctx.linkset[0][ATTRIBUTES].items()))))
    return sorted(ctx.current_link[ATTRIBUTES].items())


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
        return ctx.current_link[ATTRIBUTES].get(key, [None])
    return _subfield


def values(*rels):
    '''
    Action function generator to multiplex a relationship at processing time

    :param rels: List of relationships to establish
    :return: Versa action function to do the actual work
    '''
    def _values(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        computed_rels = [ rel(ctx) if callable(rel) else rel for rel in rels ]
        return computed_rels
    return _values


def normalizeparse(text_in):
    '''
    Action function generator to multiplex a relationship at processing time

    :param rels: List of relationships to establish
    :return: Versa action function to do the actual work
    '''
    def _normalizeparse(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        #If we get a list arg, take the first
        _text_in = text_in(ctx) if callable(text_in) else text_in
        if isinstance(_text_in, list): _text_in = _text_in[0]
        return slugify(_text_in, False) if _text_in else ''
    return _normalizeparse


def ifexists(test, value, alt=None):
    '''
    Action function generator to multiplex a relationship at processing time

    :param rels: List of relationships to establish
    :return: Versa action function to do the actual work
    '''
    def _ifexists(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        _test = test(ctx) if callable(test) else test
        _value = value(ctx) if callable(value) else value
        _alt = alt(ctx) if callable(alt) else alt
        return _value if _test else _alt
    return _ifexists


def materialize(typ, rel=None, derive_origin=None, unique=None, mr_properties=None):
    '''
    Create a new resource related to the origin
    '''
    mr_properties = mr_properties or {}
    def _materialize(ctx):
        _typ = typ(ctx) if callable(typ) else typ
        _rel = rel(ctx) if callable(rel) else rel
        #Conversions to make sure we end up with a list of relationships out of it all
        rels = _rel if isinstance(_rel, list) else ([_rel] if rel else [])
        (o, r, t, a) = ctx.current_link
        if derive_origin:
            #Have been given enough info to derive the origin from context. Ignore origin in current link
            o = derive_origin(ctx)
        computed_unique = unique(ctx) if unique else None
        objid = ctx.idgen(_typ, unique=unique(ctx), existing_ids=ctx.existing_ids)
        for curr_rel in rels:
            #FIXME: Fix this properly, by slugifying & making sure slugify handles all numeric case (prepend '_')
            r = '_' + r if curr_rel.isdigit() else r
            ctx.output_model.add(I(o), I(iri.absolutize(curr_rel, ctx.base)), I(objid), {})
        folded = objid in ctx.existing_ids
        if not folded:
            if _typ: ctx.output_model.add(I(objid), VTYPE_REL, I(iri.absolutize(_typ, ctx.base)), {})
            #FIXME: Should we be using Python Nones to mark blanks, or should Versa define some sort of null resource?
            for k, v in mr_properties.items():
                k = k(ctx) if callable(k) else k
                new_current_link = (I(objid), k, ctx.current_link[TARGET], ctx.current_link[ATTRIBUTES])
                newctx = ctx.copy(current_link=new_current_link)
                v = v(newctx) if callable(v) else v
                #Pipeline functions can return lists of replacement statements or lists of scalar values
                #Or of course a single scalar value or None
                if isinstance(v, list) and isinstance(v[0], tuple):
                    #It's a list of replacement statements
                    ctx.output_model.add_many(v)
                #If k or v come from pipeline functions as None it signals to skip generating anything for this subfield
                elif k and v is not None:
                    #FIXME: Fix this properly, by slugifying & making sure slugify handles all numeric case (prepend '_')
                    if k.isdigit(): k = '_' + k
                    if isinstance(v, list):
                        for valitems in v:
                            if valitems:
                                ctx.output_model.add(I(objid), I(iri.absolutize(k, newctx.base)), valitems, {})
                    else:
                        ctx.output_model.add(I(objid), I(iri.absolutize(k, newctx.base)), v, {})
            #To avoid losing info include subfields which come via Versa attributes
            for k, v in ctx.current_link[ATTRIBUTES].items():
                for valitems in v:
                    ctx.output_model.add(I(objid), I(iri.absolutize('sf-' + k, ctx.base)), valitems, {})
            ctx.existing_ids.add(objid)

    return _materialize


def res(arg):
    '''
    Convert the argument into an IRI ref
    '''
    def _res(ctx):
        _arg = arg(ctx) if callable(arg) else arg
        return I(arg)
    return _res


onwork = base_transformer(origin_class.work)
oninstance = base_transformer(origin_class.instance)

AVAILABLE_TRANSFORMS = {}

def register_transforms(iri, tdict):
    AVAILABLE_TRANSFORMS[iri] = tdict
