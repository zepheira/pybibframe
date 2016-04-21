# bibframe.reader

#Transforms
CORE_BFLITE_TRANSFORMS = 'http://bibfra.me/tool/pybibframe/transforms#bflite'
CORE_MARC_TRANSFORMS = 'http://bibfra.me/tool/pybibframe/transforms#marc'
DEFAULT_TRANSFORM_IRIS = [CORE_BFLITE_TRANSFORMS, CORE_MARC_TRANSFORMS]

#Processing phases
BOOTSTRAP_PHASE = 'http://bibfra.me/tool/pybibframe/phase#bootstrap'
BIBLIO_PHASE = 'http://bibfra.me/tool/pybibframe/phase#biblio'

PHASE_NICKNAMES = {
    'bootstrap': BOOTSTRAP_PHASE,
    'biblio': BIBLIO_PHASE,
}

#Special relationship identifying the target resource determined during bootstrap phase
PYBF_BOOTSTRAP_TARGET_REL = 'http://bibfra.me/tool/pybibframe/vocab#bootstrap-target'


class transform_set(object):
    def __init__(self, tspec=None, specials_vocab=None):
        if not tspec:
            self.iris = {BOOTSTRAP_PHASE: WORK_HASH_TRANSFORMS_ID, BIBLIO_PHASE: DEFAULT_TRANSFORM_IRIS}
            self.compiled = {BOOTSTRAP_PHASE: WORK_HASH_TRANSFORMS, BIBLIO_PHASE: DEFAULT_TRANSFORMS}
        else:
            if isinstance(tspec, list):
                #As a shortcut these are transforms for the biblio phase
                transforms = {}
                for tiri in tspec:
                    try:
                        transforms.update(AVAILABLE_TRANSFORMS[tiri])
                    except KeyError:
                        raise Exception('Unknown transforms set {0}'.format(tiri))
                self.iris = {BOOTSTRAP_PHASE: WORK_HASH_TRANSFORMS_ID, BIBLIO_PHASE: tspec}
                self.compiled = {BOOTSTRAP_PHASE: WORK_HASH_TRANSFORMS, BIBLIO_PHASE: transforms}
            else:
                #Just need to replace transform IRI list with consolidated  transform dict
                compiled = {}
                for phase, tiris in tspec.items():
                    perphase_transforms = {}
                    for tiri in tiris:
                        try:
                            perphase_transforms.update(AVAILABLE_TRANSFORMS[tiri])
                        except KeyError:
                            raise Exception('Unknown transforms set {0}'.format(tiri))
                    compiled[phase] = perphase_transforms
                self.iris = tspec
                self.compiled = compiled
                if BOOTSTRAP_PHASE not in self.iris:
                    self.iris[BOOTSTRAP_PHASE] = WORK_HASH_TRANSFORMS_ID
                    self.compiled[BOOTSTRAP_PHASE] = WORK_HASH_TRANSFORMS
        self.specials=special_transforms(specials_vocab)

from .engine import bfconvert
from .marcpatterns import TRANSFORMS as DEFAULT_TRANSFORMS
from .marcworkidpatterns import WORK_HASH_TRANSFORMS, WORK_HASH_TRANSFORMS_ID, WORK_HASH_INPUT
from .util import AVAILABLE_TRANSFORMS
from .marcextra import transforms as special_transforms
