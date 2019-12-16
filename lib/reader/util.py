#bibframe.reader.util
#FIXME: Rename to bibframe.reader.pipeline (cf Versa) post 1.0
'''
Library of functions that take a prototype link set and generate a transformed link set


'''

import re
import sys
from itertools import product
from enum import Enum #https://docs.python.org/3.4/library/enum.html
from collections import OrderedDict

from versa.pipeline import context as versacontext
from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES
from versa.pipeline import values, target, origin, rel, ifexists, toiri, res, url, if_, replace_from, lookup, SKIP, regex_match_modify

from bibframe.contrib.datachefids import slugify#, FROM_EMPTY_64BIT_HASH
from bibframe.contrib.datachefids import idgen as default_idgen
from bibframe import BFZ, BL
from bibframe.isbnplus import isbn_list, compute_ean13_check

from bibframe.reader import BOOTSTRAP_PHASE

from amara3 import iri

__all__ = ["bfcontext", "base_transformer", "link", "ignore", "anchor", "target", "rel", "origin",
            "all_subfields", "subfield", "values", "relator_property", "replace_from",
            "if_", "ifexists", "foreach", "indicator", "materialize", "url", "normalize_isbn",
            "onwork", "oninstance", "lookup", "regex_match_modify", "register_transforms",
            "subfields", "abort_on", "SKIP", "ifexists", "if_"]

RDA_PARENS_PAT = re.compile('\\(.*\\)')

PYBF_BASE = '"http://bibfra.me/tool/pybibframe/transforms#'
WORK_TYPE = BL + 'Work'
INSTANCE_TYPE = BL + 'Instance'
VTYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))

#ACTION_FUNCTION_PAT = re.compile('([\w-_]+)\s*\\(') #Intentionally crude. Not a big deal if we pull false positives


#FIXME: Make proper use of subclassing (implementation derivation)
class bfcontext(versacontext):
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


#class action(Enum):
#    replace = 1

DEFAULT_REL = object()

#SUBFIELDS_CACHE = {}

#Can't use functools.lru_cache because of the dict (unhashable) arg
#@lru_cache()
def subfields(attrs, code=None, ctx=None):
    '''
    Compute a given subfield from the full structure of attributes. Return a list of code/value pairs.

    attrs - A dictionary based on the input XML, including items in the form 'i.c': v where i is a numerical index
    to preserve the ordering from the original MARC, c is the subfield code and v is the value.

    code - optional string subfield code, or None to include all subfields in the result.

    ctx - optional context object to be used if the caller wants to track the total ordering information of the codes included in the result

    >>> subfields({'tag': '245', 'ind1': '1', 'ind2': '0', '2.a': 'Western America in 1846-1847. :', '3.b': 'The original travel diary of Lieutenant J. W. Abert, who mapped New Mexico for the United States Army; with illus. in color from his sketchbook /', '4.c': 'Edited by John Galvin.'}, code='a')
    [('a', 'Western America in 1846-1847. :')]
    >>> subfields({'tag': '100', 'ind1': '1', 'ind2': '', '2.a': 'Abert, J. W.', '3.q': '(James William),', '4.d': '1820-1897.'}, 'e')
    []
    >>> subfields({'tag': '100', 'ind1': '1', 'ind2': '', '2.a': 'Abert, J. W.', '3.q': '(James William),', '4.d': '1820-1897.'})
    [('a', 'Abert, J. W.'), ('q', '(James William),'), ('d', '1820-1897.')]
    >>> subfields({'tag': '040', 'ind1': '', 'ind2': '', '2.a': 'DLC', '3.c': 'DLC', '4.d': 'm.c.', '5.d':
'WaOLN', '6.d': 'UtOrBLW'})
    [('a', 'DLC'), ('c', 'DLC'), ('d', 'm.c.'), ('d', 'WaOLN'), ('d', 'UtOrBLW')]
    >>> subfields({'tag': '650', 'ind1': '', 'ind2': '0', '2.a': 'Tapestry', '3.z': 'Massachusetts', '4.z': 'Boston', '5.v': 'Catalogs.'}, 'z')
    [('z', 'Massachusetts'), ('z', 'Boston')]

    '''
    result = []
    # If the attributes have their own ordering, use it, otherwise sort
    attrs_in_order = sorted(attrs.items())
    for ix, (k, v) in enumerate(attrs_in_order):
        if '.' in k:
            this_code = k.rsplit('.')[-1]
            if code is None or this_code == code:
                result.append((this_code, v))
                if ctx and 'current-subfield-ix' in ctx.extras:
                    ctx.extras['current-subfield-ix'].append(ix)
    return result


