'''
Treatment of certain special MARC fields, leader, 006, 007, 008, etc.
'''

from versa import I, VERSA_BASEIRI
from bibframe import BL, BA, REL, MARC, RBMS, AV

BL = 'http://bibfra.me/vocab/lite/'

#TODO: Also split on multiple 260 fields

VTYPE = VERSA_BASEIRI+'type'
LANG= BL+'language'
DEFAULT_VOCAB_ITEMS = [BL, BA, REL, MARC, RBMS, AV, LANG, VTYPE]

SLUG = lambda s: s.rsplit('/')[-1].replace('-',' ') if s else None

def runtime(rt):
    '''
    Handle visual material running time property
    '''
    runtime = None # no runtime property produced
    if isinstance(rt, str):
        if rt == 'nnn':
            runtime = I(self._vocab[MARC]+"running-time-not-applicable")
        elif rt == '---':
            runtime = I(self._vocab[MARC]+"unknown-running-time")
    else:
        try:
            runtime = int(rt)
        except ValueError:
            pass #None

    return runtime

class transforms(object):
    def __init__(self, vocab=None):
        DEFAULT_VOCAB = { i:i for i in DEFAULT_VOCAB_ITEMS }
        vocab = vocab or {}
        #Use any provided, overridden vocab items, or just the defaults
        self._vocab = { i: vocab.get(i, i) for i in DEFAULT_VOCAB_ITEMS }

        # some shared mappings between and within 006/008 fields
        self.AUDIENCE = {
            'a': I(self._vocab[MARC]+"preschool"),
            'b': I(self._vocab[MARC]+"primary"),
            'c': I(self._vocab[MARC]+"pre-adolescent"),
            'd': I(self._vocab[MARC]+"adolescent"),
            'e': I(self._vocab[MARC]+"adult"),
            'f': I(self._vocab[MARC]+"specialized"),
            'g': I(self._vocab[MARC]+"general"),
            'j': I(self._vocab[MARC]+"juvenile")
            }

        self.FORM_OF_ITEM = {
            'a': I(self._vocab[MARC]+'microfilm'),
            'b': I(self._vocab[MARC]+'microfiche'),
            'c': I(self._vocab[MARC]+'microopaque'),
            'd': I(self._vocab[MARC]+'large-print'),
            'f': I(self._vocab[MARC]+'braille'),
            'o': I(self._vocab[MARC]+'online'),
            'q': I(self._vocab[MARC]+'direct-electronic'),
            'r': I(self._vocab[MARC]+'regular-print-reproduction'),
            's': I(self._vocab[MARC]+'electronic'),
            }

        self.BIOGRAPHICAL = dict(
            a=I(self._vocab[MARC]+"autobiography"),
            b=I(self._vocab[MARC]+'individual-biography'),
            c=I(self._vocab[MARC]+'collective-biography'),
            d=I(self._vocab[MARC]+'contains-biographical-information')
            )

        self.GOVT_PUBLICATION = {
            "a": I(self._vocab[MARC]+"publication-of-autonomous-or-semi-autonomous-component-of-government"),
            "c": I(self._vocab[MARC]+"publication-from-multiple-local-governments"),
            "f": I(self._vocab[MARC]+"federal-national-government-publication"),
            "i": I(self._vocab[MARC]+"international-or-intergovernmental-publication"),
            "l": I(self._vocab[MARC]+"local-government-publication"),
            "m": I(self._vocab[MARC]+"multistate-government-publication"),
            "o": I(self._vocab[MARC]+"government-publication-level-undetermined"),
            "s": I(self._vocab[MARC]+"government-publication-of-a-state-province-territory-dependency-etc"),
            "u": I(self._vocab[MARC]+"unknown-if-item-is-government-publication"),
            "z": I(self._vocab[MARC]+"other-type-of-government-publication")}

        self.INDEX = {
            '0': I(self._vocab[MARC]+'no-index-present'),
            '1': I(self._vocab[MARC]+'index-present'),
        }

        self.LITERARY_FORM = {
            "0": I(self._vocab[MARC]+"non-fiction"),
            "1": I(self._vocab[MARC]+"fiction"),
            "c": I(self._vocab[MARC]+"comic-strips"),
            "d": I(self._vocab[MARC]+"dramas"),
            "e": I(self._vocab[MARC]+"essays"),
            "f": I(self._vocab[MARC]+"novels"),
            "h": I(self._vocab[MARC]+"humor-satires-etc"),
            "i": I(self._vocab[MARC]+"letters"),
            "j": I(self._vocab[MARC]+"short-stories"),
            "m": I(self._vocab[MARC]+"mixed-forms"),
            "p": I(self._vocab[MARC]+"poetry"),
            "s": I(self._vocab[MARC]+"speeches"),
            "u": I(self._vocab[MARC]+'unknown-literary-form')
        }

        self.CONFERENCE_PUBLICATION = {
            '1': I(self._vocab[MARC]+'conference-publication'),
        }

        self.NATURE_OF_CONTENTS = {
            'a': I(self._vocab[MARC]+'abstracts-summaries'),
            'b': I(self._vocab[MARC]+'bibliography'),
            'c': I(self._vocab[MARC]+'catalogs'),
            'd': I(self._vocab[MARC]+'dictionaries'),
            'e': I(self._vocab[MARC]+'encyclopedias'),
            'f': I(self._vocab[MARC]+'handbooks'),
            'g': I(self._vocab[MARC]+'legal-articles'),
            'i': I(self._vocab[MARC]+'indexes'),
            'j': I(self._vocab[MARC]+'patent-document'),
            'k': I(self._vocab[MARC]+'discographies'),
            'l': I(self._vocab[MARC]+'legislation'),
            'm': I(self._vocab[MARC]+'theses'),
            'n': I(self._vocab[MARC]+'surveys-of-literature'),
            'o': I(self._vocab[MARC]+'reviews'),
            'p': I(self._vocab[MARC]+'programmed-texts'),
            'q': I(self._vocab[MARC]+'filmographies'),
            'r': I(self._vocab[MARC]+'directories'),
            's': I(self._vocab[MARC]+'statistics'),
            't': I(self._vocab[MARC]+'technical-reports'),
            'u': I(self._vocab[MARC]+'standards-specifications'),
            'v': I(self._vocab[MARC]+'legal-cases-and-notes'),
            'w': I(self._vocab[MARC]+'law-reports-and-digests'),
            'y': I(self._vocab[MARC]+'yearbooks'),
            'z': I(self._vocab[MARC]+'treaties'),
            '2': I(self._vocab[MARC]+'offprints'),
            '5': I(self._vocab[MARC]+'calendars'),
            '6': I(self._vocab[MARC]+'comics-graphic-novels'),
        }

        self.Books = dict(
            Illustrations = {
                'a': I(self._vocab[MARC]+'illustrations'),
                'b': I(self._vocab[MARC]+'maps'),
                'c': I(self._vocab[MARC]+'portraits'),
                'd': I(self._vocab[MARC]+'charts'),
                'e': I(self._vocab[MARC]+'plans'),
                'f': I(self._vocab[MARC]+'plates'),
                'g': I(self._vocab[MARC]+'music'),
                'h': I(self._vocab[MARC]+'facsimiles'),
                'i': I(self._vocab[MARC]+'coats-of-arms'),
                'j': I(self._vocab[MARC]+'genealogical-tables'),
                'k': I(self._vocab[MARC]+'forms'),
                'l': I(self._vocab[MARC]+'samples'),
                'm': I(self._vocab[MARC]+'phonodisk'),
                'o': I(self._vocab[MARC]+'photographs'),
                'p': I(self._vocab[MARC]+'illuminations'),
            },
            Festschrift = {
                '1': I(self._vocab[MARC]+'festschrift'),
            },
        )

        self.Music = dict(
            FormOfComposition = {
                'an': I(self._vocab[MARC]+'anthems'),
                'bd': I(self._vocab[MARC]+'ballads'),
                'bg': I(self._vocab[MARC]+'bluegrass-music'),
                'bl': I(self._vocab[MARC]+'blues'),
                'bt': I(self._vocab[MARC]+'ballets'),
                'ca': I(self._vocab[MARC]+'chaconnes'),
                'cb': I(self._vocab[MARC]+'chants-other-religions'),
                'cc': I(self._vocab[MARC]+'chant-christian'),
                'cg': I(self._vocab[MARC]+'concerti-grossi'),
                'ch': I(self._vocab[MARC]+'chorales'),
                'cl': I(self._vocab[MARC]+'chorale-preludes'),
                'cn': I(self._vocab[MARC]+'canons-and-rounds'),
                'co': I(self._vocab[MARC]+'concertos'),
                'cp': I(self._vocab[MARC]+'chansons-polyphonic'),
                'cr': I(self._vocab[MARC]+'carols'),
                'cs': I(self._vocab[MARC]+'chance-compositions'),
                'ct': I(self._vocab[MARC]+'cantatas'),
                'cy': I(self._vocab[MARC]+'country-music'),
                'cz': I(self._vocab[MARC]+'canzonas'),
                'df': I(self._vocab[MARC]+'dance-forms'),
                'dv': I(self._vocab[MARC]+'divertimentos-serenades-cassations-divertissements-and-noturni'),
                'fg': I(self._vocab[MARC]+'fugues'),
                'fl': I(self._vocab[MARC]+'flamenco'),
                'fm': I(self._vocab[MARC]+'folk-music'),
                'ft': I(self._vocab[MARC]+'fantasias'),
                'gm': I(self._vocab[MARC]+'gospel-music'),
                'hy': I(self._vocab[MARC]+'hymns'),
                'jz': I(self._vocab[MARC]+'jazz'),
                'mc': I(self._vocab[MARC]+'musical-revues-and-comedies'),
                'md': I(self._vocab[MARC]+'madrigals'),
                'mi': I(self._vocab[MARC]+'minuets'),
                'mo': I(self._vocab[MARC]+'motets'),
                'mp': I(self._vocab[MARC]+'motion-picture-music'),
                'mr': I(self._vocab[MARC]+'marches'),
                'ms': I(self._vocab[MARC]+'masses'),
                'mu': I(self._vocab[MARC]+'multiple-forms'),
                'mz': I(self._vocab[MARC]+'mazurkas'),
                'nc': I(self._vocab[MARC]+'nocturnes'),
                'nn': I(self._vocab[MARC]+'not-applicable'),
                'op': I(self._vocab[MARC]+'operas'),
                'or': I(self._vocab[MARC]+'oratorios'),
                'ov': I(self._vocab[MARC]+'overtures'),
                'pg': I(self._vocab[MARC]+'program-music'),
                'pm': I(self._vocab[MARC]+'passion-music'),
                'po': I(self._vocab[MARC]+'polonaises'),
                'pp': I(self._vocab[MARC]+'popular-music'),
                'pr': I(self._vocab[MARC]+'preludes'),
                'ps': I(self._vocab[MARC]+'passacaglias'),
                'pt': I(self._vocab[MARC]+'part-songs'),
                'pv': I(self._vocab[MARC]+'pavans'),
                'rc': I(self._vocab[MARC]+'rock-music'),
                'rd': I(self._vocab[MARC]+'rondos'),
                'rg': I(self._vocab[MARC]+'ragtime-music'),
                'ri': I(self._vocab[MARC]+'ricercars'),
                'rp': I(self._vocab[MARC]+'rhapsodies'),
                'rq': I(self._vocab[MARC]+'requiems'),
                'sd': I(self._vocab[MARC]+'square-dance-music'),
                'sg': I(self._vocab[MARC]+'songs'),
                'sn': I(self._vocab[MARC]+'sonatas'),
                'sp': I(self._vocab[MARC]+'symphonic-poems'),
                'st': I(self._vocab[MARC]+'studies-and-exercises'),
                'su': I(self._vocab[MARC]+'suites'),
                'sy': I(self._vocab[MARC]+'symphonies'),
                'tc': I(self._vocab[MARC]+'toccatas'),
                'tl': I(self._vocab[MARC]+'teatro-lirico'),
                'ts': I(self._vocab[MARC]+'trio-sonatas'),
                'uu': I(self._vocab[MARC]+'unknown-form-of-composition'),
                'vi': I(self._vocab[MARC]+'villancicos'),
                'vr': I(self._vocab[MARC]+'variations'),
                'wz': I(self._vocab[MARC]+'waltzes'),
                'za': I(self._vocab[MARC]+'zarzuelas'),
                'zz': I(self._vocab[MARC]+'other-form-of-composition'),
            },
            FormatOfMusic = {
                'a': I(self._vocab[MARC]+'full-score'),
                'b': I(self._vocab[MARC]+'full-score-miniature-or-study-size'),
                'c': I(self._vocab[MARC]+'accompaniment-reduced-for-keyboard'),
                'd': I(self._vocab[MARC]+'voice-score-with-accompaniment-omitted'),
                'e': I(self._vocab[MARC]+'condensed-score-or-piano-conductor-score'),
                'g': I(self._vocab[MARC]+'close-score'),
                'h': I(self._vocab[MARC]+'chorus-score'),
                'i': I(self._vocab[MARC]+'condensed-score'),
                'j': I(self._vocab[MARC]+'performer-conductor-part'),
                'k': I(self._vocab[MARC]+'vocal-score'),
                'l': I(self._vocab[MARC]+'score'),
                'm': I(self._vocab[MARC]+'multiple-score-formats'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown-music-format'),
                'z': I(self._vocab[MARC]+'other-music-format'),
            },
            MusicParts = {
                'd': I(self._vocab[MARC]+'instrumental-and-vocal-parts'),
                'e': I(self._vocab[MARC]+'instrumental-parts'),
                'f': I(self._vocab[MARC]+'vocal-parts'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown-parts'),
            },
            AccompanyingMatter = {
                'a': I(self._vocab[MARC]+'discography'),
                'b': I(self._vocab[MARC]+'bibliography'),
                'c': I(self._vocab[MARC]+'thematic-index'),
                'd': I(self._vocab[MARC]+'libretto-or-text'),
                'e': I(self._vocab[MARC]+'biography-of-composer-or-author'),
                'f': I(self._vocab[MARC]+'biography-of-performer-or-history-of-ensemble'),
                'g': I(self._vocab[MARC]+'technical-and-or-historical-information-on-instruments'),
                'h': I(self._vocab[MARC]+'technical-information-on-music'),
                'i': I(self._vocab[MARC]+'historical-information'),
                'k': I(self._vocab[MARC]+'ethnological-information'),
                'r': I(self._vocab[MARC]+'instructional-materials'),
                's': I(self._vocab[MARC]+'music'),
                'z': I(self._vocab[MARC]+'other-accompanying-matter'),
            },
            LiteraryTextForSoundRecordings = {
                'a': I(self._vocab[MARC]+'autobiography'),
                'b': I(self._vocab[MARC]+'biography'),
                'c': I(self._vocab[MARC]+'conference-proceedings'),
                'd': I(self._vocab[MARC]+'drama'),
                'e': I(self._vocab[MARC]+'essays'),
                'f': I(self._vocab[MARC]+'fiction'),
                'g': I(self._vocab[MARC]+'reporting'),
                'h': I(self._vocab[MARC]+'history'),
                'i': I(self._vocab[MARC]+'instruction'),
                'j': I(self._vocab[MARC]+'language-instruction'),
                'k': I(self._vocab[MARC]+'comedy'),
                'l': I(self._vocab[MARC]+'lectures-speeches'),
                'm': I(self._vocab[MARC]+'memoirs'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'o': I(self._vocab[MARC]+'folktales'),
                'p': I(self._vocab[MARC]+'poetry'),
                'r': I(self._vocab[MARC]+'rehearsals'),
                's': I(self._vocab[MARC]+'sounds'),
                't': I(self._vocab[MARC]+'interviews'),
                'z': I(self._vocab[MARC]+'other-literary-text-for-sound-recordings'),
            },
            TranspositionAndArrangement = {
                'a': I(self._vocab[MARC]+'transposition'),
                'b': I(self._vocab[MARC]+'arrangement'),
                'c': I(self._vocab[MARC]+'both-transposed-and-arranged'),
                'n': I(self._vocab[MARC]+'not-applicable-transposition-and-arrangement'),
                'u': I(self._vocab[MARC]+'unknown-transposition-and-arrangement'),
            }
        )

        self.Maps = dict(
            Relief = {
                'a': I(self._vocab[MARC]+'contours'),
                'b': I(self._vocab[MARC]+'shading'),
                'c': I(self._vocab[MARC]+'gradient-and-bathymetric-tints'),
                'd': I(self._vocab[MARC]+'hachures'),
                'e': I(self._vocab[MARC]+'bathymetry-soundings'),
                'f': I(self._vocab[MARC]+'form-lines'),
                'g': I(self._vocab[MARC]+'spot-heights'),
                'i': I(self._vocab[MARC]+'pictorially'),
                'j': I(self._vocab[MARC]+'land-forms'),
                'k': I(self._vocab[MARC]+'bathymetry-isolines'),
                'm': I(self._vocab[MARC]+'rock-drawings'),
                'z': I(self._vocab[MARC]+'other-relief'),
            },
            Projection = {
                'aa': I(self._vocab[MARC]+'aitoff'),
                'ab': I(self._vocab[MARC]+'gnomic'),
                'ac': I(self._vocab[MARC]+'lamberts-azimuthal-equal-area'),
                'ad': I(self._vocab[MARC]+'orthographic'),
                'ae': I(self._vocab[MARC]+'azimuthal-equidistant'),
                'af': I(self._vocab[MARC]+'stereographic'),
                'ag': I(self._vocab[MARC]+'general-vertical-near-sided'),
                'am': I(self._vocab[MARC]+'modified-stereographic-for-alaska'),
                'an': I(self._vocab[MARC]+'chamberlain-trimetric'),
                'ap': I(self._vocab[MARC]+'polar-stereographic'),
                'au': I(self._vocab[MARC]+'azimuthal-specific-type-unknown'),
                'az': I(self._vocab[MARC]+'azimuthal-other'),
                'ba': I(self._vocab[MARC]+'gall'),
                'bb': I(self._vocab[MARC]+'goodes-homolographic'),
                'bc': I(self._vocab[MARC]+'lamberts-cylindrical-equal-area'),
                'bd': I(self._vocab[MARC]+'mercator'),
                'be': I(self._vocab[MARC]+'miller'),
                'bf': I(self._vocab[MARC]+'mollweide'),
                'bg': I(self._vocab[MARC]+'sinusoidal'),
                'bh': I(self._vocab[MARC]+'transverse-mercator'),
                'bi': I(self._vocab[MARC]+'gauss-kruger'),
                'bj': I(self._vocab[MARC]+'equirectangular'),
                'bk': I(self._vocab[MARC]+'krovak'),
                'bl': I(self._vocab[MARC]+'cassini-soldner'),
                'bo': I(self._vocab[MARC]+'oblique-mercator'),
                'br': I(self._vocab[MARC]+'robinson'),
                'bs': I(self._vocab[MARC]+'space-oblique-mercator'),
                'bu': I(self._vocab[MARC]+'cylindrical-specific-type-unknown'),
                'bz': I(self._vocab[MARC]+'cylindrical-other'),
                'ca': I(self._vocab[MARC]+'albers-equal-area'),
                'cb': I(self._vocab[MARC]+'bonne'),
                'cc': I(self._vocab[MARC]+'lamberts-conformal-conic'),
                'ce': I(self._vocab[MARC]+'equidistant-conic'),
                'cp': I(self._vocab[MARC]+'polyconic'),
                'cu': I(self._vocab[MARC]+'conic-specific-type-unknown'),
                'cz': I(self._vocab[MARC]+'conic-other'),
                'da': I(self._vocab[MARC]+'armadillo'),
                'db': I(self._vocab[MARC]+'butterfly'),
                'dc': I(self._vocab[MARC]+'eckert'),
                'dd': I(self._vocab[MARC]+'goodes-homolosine'),
                'de': I(self._vocab[MARC]+'millers-bipolar-oblique-conformal-optic'),
                'df': I(self._vocab[MARC]+'van-der-grinten'),
                'dg': I(self._vocab[MARC]+'dimaxion'),
                'dh': I(self._vocab[MARC]+'cordiform'),
                'dl': I(self._vocab[MARC]+'lambert-conformal'),
                'zz': I(self._vocab[MARC]+'other-projection'),
            },
            TypeOfCartographicMaterial = {
                'a': I(self._vocab[MARC]+'single-map'),
                'b': I(self._vocab[MARC]+'map-series'),
                'c': I(self._vocab[MARC]+'map-serial'),
                'd': I(self._vocab[MARC]+'globe'),
                'e': I(self._vocab[MARC]+'atlas'),
                'f': I(self._vocab[MARC]+'separate-supplement-to-another-work'),
                'g': I(self._vocab[MARC]+'bound-as-part-of-another-work'),
                'u': I(self._vocab[MARC]+'unknown-type-of-cartographic-material'),
                'z': I(self._vocab[MARC]+'other-type-of-cartographic-material'),
            },
            SpecialFormatCharacteristics = {
                'e': I(self._vocab[MARC]+'manuscript'),
                'j': I(self._vocab[MARC]+'picture-card-post-card'),
                'k': I(self._vocab[MARC]+'calendar'),
                'l': I(self._vocab[MARC]+'puzzle'),
                'n': I(self._vocab[MARC]+'game'),
                'o': I(self._vocab[MARC]+'wall-map'),
                'p': I(self._vocab[MARC]+'playing-cards'),
                'r': I(self._vocab[MARC]+'loose-leaf'),
                'z': I(self._vocab[MARC]+'other-special-format-characteristic'),
            },
        )

        self.VisualMaterials = dict(
            TypeOfVisualMaterial = {
                'a': I(self._vocab[MARC]+'art-original'),
                'b': I(self._vocab[MARC]+'kit'),
                'c': I(self._vocab[MARC]+'art-reproduction'),
                'd': I(self._vocab[MARC]+'diorama'),
                'f': I(self._vocab[MARC]+'filmstrip'),
                'g': I(self._vocab[MARC]+'game'),
                'i': I(self._vocab[MARC]+'picture'),
                'k': I(self._vocab[MARC]+'graphic'),
                'l': I(self._vocab[MARC]+'technical-drawing'),
                'm': I(self._vocab[MARC]+'motion-picture'),
                'n': I(self._vocab[MARC]+'chart'),
                'o': I(self._vocab[MARC]+'flash-card'),
                'p': I(self._vocab[MARC]+'microscope-slide'),
                'q': I(self._vocab[MARC]+'model'),
                'r': I(self._vocab[MARC]+'realia'),
                's': I(self._vocab[MARC]+'slide'),
                't': I(self._vocab[MARC]+'transparency'),
                'v': I(self._vocab[MARC]+'videorecording'),
                'w': I(self._vocab[MARC]+'toy'),
                'z': I(self._vocab[MARC]+'other-type-of-visual-material'),

            },
            Technique = {
                'a': I(self._vocab[MARC]+'animation'),
                'c': I(self._vocab[MARC]+'animation-and-live-action'),
                'l': I(self._vocab[MARC]+'live-action'),
                'n': I(self._vocab[MARC]+'not-applicable-technique'),
                'u': I(self._vocab[MARC]+'unknown-technique'),
                'z': I(self._vocab[MARC]+'other-technique'),
            }
        )

        self.ComputerFiles = dict(
            FormOfItem = { # subset of FORM_OF_ITEM
                'o': I(self._vocab[MARC]+'online'),
                'q': I(self._vocab[MARC]+'direct-electronic'),
            },
            TypeOfComputerFile = {
                'a': I(self._vocab[MARC]+'numeric-data'),
                'b': I(self._vocab[MARC]+'computer-program'),
                'c': I(self._vocab[MARC]+'representational'),
                'd': I(self._vocab[MARC]+'document'),
                'e': I(self._vocab[MARC]+'bibliographic-data'),
                'f': I(self._vocab[MARC]+'font'),
                'g': I(self._vocab[MARC]+'game'),
                'h': I(self._vocab[MARC]+'sound'),
                'i': I(self._vocab[MARC]+'interactive-multimedia'),
                'j': I(self._vocab[MARC]+'online-system-or-service'),
                'm': I(self._vocab[MARC]+'combination'),
                'u': I(self._vocab[MARC]+'unknown-type-of-computer-file'),
                'z': I(self._vocab[MARC]+'other-type-of-computer-file'),
            }
        )

        self.ContinuingResources = dict(
            Frequency = {
                'a': I(self._vocab[MARC]+'annual'),
                'b': I(self._vocab[MARC]+'bimonthly'),
                'c': I(self._vocab[MARC]+'semiweekly'),
                'd': I(self._vocab[MARC]+'daily'),
                'e': I(self._vocab[MARC]+'biweekly'),
                'f': I(self._vocab[MARC]+'semiannual'),
                'g': I(self._vocab[MARC]+'biennial'),
                'h': I(self._vocab[MARC]+'triennial'),
                'i': I(self._vocab[MARC]+'three-times-a-week'),
                'j': I(self._vocab[MARC]+'three-times-a-month'),
                'k': I(self._vocab[MARC]+'continuously-updated'),
                'm': I(self._vocab[MARC]+'monthly'),
                'q': I(self._vocab[MARC]+'quarterly'),
                't': I(self._vocab[MARC]+'three-times-a-year'),
                'u': I(self._vocab[MARC]+'unknown-frequency'),
                'w': I(self._vocab[MARC]+'weekly'),
                'z': I(self._vocab[MARC]+'other-frequency'),
            },
            Regularity = {
                'n': I(self._vocab[MARC]+'normalized-irregular'),
                'r': I(self._vocab[MARC]+'regular'),
                'u': I(self._vocab[MARC]+'unknown'),
                'x': I(self._vocab[MARC]+'complete-irregular'),
            },
            TypeOfContinuingResource = {
                'd': I(self._vocab[MARC]+'updating-database'),
                'l': I(self._vocab[MARC]+'updating-loose-leaf'),
                'm': I(self._vocab[MARC]+'monographic-series'),
                'n': I(self._vocab[MARC]+'newspaper'),
                'p': I(self._vocab[MARC]+'periodical'),
                'w': I(self._vocab[MARC]+'updating-web-site'),
            },
            OriginalAlphabetOrScriptOfTitle = {
                'a': I(self._vocab[MARC]+'basic-roman'),
                'b': I(self._vocab[MARC]+'extended-roman'),
                'c': I(self._vocab[MARC]+'cyrillic'),
                'd': I(self._vocab[MARC]+'japanese'),
                'e': I(self._vocab[MARC]+'chinese'),
                'f': I(self._vocab[MARC]+'arabic'),
                'g': I(self._vocab[MARC]+'greek'),
                'h': I(self._vocab[MARC]+'hebrew'),
                'i': I(self._vocab[MARC]+'thai'),
                'j': I(self._vocab[MARC]+'devanagari'),
                'k': I(self._vocab[MARC]+'korean'),
                'l': I(self._vocab[MARC]+'tamil'),
                'u': I(self._vocab[MARC]+'unknown-alphabet'),
                'z': I(self._vocab[MARC]+'other-alphabet'),
            },
            EntryConvention = {
                '0': I(self._vocab[MARC]+'successive-entry'),
                '1': I(self._vocab[MARC]+'latest-entry'),
                '2': I(self._vocab[MARC]+'integrated-entry'),
            }
        )

        # leader6+7 lookup based on all the "field definition and scope" sections below
        # http://www.loc.gov/marc/bibliographic/bd008.html
        self.MATERIAL_TYPE = {
            'aa': 'Books',
            'ab': 'ContinuingResources',
            'ac': 'Books',
            'ad': 'Books',
            'ai': 'ContinuingResources',
            'am': 'Books',
            'as': 'ContinuingResources',
            'c': 'Music',
            'd': 'Music',
            'e': 'Maps',
            'f': 'Maps',
            'g': 'VisualMaterials',
            'i': 'Music',
            'j': 'Music',
            'k': 'VisualMaterials',
            'm': 'ComputerFiles',
            'o': 'VisualMaterials',
            'p': 'MixedMaterials',
            'r': 'VisualMaterials',
            'ta': 'Books',
            'tb': 'ContinuingResources',
            'tc': 'Books',
            'td': 'Books',
            'ti': 'ContinuingResources',
            'tm': 'Books',
            'ts': 'ContinuingResources',
        }

        return

    def process_leader(self, params):
        """
        Processes leader field according to the MARC standard.
        http://www.loc.gov/marc/marc2dc.html#ldr06conversionrules
        http://www.loc.gov/marc/bibliographic/bdleader.html

        :leader: - text of leader field, a character array
        :work: - work resource in context of which leader is being processed. Useful in the return value.
        :instance: - instance resource in context of which leader is being processed. Useful in the return value.

        yields - 0 or more 3-tuples, (origin, rel, target), each representing a new
            link generated from leader data. origin is almost always the work or instance
            resource passed in. If origin is None, signal to the caller to default
            to the work as origin

        >>> from bibframe.reader.marcextra import transforms
        >>> t = transforms()
        >>> list(t.process_leader({'leader':'03495cpcaa2200673 a 4500','workid':None,'instanceids':[None]}))
        [(None, I(http://bibfra.me/purl/versa/type), (I(http://bibfra.me/vocab/marc/Collection), I(http://bibfra.me/vocab/marc/Multimedia))), (None, I(http://bibfra.me/purl/versa/type), I(http://bibfra.me/vocab/marc/Collection))]
        """
        if 'leader' not in params: return

        leader = params['leader']
        leader = leader.ljust(24) if leader is not None else ' '*24

        work = params['workid']
        instance = params['instanceids'][0]
        work_06 = dict(
            a=I(self._vocab[MARC]+"LanguageMaterial"),
            c=(I(self._vocab[MARC]+"LanguageMaterial"), I(self._vocab[MARC]+"NotatedMusic")),
            d=(I(self._vocab[MARC]+"LanguageMaterial"), I(self._vocab[MARC]+"Manuscript"), I(self._vocab[MARC]+"NotatedMusic")),
            e=(I(self._vocab[MARC]+"StillImage"), I(self._vocab[MARC]+"Cartography")),
            f=(I(self._vocab[MARC]+"Manuscript"), I(self._vocab[MARC]+"Cartography"), I(self._vocab[MARC]+"StillImage")),
            g=I(self._vocab[MARC]+"MovingImage"),
            i=(I(self._vocab[MARC]+"Audio"), I(self._vocab[MARC]+"Nonmusical"), I(self._vocab[MARC]+"Sounds")),
            j=(I(self._vocab[MARC]+"Audio"), I(self._vocab[MARC]+"Musical")),
            k=I(self._vocab[MARC]+"StillImage"),
            m=(I(self._vocab[MARC]+"Multimedia"), I(self._vocab[MARC]+"Software")),
            o=I(self._vocab[MARC]+"Kit"),
            p=(I(self._vocab[MARC]+"Collection"), I(self._vocab[MARC]+"Multimedia")),
            r=I(self._vocab[MARC]+"ThreeDimensionalObject"),
            t=(I(self._vocab[MARC]+"LanguageMaterial"), I(self._vocab[MARC]+"Manuscript"))
            )

        instance_06 = dict(
            )

        _06 = leader[6]
        if _06 in work_06.keys():
            yield work, I(self._vocab[VTYPE]), work_06[_06]
        if _06 in instance_06.keys():
            yield instance, I(self._vocab[VTYPE]), instance_06[_06]
        if leader[7] in ('c', 's'):
            yield None, I(self._vocab[VTYPE]), I(self._vocab[MARC]+"Collection")

    def _process_fixed_length(self, info, offset, params):
        """
        Processes 008 and 006 control fields containing fixed length data elements,
        according to the MARC standard http://www.loc.gov/marc/umb/um07to10.html#part9

        :info: - text of 008 or a single 006 field, a character array
        :offset: - byte offset into 'info' containing germane data. 18 for 008, 0 for 006
        :params: - work and instance resources in context of which 008 is being processed. Useful in the return value.

        yields - 0 or more 3-tuples, (origin, rel, target), each representing a new
            link generated from 008 data. origin is almost always the work or instance
            resource passed in. If origin is None, signal to the caller to default
            to the work as origin

        """
        if info is None: return

        leader = params['leader']
        work = params['workid']
        instance = params['instanceids'][0]
        logger = params['logger']

        #Marc chaacters skipped in the 008 field by convention
        #In most cases we dont have to actually check for these, as they'll just not be in the value lookup tables above
        SKIP_CHARS = ('#', ' ', '|')

        # Registry of patterns to be processed from 008 field {index key: value function}
        # There are 3 types of index keys to this dict
        # 1) An int, simply processed as a character position passed to the value function
        # 2) A tuple of ints, processed once for each character position in the list, each int passed to the value function
        # 3) A tuple starting with 'slice' and then 2 ints, processed as a character chunk/slice passed as a whole to the value function
        # If the value function returns None or a tuple with None in the lats position, it's a signal to do nothing for the case at hand
        PATTERNS = dict(
            Books = {
                (0, 1, 2, 3): lambda i: (None, I(self._vocab[MARC]+'illustrations'), SLUG(self.Books['Illustrations'].get(info[i]))),
                4: lambda i: (None, I(self._vocab[MARC]+'targetAudience'), SLUG(self.AUDIENCE.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                (6, 7, 8, 9): lambda i: (None, I(self._vocab[MARC]+'natureOfContents'), SLUG(self.NATURE_OF_CONTENTS.get(info[i]))),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
                11: lambda i: (None, I(self._vocab[VTYPE]), self.CONFERENCE_PUBLICATION.get(info[i])),
                12: lambda i: (None, I(self._vocab[VTYPE]), self.Books['Festschrift'].get(info[i])),
                13: lambda i: (None, I(self._vocab[MARC]+'index'), SLUG(self.INDEX.get(info[i]))),
                15: lambda i: (None, I(self._vocab[MARC]+'literaryForm'), SLUG(self.LITERARY_FORM.get(info[i]))),
                16: lambda i: (None, I(self._vocab[MARC]+'biographical'), SLUG(self.BIOGRAPHICAL.get(info[i]))),
            },
            Music = {
                ('slice', 0, 2): lambda i: (None, I(self._vocab[MARC]+'formOfComposition'), SLUG(self.Music['FormOfComposition'].get(info[i]))),
                2: lambda i: (None, I(self._vocab[MARC]+'formatOfMusic'), SLUG(self.Music['FormatOfMusic'].get(info[i]))),
                3: lambda i: (None, I(self._vocab[MARC]+'musicParts'), SLUG(self.Music['MusicParts'].get(info[i]))),
                4: lambda i: (None, I(self._vocab[MARC]+'targetAudience'), SLUG(self.AUDIENCE.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                (6, 7, 8, 9, 10, 11): lambda i: (None, I(self._vocab[MARC]+'accompanyingMatter'), SLUG(self.Music['AccompanyingMatter'].get(info[i]))),
                (12, 13): lambda i: (None, I(self._vocab[MARC]+'literaryTextForSoundRecordings'), SLUG(self.Music['LiteraryTextForSoundRecordings'].get(info[i]))),
                15: lambda i: (None, I(self._vocab[MARC]+'transpositionAndArrangement'), SLUG(self.Music['TranspositionAndArrangement'].get(info[i]))),
            },
            Maps = {
                (0, 1, 2, 3): lambda i: (None, I(self._vocab[MARC]+'relief'), SLUG(self.Maps['Relief'].get(info[i]))),
                ('slice', 4, 5): lambda i: (None, I(self._vocab[MARC]+'projection'), SLUG(self.Maps['Projection'].get(info[i]))),
                7: lambda i: (instance, I(self._vocab[VTYPE]), self.Maps['TypeOfCartographicMaterial'].get(info[i])),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
                11: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                13: lambda i: (None, I(self._vocab[MARC]+'index'), SLUG(self.INDEX.get(info[i]))),
                (15, 16): lambda i: (None, I(self._vocab[MARC]+'specialFormatCharacteristics'), SLUG(self.Maps['SpecialFormatCharacteristics'].get(info[i]))),
            },
            VisualMaterials = {
                ('slice', 0, 2): lambda i: (None, I(self._vocab[MARC]+'runtime'), runtime(info[i])),
                4: lambda i: (None, I(self._vocab[MARC]+'targetAudience'), SLUG(self.AUDIENCE.get(info[i]))),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
                11: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                15: lambda i: (instance, I(self._vocab[VTYPE]), self.VisualMaterials['TypeOfVisualMaterial'].get(info[i])),
                16: lambda i: (None, I(self._vocab[MARC]+'technique'), SLUG(self.VisualMaterials['Technique'].get(info[i]))),
            },
            ComputerFiles = {
                4: lambda i: (None, I(self._vocab[MARC]+'targetAudience'), SLUG(self.AUDIENCE.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.ComputerFiles['FormOfItem'].get(info[i]))),
                8: lambda i: (None, I(self._vocab[VTYPE]), self.ComputerFiles['TypeOfComputerFile'].get(info[i])),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
            },
            MixedMaterials = {
                5: lambda i: (None, I(self._vocab[VTYPE]), self.FORM_OF_ITEM.get(info[i])),
            },
            ContinuingResources = {
                0: lambda i: (None, I(self._vocab[MARC]+'frequency'), SLUG(self.ContinuingResources['Frequency'].get(info[i]))),
                1: lambda i: (None, I(self._vocab[MARC]+'regularity'), SLUG(self.ContinuingResources['Regularity'].get(info[i]))),
                3: lambda i: (None, I(self._vocab[VTYPE]), self.ContinuingResources['TypeOfContinuingResource'].get(info[i])),
                4: lambda i: (instance, I(self._vocab[MARC]+'formOfOriginalItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                6: lambda i: (None, I(self._vocab[MARC]+'natureOfEntireWork'), SLUG(self.NATURE_OF_CONTENTS.get(info[i]))),
                (7,8,9): lambda i: (None, I(self._vocab[MARC]+'natureOfContents'), SLUG(self.NATURE_OF_CONTENTS.get(info[i]))),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
                11: lambda i: (None, I(self._vocab[VTYPE]), self.CONFERENCE_PUBLICATION.get(info[i])),
                15: lambda i: (None, I(self._vocab[MARC]+'originalAlphabetOrScriptOfTitle'), SLUG(self.ContinuingResources['OriginalAlphabetOrScriptOfTitle'].get(info[i]))),
                16: lambda i: (None, I(self._vocab[MARC]+'entryConvention'), SLUG(self.ContinuingResources['EntryConvention'].get(info[i]))),
            }
        )

        # build new patterns from existing patterns by byte shifting, i.e. 18 bytes for 006->008
        def shift_patterns(patterns, offset):
            new_patt = {}
            for k, v in patterns.items():
                if isinstance(k, tuple):
                    if k[0] == 'slice':
                        new_k = (k[0], k[1]+offset, k[2]+offset)
                    else:
                        new_k = tuple((kk+offset for kk in k))
                else: # int
                    new_k = k+offset

                new_patt[new_k] = v

            return new_patt

        # first perform 6/7 lookup, then fallback to 6 lookup
        _06 = leader[6]
        _07 = leader[7] if leader[7] != ' ' else ''
        typ = self.MATERIAL_TYPE.get(_06+_07)
        if not typ:
            typ = self.MATERIAL_TYPE.get(_06)
            if not typ:
                logger.debug('Unknown leader 6/7 combination "{}"'.format(_06+_07))

        # add a type statement for this type too
        if typ: yield work, I(self._vocab[VTYPE]), I(self._vocab[MARC]+typ)

        patterns = PATTERNS.get(typ)
        if patterns:
            if offset:
                patterns = shift_patterns(patterns, offset)

            yield from process_patterns(patterns)

    def process_008(self, info, params):
        '''
        Processes 008 control fields
        
        #>>> from bibframe.reader.marcextra import transforms
        #>>> import logging
        #>>> t = transforms()
        #>>> ld = '790726||||||||||||                 eng  '
        #>>> list(t.process_008(ld,{'leader':ld,'workid':None,'instanceids':[None],'logger':logging}))
        #[('date_008', '1979-07-26')]
        '''
        if info is None: return

        # pad to expected size
        info = info.ljust(40)

        #ARE YOU FRIGGING KIDDING ME?! MARC/008 is NON-Y2K SAFE?!
        year = info[0:2]
        try:
            century = '19' if int(year) > 30 else '20' #I guess we can give an 18 year berth before this breaks ;)
            # remove date_008 from data export at this time
            # yield 'date_008', '{}{}-{}-{}'.format(century, year, info[2:4], info[4:6])
        except ValueError:
            #Completely Invalid date
            pass

        yield from self._process_fixed_length(info, 18, params)

    def process_006(self, infos, params):
        '''
        Re: Multiple 006 fields see page 2 of University of Colorado Boulder University Libraries Cataloging Procedures Manual,
        "Books with Accompanying Media" https://ucblibraries.colorado.edu/cataloging/cpm/bookswithmedia.pdf
        '''
        for info in infos:
            # pad to expected size
            info = info.ljust(18)

            yield from self._process_fixed_length(info, 0, params)

def process_patterns(patterns):
    #Execute the rules detailed in the various positional patterns lookup tables above
    for i, func in patterns.items():
        if isinstance(i, tuple):
            if i[0] == 'slice':
                params = [slice(i[1], i[2])]
            else:
                params = i
        elif isinstance(i, int):
            params = [i]

        for param in params:
            try:
                result = func(param)
                result = result if isinstance(result, list) else [result]
                for r in result:
                    if r and r[2] is not None:
                        yield r
            except IndexError:
                pass #Truncated field
