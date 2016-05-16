# bibframe.reader

import warnings

from amara3 import iri
from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES

VTYPE_REL = I(iri.absolutize('type', VERSA_BASEIRI))

#Transforms
CORE_BFLITE_TRANSFORMS = 'http://bibfra.me/tool/pybibframe/transforms#bflite'
CORE_MARC_TRANSFORMS = 'http://bibfra.me/tool/pybibframe/transforms#marc'
DEFAULT_TRANSFORM_IRIS = [CORE_BFLITE_TRANSFORMS, CORE_MARC_TRANSFORMS]

#Processing phases
BOOTSTRAP_PHASE = 'http://bibfra.me/tool/pybibframe/phase#bootstrap'
DEFAULT_MAIN_PHASE = 'http://bibfra.me/tool/pybibframe/phase#default-main'

PHASE_NICKNAMES = {
    'bootstrap': BOOTSTRAP_PHASE,
    'default-main': DEFAULT_MAIN_PHASE,
}

#Special relationship identifying the target resource determined during bootstrap phase
PYBF_BOOTSTRAP_TARGET_REL = 'http://bibfra.me/tool/pybibframe/vocab#bootstrap-target'


class transform_set(object):
    def __init__(self, tspec=None, specials_vocab=None):
        self.orderings = None
        if not tspec:
            self.iris = {BOOTSTRAP_PHASE: WORK_HASH_TRANSFORMS_ID, DEFAULT_MAIN_PHASE: DEFAULT_TRANSFORM_IRIS}
            self.compiled = {BOOTSTRAP_PHASE: WORK_HASH_TRANSFORMS, DEFAULT_MAIN_PHASE: DEFAULT_TRANSFORMS}
        else:
            if isinstance(tspec, list):
                #As a shortcut these are transforms for the biblio phase
                transforms = {}
                for tiri in tspec:
                    try:
                        transforms.update(AVAILABLE_TRANSFORMS[tiri])
                    except KeyError:
                        raise Exception('Unknown transforms set {0}'.format(tiri))
                self.iris = {BOOTSTRAP_PHASE: WORK_HASH_TRANSFORMS_ID, DEFAULT_MAIN_PHASE: tspec}
                self.compiled = {BOOTSTRAP_PHASE: WORK_HASH_TRANSFORMS, DEFAULT_MAIN_PHASE: transforms}
            else:
                #Just need to replace transform IRI list with consolidated  transform dict
                compiled = {}
                self.iris = {}
                for phase, tiris in tspec.items():
                    if phase in PHASE_NICKNAMES: phase = PHASE_NICKNAMES[phase]
                    perphase_transforms = {}
                    for tiri in tiris:
                        try:
                            new_transforms = AVAILABLE_TRANSFORMS[tiri]
                            orderings_specified = isinstance(new_transforms, tuple)
                            if phase == BOOTSTRAP_PHASE and orderings_specified:
                                new_transforms, self.orderings = new_transforms
                            elif phase == BOOTSTRAP_PHASE and not orderings_specified:
                                warnings.warn('A bootstrap transform phase really needs ordering information to ensure reliable output resource hashes.', RuntimeWarning)
                            elif phase != BOOTSTRAP_PHASE and orderings_specified:
                                raise RuntimeError('Ordering information is only suported for the bootstrap transform phase.')
                            perphase_transforms.update(new_transforms)
                        except KeyError:
                            raise Exception('Unknown transforms set {0}'.format(tiri))
                    compiled[phase] = perphase_transforms
                    self.iris[phase] = tiris
                self.compiled = compiled
                if BOOTSTRAP_PHASE not in self.iris:
                    self.iris[BOOTSTRAP_PHASE] = WORK_HASH_TRANSFORMS_ID
                    self.compiled[BOOTSTRAP_PHASE] = WORK_HASH_TRANSFORMS
        #raise(Exception(repr(self.iris)))
        self.specials=special_transforms(specials_vocab)

def force_tuple(val):
    return val if isinstance(val, tuple) else (val,)

def merge_transform_lookups(lookups1, lookups2):
    lookups1 = lookups1 if isinstance(lookups1, dict) else AVAILABLE_TRANSFORMS[lookups1]
    lookups2 = lookups2 if isinstance(lookups2, dict) else AVAILABLE_TRANSFORMS[lookups2]
    handled = set()
    merged = {}
    for k, v in lookups1.items():
        if k in lookups2:
            merged[k] = force_tuple(v) + force_tuple(lookups2[k])
            handled.add(k)
    for k, v in lookups2.items():
        if k not in handled and k in lookups1:
            merged[k] = force_tuple(v) + force_tuple(lookups1[k])
    return merged


#XXX: Deferred because of circular imports. True fix is to move above to subordinate module, but shhh! ;)
from .engine import bfconvert
from .marcpatterns import TRANSFORMS as DEFAULT_TRANSFORMS
from .marcworkidpatterns import WORK_HASH_TRANSFORMS, WORK_HASH_TRANSFORMS_ID, WORK_HASH_INPUT
from .util import AVAILABLE_TRANSFORMS
from .marcextra import transforms as special_transforms