class base_transformer(object):
    def __init__(self, origin_type=None):
        self._origin_type = origin_type
        return

    def __call__(self, origin_type, *args, **kwargs):
        self._origin_type = origin_type
        return

    def derive_origin(self, ctx):
        '''
        Given a pipeline transform context, derive an origin for generated Versa links
        from whether we're meant to deal with work or instance rules
        '''
        #Origins are indexed by resource type
        return ctx.extras['origins'][self._origin_type]
        #workid, iid = ctx.extras[WORK_TYPE], ctx.extras[INSTANCE_TYPE]
        #return {origin_class.work: workid, origin_class.instance: iid}[self._use_origin]

    def link(self, rel=None, value=None, res=False, ignore_refs=True):
        '''
        Create a link based the context's current link, specifying the output link
        IRI and a target value to be constructed for the link

        rel - IRI of the output link
        value - construction of the target value ofthe link. If None, equivalent of
                using target(), i.e. just reuse the target of the context current link
        res = if True mark the link target value as an IRI (i.e. not a plain string)
        '''
        #Delegate the work
        return link(derive_origin=self.derive_origin, rel=rel, value=value, res=res, ignore_refs=ignore_refs)

    def materialize(self, typ, rel=DEFAULT_REL, unique=None, links=None, postprocess=None):
        '''
        Create a new resource related to the origin
        '''
        links = links or {}
        #Delegate the work
        return materialize(typ, rel=rel, derive_origin=self.derive_origin, unique=unique,
                            links=links, postprocess=postprocess)


def link(derive_origin=None, rel=None, value=None, res=False, ignore_refs=True):
    '''
    Create a new link

    :param derive_origin: Versa action function to be invoked in order to
    determine the origin of the main generated link. If none the origin is derived
    from the context given when the materialize action function is called

    :param rel: IRI of the relationship to be created, from the origin,
    or a list of relationship IRIs, each of which will be used to create
    a separate link, or a versa action function to derive this relationship or
    list of relationships at run time, or None. If None, the relationship is derived
    from the context given when the materialize action function is called

    :param ignore_refs: if True, make no attempt to convert would-be IRI refs (i.e. relative links) to IRI type, even if asked (via ref)

    For examples of all these scenarios see marcpatterns.py

    :return: Versa action function to do the actual work
    '''
    def _link(ctx):
        (origin, _, t, a) = ctx.current_link
        if derive_origin:
            #Have enough info to derive the origin from context. Ignore origin in current link
            origin = derive_origin(ctx)

        #If need be call the Versa action function to determine the relationship to the materialized resource
        rels = rel(ctx) if callable(rel) else rel
        if not isinstance(rels, list): rels = [rels]

        values = value(ctx) if callable(value) else (t if value is None else value)
        if not isinstance(values, list): values = [values]

        def recurse_values(vs):
            if not isinstance(vs, list): vs = [vs]
            for v in vs:
                if callable(v):
                    yield from recurse_values(v(ctx))
                else:
                    yield v

        for _value in recurse_values(values):
            #If asked to convert value to resource, do so as long as it is absolute and ignore_refs is false
            if res and not (ignore_refs and not iri.is_absolute(_value)):
                try:
                    _value = I(_value)
                except ValueError:
                    ctx.extras['logger'].warn('Requirement to convert link target to IRI failed for invalid input, causing the corresponding output link to be omitted entirely: {0}'.format(repr((I(origin), I(iri.absolutize(rel, ctx.base)), _value))))
                    #XXX How do we really want to handle this error?
                    #return []
                    continue

            for r in rels:
                ctx.output_model.add(I(origin), I(iri.absolutize(r, ctx.base)), _value, {})

        return

    return _link


def ignore():
    '''
    Action function generator to do nothing, a no-op

    :return: None
    '''
    #Action function generator to do nothing
    def _ignore(ctx):
        #(o, r, t, a) = ctx.current_link
        ctx.extras['logger'].debug(' {0} ignored by rule'.format(ctx.extras['match-spec']))
        return
    return _ignore


