import re
from itertools import product
from enum import Enum #https://docs.python.org/3.4/library/enum.html

from versa.pipeline import *
from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES

from bibframe.contrib.datachefids import slugify, FROM_EMPTY_HASH
from bibframe.contrib.datachefids import idgen as default_idgen
from bibframe import BFZ

RDA_PARENS_PAT = re.compile('\\(.*\\)')

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
        self.idgen = idgen or default_idgen(base)
        self.existing_ids = existing_ids or set()
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

    def materialize(self, typ, rel, unique=None, links=None):
        '''
        Create a new resource related to the origin
        '''
        links = links or {}
        def derive_origin(ctx):
            '''
            Given a pipeline transform context, derive an origin for generated Versa links
            from whether we're meant to deal with work or instance rules
            '''
            workid, iid = ctx.extras[WORKID], ctx.extras[IID]
            return {origin_class.work: workid, origin_class.instance: iid}[self._use_origin]
        #Now delegate to the actual materialize funtion to do the work
        return materialize(typ, rel, derive_origin=derive_origin, unique=unique, links=links)


def target():
    '''
    Action function generator to return the target of the context's current link

    :return: target of the context's current link
    '''
    #Action function generator to multiplex a relationship at processing time
    def _target(ctx):
        '''
        Versa action function Utility to return the target of the context's current link

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Target of the context's current link
        '''
        return ctx.current_link[TARGET]
    return _target


def all_subfields(ctx):
    '''
    Utility to return a hash key from all subfields mentioned in the MARC prototype link

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
        Versa action function Utility to look up a MARC subfield at processing time based on the given prototype linkset

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        return ctx.current_link[ATTRIBUTES].get(key)
        #Why the blazes would this ever return [None] rather than None?!
        #return ctx.current_link[ATTRIBUTES].get(key, [None])
    return _subfield


def values(*rels):
    '''
    Action function generator to compute a set of relationships from criteria

    :param rels: List of relationships to compute
    :return: Versa action function to do the actual work
    '''
    #Action function generator to multiplex a relationship at processing time
    def _values(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        computed_rels = [ rel(ctx) if callable(rel) else rel for rel in rels ]
        return computed_rels
    return _values


def relator_property(text_in, prefix=None):
    '''
    Action function generator to take some text and compute a relationship slug therefrom

    :param text_in: Source text for the relationship to be created, e.g. a MARC relator
    :return: Versa action function to do the actual work
    '''
    def _relator_property(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link)
        :return: Relationship computed from the source text
        '''
        #If we get a list arg, take the first
        _text_in = text_in(ctx) if callable(text_in) else text_in
        if isinstance(_text_in, list) and _text_in: _text_in = _text_in[0]
        #Take into account RDA-isms such as $iContainer of (expression) by stripping the parens https://foundry.zepheira.com/topics/380
        return ((prefix or '') + slugify(RDA_PARENS_PAT.subn('', _text_in)[0], False)) if _text_in else ''
    return _relator_property