from bibframe import *
WORK_TYPE = BL+'Work'

def anchor(rtype=WORK_TYPE):
    '''
    Action function generator to return a main resource ID from the current context, based on resource type

    :param rtype: resource type (IRI)

    :return: anchor resource ID from the current context

    Note:
        * rather than anchor_work() use anchor(BL + 'Work')
        * rather than anchor_instance() use anchor(BL + 'Instance')
    '''
    def _anchor(ctx):
        '''
        Versa action function to return the anchor work ID from the current context

        :param ctx: Versa context used in processing (e.g. includes the prototype link)

        :return: work ID from the current context
        '''
        return ctx.extras['origins'][rtype]
    return _anchor


NS_PATCH = lambda ns, k, v: (ns+k, v) if not iri.is_absolute(k) else (k, v)
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
    return (NS_PATCH(ctx.extras['inputns'], k, v) for k, v in subfields(ctx.current_link[ATTRIBUTES]))


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
        #return [ (tup[1][0] if isinstance(tup[1], list) else tup[1] ) for tup in subfields(ctx.current_link[ATTRIBUTES], key, ctx=ctx) ]
        return [ tup[1] for tup in subfields(ctx.current_link[ATTRIBUTES], key, ctx=ctx) ]
        #Why the blazes would this ever return [None] rather than None?!
        #return ctx.current_link[ATTRIBUTES].get(key, [None])
    return _subfield


def relator_property(text_in, allowed=None, default=None, prefix=None):
    '''
    Action function generator to take some text and compute a relationship slug therefrom

    :param text_in: Source text, or list thereof, for the relationship to be created, e.g. a MARC relator
    :return: Versa action function to do the actual work
    '''
    def _relator_property(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link)
        :return: List of relationships computed from the source text
        '''
        _text_in = text_in(ctx) if callable(text_in) else text_in
        _prefix = prefix or ''
        if not isinstance(_text_in, list): _text_in = [_text_in]
        #Take into account RDA-isms such as $iContainer of (expression) by stripping the parens https://foundry.zepheira.com/topics/380
        properties = [(_prefix + iri.percent_encode(slugify(RDA_PARENS_PAT.sub('', ti), False)))
                    if ti else '' for ti in _text_in]
        properties = [ prop if (allowed is None or prop in allowed) else default for prop in properties ]
        return properties
    return _relator_property


def foreach(origin=None, rel=None, target=None, attributes=None):
    '''
    Action function generator to compute a combination of links from a list of expressions

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
                    in product(o, r, t, a) if all((curr_o, curr_r, curr_t)) ]
        #for (curr_o, curr_r, curr_t, curr_a) in product(origin or [o], rel or [r], target or [t], attributes or [a]):
        #    newctx = ctx.copy(current_link=(curr_o, curr_r, curr_t, curr_a))
            #ctx.output_model.add(I(objid), VTYPE_REL, I(iri.absolutize(_typ, ctx.base)), {})
    return _foreach


def indicator(pat, mode='and'):
    '''
    Action function generator to determine if the current datafield's indicators match the given pattern

    :param pat: the 2-char pattern against which the indicators will be tested. '#' indicates no
    indicator value, while '?' indicates the position is ignored. Not tested for call-ability.
    :param mode: either 'and' or 'or', the former (and default) indicating that both indicators
    are tested to evaluate as True, while 'or' indicates that both are tested to evaluate as False.
    :return: Versa action function to do the actual work

    Pseudo doc test:
    #>>> ctx = {'extras':{'ind1':'3','ind2':'4'}}
    #>>> indicator('?4')
    #True
    #>>> indicator('3?')
    #True
    #>>> indicator('3#')
    #False
    #>>> indicator('##')
    #False
    #>>> indicator('??')
    #True
    #>>> indicator('?4', mode='or')
    #True
    #>>> indicator('#4', mode='or')
    #True
    #>>> indicator('3?', mode='or')
    #True
    #>>> indicator('3#', mode='or')
    #True
    #>>> indicator('##', mode='or')
    #False
    #>>> indicator('??', mode='or')
    #True
    '''
    def _indicator(ctx):
        inds = '{}{}'.format(ctx.extras['indicators'].get('ind1', '#') or '#',
                            ctx.extras['indicators'].get('ind2', '#') or '#')
        for i, p in zip(inds, pat):
            if mode=='and':
                if p == '?': continue
                if p != i: return False
            elif mode=='or':
                if p == '?': return True
                if p == i: return True
        return mode=='and'

    return _indicator