def ifexists(test, value, alt=None):
    '''
    Action function generator providing an if/then/else type primitive
    :param test: Expression to be tested to determine the branch path
    :param value: Expression providing the result if test is true
    :param alt: Expression providing the result if test is false
    :return: Versa action function to do the actual work
    '''
    def _ifexists(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link)
        :return: Value computed according to the test expression result
        '''
        _test = test(ctx) if callable(test) else test
        if _test:
            return value(ctx) if callable(value) else value
        else:
            return alt(ctx) if callable(alt) else alt
    return _ifexists


def foreach(origin=None, rel=None, target=None, attributes=None):
    '''
    Action function generator to compute a combination of links and fun the 

    :return: Versa action function to do the actual work
    '''
    def _foreach(ctx):
        '''
        Versa action function utility to compute a list of values from a list of expressions

        :param ctx: Versa context used in processing (e.g. includes the prototype link)
        '''
        _origin = origin(ctx) if callable(origin) else origin
        _rel = rel(ctx) if callable(rel) else rel
        _target = target(ctx) if callable(target) else target
        _attributes = attributes(ctx) if callable(attributes) else attributes
        (o, r, t, a) = ctx.current_link
        o = [o] if _origin is None else (_origin if isinstance(_origin, list) else [_origin])
        r = [r] if _rel is None else (_rel if isinstance(_rel, list) else [_rel])
        t = [t] if _target is None else (_target if isinstance(_target, list) else [_target])
        #a = [a] if _attributes is None else _attributes
        a = [a] if _attributes is None else (_attributes if isinstance(_attributes, list) else [_attributes])
        #print([(curr_o, curr_r, curr_t, curr_a) for (curr_o, curr_r, curr_t, curr_a)
        #            in product(o, r, t, a)])
        return [ ctx.copy(current_link=(curr_o, curr_r, curr_t, curr_a))
                    for (curr_o, curr_r, curr_t, curr_a)
                    in product(o, r, t, a) ]
        #for (curr_o, curr_r, curr_t, curr_a) in product(origin or [o], rel or [r], target or [t], attributes or [a]):
        #    newctx = ctx.copy(current_link=(curr_o, curr_r, curr_t, curr_a))
            #ctx.output_model.add(I(objid), VTYPE_REL, I(iri.absolutize(_typ, ctx.base)), {})
    return _foreach


def materialize(typ, rel=None, derive_origin=None, unique=None, links=None):
    '''
    Create a new resource related to the origin
    '''
    links = links or {}
    def _materialize(ctx):
        _typ = typ(ctx) if callable(typ) else typ
        _rel = rel(ctx) if callable(rel) else rel
        #Conversions to make sure we end up with a list of relationships out of it all
        (o, r, t, a) = ctx.current_link
        if _rel is None:
            _rel = [r]
        rels = _rel if isinstance(_rel, list) else ([_rel] if rel else [])
        if derive_origin:
            #Have been given enough info to derive the origin from context. Ignore origin in current link
            o = derive_origin(ctx)
        computed_unique = unique(ctx) if unique else None
        objid = ctx.idgen(_typ, unique=computed_unique, existing_ids=ctx.existing_ids)
        for curr_rel in rels:
            #FIXME: Fix this properly, by slugifying & making sure slugify handles all numeric case (prepend '_')
            curr_rel = '_' + curr_rel if curr_rel.isdigit() else curr_rel
            if curr_rel:
                ctx.output_model.add(I(o), I(iri.absolutize(curr_rel, ctx.base)), I(objid), {})
        folded = objid in ctx.existing_ids
        if not folded:
            if _typ: ctx.output_model.add(I(objid), VTYPE_REL, I(iri.absolutize(_typ, ctx.base)), {})
            #FIXME: Should we be using Python Nones to mark blanks, or should Versa define some sort of null resource?
            for k, v in links.items():
                k = k(ctx) if callable(k) else k
                #If k is a list of contexts use it to dynamically execute functions
                if isinstance(k, list):
                    if k and isinstance(k[0], bfcontext):
                        for newctx in k:
                            #Presumably the function in question will generate any needed links in the output model
                            v(newctx)
                        continue

                #import traceback; traceback.print_stack() #For looking up the call stack e.g. to debug nested materialize
                #Check that the links key is not None, which is a signal not to
                #generate the item. For example if the key is an ifexists and the
                #test expression result is False, it will come back as None,
                #and we don't want to run the v function
                if k:
                    new_current_link = (I(objid), k, ctx.current_link[TARGET], ctx.current_link[ATTRIBUTES])
                    newctx = ctx.copy(current_link=new_current_link)
                    v = v(newctx) if callable(v) else v

                    #If k or v come from pipeline functions as None it signals to skip generating anything else for this link item
                    if v is not None:
                        v = v(newctx) if callable(v) else v
                        #FIXME: Fix properly, by slugifying & making sure slugify handles all-numeric case
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

def compose(*funcs):
    '''
    Compose an ordered list of functions. Args of a,b,c,d evaluates as a(b(c(d(ctx))))
    '''
    def _compose(ctx):
        # last func gets context, rest get result of previous func
        _result = funcs[-1](ctx)
        for f in reversed(funcs[:-1]):
            _result = f(_result)

        return _result
    return _compose


onwork = base_transformer(origin_class.work)
oninstance = base_transformer(origin_class.instance)

AVAILABLE_TRANSFORMS = {}

def register_transforms(iri, tdict):
    AVAILABLE_TRANSFORMS[iri] = tdict