def materialize(typ, rel=DEFAULT_REL, derive_origin=None, unique=None, links=None, postprocess=None):
    '''
    Create a new resource related to the origin.

    :param typ: IRI of the type for the resource to be materialized,
    which becomes the target of the main link, and the origin of any
    additional links given in the links param

    :param rel: IRI of the relationship between the origin and the materialized
    target, or a list of relationship IRIs, each of which will be used to create
    a separate link, or a versa action function to derive this relationship or
    list of relationships at run time, or None. If None, the relationship is derived
    from the context given when the materialize action function is called

    :param derive_origin: Versa action function to be invoked in order to
    determine the origin of the main generated link. If none the origin is derived
    from the context given when the materialize action function is called

    :param unique: Versa action function to be invoked in order to
    derive a unique hash key input for the materialized resource, in the form of
    multiple key, value pairs (or key, list-of-values)

    :param links: Dictionary of links from the newly materialized resource.
    Each keys can be a relationship IRIs, a Versa action function returning
    a relationship IRI, a Versa action function returning a list of Versa
    contexts, which can be used to guide a sequence pattern of generated
    links, or a Versa action function returning None, which signals that
    the particular link is skipped entirely.

    :param postprocess: IRI or list of IRI queueing up actions to be postprocessed
    for this materialized resource. None, the default, signals no special postprocessing

    For examples of all these scenarios see marcpatterns.py

    :return: Versa action function to do the actual work
    '''
    links = links or {}
    def _materialize(ctx):
        '''
        Inserts at least two main links in the context's output_model, one or more for
        the relationship from the origin to the materialized resource, one for the
        type of the materialized resource, and links according to the links parameter

        :param ctx: Runtime Versa context used in processing (e.g. includes the prototype link)
        :return: None

        This function is intricate in its use and shifting of Versa context, but the
        intricacies are all designed to make the marcpatterns mini language more natural.
        '''
        #If need be call the Versa action function to determine the materialized resource's type
        _typ = typ(ctx) if callable(typ) else typ
        #If need be call the Versa action function to determine the relationship to the materialized resource
        _rel = rel(ctx) if callable(rel) else rel
        _unique = unique(ctx) if callable(unique) else unique
        _postprocess = postprocess if isinstance(postprocess, list) else ([postprocess] if postprocess else [])
        #The current link from the passed-in context might be used in several aspects of operation
        (origin, r, t, a) = ctx.current_link
        #Some conversions to make sure we end up with a list of relationships
        if _rel is DEFAULT_REL:
            _rel = [r]
        rels = _rel if isinstance(_rel, list) else ([_rel] if _rel else [])
        if derive_origin:
            #Have been given enough info to derive the origin from context. Ignore origin in current link
            origin = derive_origin(ctx)

        computed_unique = [] if _unique else None
        if _unique:
            # strip None values from computed unique list, including pairs where v is None
            for k, v in _unique:
                if None in (k, v): continue
                v = v if isinstance(v, list) else [v]
                for subitem in v:
                    subval = subitem(ctx) if callable(subitem) else subitem
                    if subval:
                        subval = subval if isinstance(subval, list) else [subval]
                        computed_unique.extend([(k,s) for s in subval])

        #XXX: Relying here on shared existing_ids from the idgen function. Probably need to think through this state coupling
        objid = ctx.idgen(_typ, data=computed_unique)
        #FIXME: Fix properly, by slugifying & making sure slugify handles all numeric case (prepend '_')
        rels = [ ('_' + curr_rel if curr_rel.isdigit() else curr_rel) for curr_rel in rels if curr_rel ]
        for curr_rel in rels:
            ctx.output_model.add(I(origin), I(iri.absolutize(curr_rel, ctx.base)), I(objid), {})
        folded = objid in ctx.existing_ids
        if not folded:
            for pp in _postprocess:
                ctx.extras['postprocessing'].append((pp, rels, I(objid)))
            if _typ: ctx.output_model.add(I(objid), VTYPE_REL, I(iri.absolutize(_typ, ctx.base)), {})
            #FIXME: Should we be using Python Nones to mark blanks, or should Versa define some sort of null resource?

            # Create a temporary model to capture attributes generated from this particular materialization, which will later be copied to the real output model in the order preserved from MARC
            tmp_omodel = ctx.output_model.copy(contents=False)

            #Start tracking current subfield
            #XXX It's probably circumstantially OK that this is a single, replaced  value and not a list. In theory, however, we could lose ordering info if an output relationship was derived from more than one subfield
            subfield_rids = {}

            for k, v in links.items():
                ctx.extras['current-subfield-ix'] = []
                #Make sure the context used has the right origin
                new_current_link = (I(objid), ctx.current_link[RELATIONSHIP], ctx.current_link[TARGET], ctx.current_link[ATTRIBUTES])
                newctx = ctx.copy(current_link=new_current_link, output_model=tmp_omodel)
                k = k(newctx) if callable(k) else k
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
                    new_current_link = (I(objid), k, newctx.current_link[TARGET], newctx.current_link[ATTRIBUTES])
                    newctx = newctx.copy(current_link=new_current_link, output_model=tmp_omodel)
                    #If k or v come from pipeline functions as None it signals to skip generating anything else for this link item
                    v = v(newctx) if callable(v) else v
                    if v is not None:
                        #FIXME: Fix properly, by slugifying & making sure slugify handles all-numeric case
                        if k.isdigit(): k = '_' + k
                        v = v if isinstance(v, list) else [v]
                        subfield_index_index = 0
                        for valitem in v:
                            if valitem:
                                # Associate the statement with the subfield
                                if subfield_index_index < len(ctx.extras['current-subfield-ix']):
                                    ix = ctx.extras['current-subfield-ix'][subfield_index_index]
                                else:
                                    ix = sys.maxsize
                                subfield_tracking = {'source-subfield-ix': ix}
                                tmp_omodel.add(I(objid), I(iri.absolutize(k, newctx.base)), valitem, subfield_tracking)
                                subfield_index_index += 1

            # If we care about MARC order, add the orderable statements from the
            # temporary model into the output model. tmp_omodel will not
            # necessarily be empty after this block runs so we add the remaining
            # statements into the output model too

            #rids_to_remove = []
            for lid, (tmp_o, tmp_r, tmp_t, tmp_a) in sorted(tmp_omodel, key=lambda l: l[1][ATTRIBUTES].get('source-subfield-ix', sys.maxsize)):
                #ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES
                if 'source-subfield-ix' in tmp_a: del tmp_a['source-subfield-ix']
                #print("{} moving statement number {} {} to output_model".format(ctx,rids[i], tmp_omodel[rids[i]]))
                ctx.output_model.add(tmp_o, tmp_r, tmp_t, tmp_a)
                #rids_to_remove.append(lid)

            #tmp_omodel.remove(rids_to_remove)

            #ctx.output_model.add_many(tmp_omodel)

            #To avoid losing info include subfields which come via Versa attributes
            for k, v in subfields(ctx.current_link[ATTRIBUTES]):
                ctx.output_model.add(I(objid), I(iri.absolutize('../marcext/sf-' + k, ctx.base)), v, {})
            ctx.existing_ids.add(objid)

    return _materialize


def normalize_isbn(isbn):
    '''
    Turn isbnplus into an action function to normalize ISBNs outside of 020, e.g. 776$z
    '''
    def _normalize_isbn(ctx):
        _isbn = isbn(ctx) if callable(isbn) else isbn
        _isbn = [_isbn] if not isinstance(_isbn, list) else _isbn
        return [ compute_ean13_check(i) for i, t in isbn_list([i for i in _isbn if i]) ]
    return _normalize_isbn


def abort_on(vals=None, regex=None):
    '''
    Send a signal to abort processing current record if condition met
    '''
    def _abort_on(ctx):
        #XXX Perhapos use actual signals for this?
        _vals = [vals] if not isinstance(vals, list) else vals
        (origin, _, t, a) = ctx.current_link
        if _vals and t in _vals:
            ctx.extras['abort-signal'] = True
    return _abort_on


on = base_transformer()
onwork = base_transformer(WORK_TYPE)
oninstance = base_transformer(INSTANCE_TYPE)


AVAILABLE_TRANSFORMS = {}

def register_transforms(iri, tdict, orderings=None):
    AVAILABLE_TRANSFORMS[iri] = (tdict, orderings) if orderings else tdict
