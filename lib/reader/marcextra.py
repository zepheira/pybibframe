'''
Treatment of certain special MARC fields, leader, 006, 007, 008, etc.
'''

from versa import I, VERSA_BASEIRI
from bibframe import BL, BA, REL, RDA, RBMS, AV

BL = 'http://bibfra.me/vocab/lite/'

#TODO: Also split on multiple 260 fields

VTYPE = VERSA_BASEIRI+'type'
LANG= BL+'language'
DEFAULT_VOCAB_ITEMS = [BL, BA, REL, RDA, RBMS, AV, LANG, VTYPE]

SLUG = lambda s: s.rsplit('/')[-1] if s else None

def runtime(rt):
    '''
    Handle visual material running time property
    '''
    runtime = None # no runtime property produced
    if isinstance(rt, str):
        if rt == 'nnn':
            runtime = I(self._vocab[BL]+"running-time-not-applicable")
        elif rt == '---':
            runtime = I(self._vocab[BL]+"unknown-running-time")
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
            'a': I(self._vocab[BL]+"preschool"),
            'b': I(self._vocab[BL]+"primary"),
            'c': I(self._vocab[BL]+"pre-adolescent"),
            'd': I(self._vocab[BL]+"adolescent"),
            'e': I(self._vocab[BL]+"adult"),
            'f': I(self._vocab[BL]+"specialized"),
            'g': I(self._vocab[BL]+"general"),
            'j': I(self._vocab[BL]+"juvenile")
            }

        self.FORM_OF_ITEM = {
            'a': I(self._vocab[BL]+'microfilm'),
            'b': I(self._vocab[BL]+'microfiche'),
            'c': I(self._vocab[BL]+'microopaque'),
            'd': I(self._vocab[BL]+'large-print'),
            'f': I(self._vocab[BL]+'braille'),
            'o': I(self._vocab[BL]+'online'),
            'q': I(self._vocab[BL]+'direct-electronic'),
            'r': I(self._vocab[BL]+'regular-print-reproduction'),
            's': I(self._vocab[BL]+'electronic'),
            }

        self.BIOGRAPHICAL = dict(
            a=I(self._vocab[BL]+"autobiography"),
            b=I(self._vocab[BL]+'individual-biography'),
            c=I(self._vocab[BL]+'collective-biography'),
            d=I(self._vocab[BL]+'contains-biographical-information')
            )

        self.GOVT_PUBLICATION = {
            "a": I(self._vocab[BL]+"publication-of-autonomous-or-semi-autonomous-component-of-government"),
            "c": I(self._vocab[BL]+"publication-from-multiple-local-governments"),
            "f": I(self._vocab[BL]+"federal-national-government-publication"),
            "i": I(self._vocab[BL]+"international-or-intergovernmental-publication"),
            "l": I(self._vocab[BL]+"local-government-publication"),
            "m": I(self._vocab[BL]+"multistate-government-publication"),
            "o": I(self._vocab[BL]+"government-publication-level-undetermined"),
            "s": I(self._vocab[BL]+"government-publication-of-a-state-province-territory-dependency-etc"),
            "u": I(self._vocab[BL]+"unknown-if-item-is-government-publication"),
            "z": I(self._vocab[BL]+"other-type-of-government-publication")}

        self.INDEX = {
            '0': I(self._vocab[BL]+'no-index-present'),
            '1': I(self._vocab[BL]+'index-present'),
        }

        self.LITERARY_FORM = {
            "0": I(self._vocab[BL]+"non-fiction"),
            "1": I(self._vocab[BL]+"fiction"),
            "c": I(self._vocab[BL]+"comic-strips"),
            "d": I(self._vocab[BL]+"dramas"),
            "e": I(self._vocab[BL]+"essays"),
            "f": I(self._vocab[BL]+"novels"),
            "h": I(self._vocab[BL]+"humor-satires-etc"),
            "i": I(self._vocab[BL]+"letters"),
            "j": I(self._vocab[BL]+"short-stories"),
            "m": I(self._vocab[BL]+"mixed-forms"),
            "p": I(self._vocab[BL]+"poetry"),
            "s": I(self._vocab[BL]+"speeches"),
            "u": I(self._vocab[BL]+'unknown-literary-form')
        }

        self.Books = dict(
            Illustrations = {
                'a': I(self._vocab[BL]+'illustrations'),
                'b': I(self._vocab[BL]+'maps'),
                'c': I(self._vocab[BL]+'portraits'),
                'd': I(self._vocab[BL]+'charts'),
                'e': I(self._vocab[BL]+'plans'),
                'f': I(self._vocab[BL]+'plates'),
                'g': I(self._vocab[BL]+'music'),
                'h': I(self._vocab[BL]+'facsimiles'),
                'i': I(self._vocab[BL]+'coats-of-arms'),
                'j': I(self._vocab[BL]+'genealogical-tables'),
                'k': I(self._vocab[BL]+'forms'),
                'l': I(self._vocab[BL]+'samples'),
                'm': I(self._vocab[BL]+'phonodisk'),
                'o': I(self._vocab[BL]+'photographs'),
                'p': I(self._vocab[BL]+'illuminations'),
            },
            NatureOfContents = { # numeric keys
                'a': I(self._vocab[BL]+'abstracts-summaries'),
                'b': I(self._vocab[BL]+'bibliography'),
                'c': I(self._vocab[BL]+'catalogs'),
                'd': I(self._vocab[BL]+'dictionaries'),
                'e': I(self._vocab[BL]+'encyclopedias'),
                'f': I(self._vocab[BL]+'handbooks'),
                'g': I(self._vocab[BL]+'legal-articles'),
                'i': I(self._vocab[BL]+'indexes'),
                'j': I(self._vocab[BL]+'patent-document'),
                'k': I(self._vocab[BL]+'discographies'),
                'l': I(self._vocab[BL]+'legislation'),
                'm': I(self._vocab[BL]+'theses'),
                'n': I(self._vocab[BL]+'surveys-of-literature'),
                'o': I(self._vocab[BL]+'reviews'),
                'p': I(self._vocab[BL]+'programmed-texts'),
                'q': I(self._vocab[BL]+'filmographies'),
                'r': I(self._vocab[BL]+'directories'),
                's': I(self._vocab[BL]+'statistics'),
                't': I(self._vocab[BL]+'technical-reports'),
                'u': I(self._vocab[BL]+'standards-specifications'),
                'v': I(self._vocab[BL]+'legal-cases-and-notes'),
                'w': I(self._vocab[BL]+'law-reports-and-digests'),
                'y': I(self._vocab[BL]+'yearbooks'),
                'z': I(self._vocab[BL]+'treaties'),
                '2': I(self._vocab[BL]+'offprints'),
                '5': I(self._vocab[BL]+'calendars'),
                '6': I(self._vocab[BL]+'comics-graphic-novels'),
            },
            ConferencePublication = {
                '1': I(self._vocab[BL]+'conference-publication'),
            },
            Festschrift = {
                '1': I(self._vocab[BL]+'festschrift'),
            },
            LiteraryForm = {
                '0': I(self._vocab[BL]+'not-fiction'),
                '1': I(self._vocab[BL]+'fiction'),
                'd': I(self._vocab[BL]+'dramas'),
                'e': I(self._vocab[BL]+'essays'),
                'f': I(self._vocab[BL]+'novels'),
                'h': I(self._vocab[BL]+'humor-satires-etc'),
                'i': I(self._vocab[BL]+'letters'),
                'j': I(self._vocab[BL]+'short-stories'),
                'm': I(self._vocab[BL]+'mixed-forms'),
                'p': I(self._vocab[BL]+'poetry'),
                's': I(self._vocab[BL]+'speeches'),
                'u': I(self._vocab[BL]+'unknown-literary-form'),
            },
        )

        self.Music = dict(
            FormOfComposition = {
                'an': I(self._vocab[BL]+'anthems'),
                'bd': I(self._vocab[BL]+'ballads'),
                'bg': I(self._vocab[BL]+'bluegrass-music'),
                'bl': I(self._vocab[BL]+'blues'),
                'bt': I(self._vocab[BL]+'ballets'),
                'ca': I(self._vocab[BL]+'chaconnes'),
                'cb': I(self._vocab[BL]+'chants-other-religions'),
                'cc': I(self._vocab[BL]+'chant-christian'),
                'cg': I(self._vocab[BL]+'concerti-grossi'),
                'ch': I(self._vocab[BL]+'chorales'),
                'cl': I(self._vocab[BL]+'chorale-preludes'),
                'cn': I(self._vocab[BL]+'canons-and-rounds'),
                'co': I(self._vocab[BL]+'concertos'),
                'cp': I(self._vocab[BL]+'chansons-polyphonic'),
                'cr': I(self._vocab[BL]+'carols'),
                'cs': I(self._vocab[BL]+'chance-compositions'),
                'ct': I(self._vocab[BL]+'cantatas'),
                'cy': I(self._vocab[BL]+'country-music'),
                'cz': I(self._vocab[BL]+'canzonas'),
                'df': I(self._vocab[BL]+'dance-forms'),
                'dv': I(self._vocab[BL]+'divertimentos-serenades-cassations-divertissements-and-noturni'),
                'fg': I(self._vocab[BL]+'fugues'),
                'fl': I(self._vocab[BL]+'flamenco'),
                'fm': I(self._vocab[BL]+'folk-music'),
                'ft': I(self._vocab[BL]+'fantasias'),
                'gm': I(self._vocab[BL]+'gospel-music'),
                'hy': I(self._vocab[BL]+'hymns'),
                'jz': I(self._vocab[BL]+'jazz'),
                'mc': I(self._vocab[BL]+'musical-revues-and-comedies'),
                'md': I(self._vocab[BL]+'madrigals'),
                'mi': I(self._vocab[BL]+'minuets'),
                'mo': I(self._vocab[BL]+'motets'),
                'mp': I(self._vocab[BL]+'motion-picture-music'),
                'mr': I(self._vocab[BL]+'marches'),
                'ms': I(self._vocab[BL]+'masses'),
                'mu': I(self._vocab[BL]+'multiple-forms'),
                'mz': I(self._vocab[BL]+'mazurkas'),
                'nc': I(self._vocab[BL]+'nocturnes'),
                'nn': I(self._vocab[BL]+'not-applicable'),
                'op': I(self._vocab[BL]+'operas'),
                'or': I(self._vocab[BL]+'oratorios'),
                'ov': I(self._vocab[BL]+'overtures'),
                'pg': I(self._vocab[BL]+'program-music'),
                'pm': I(self._vocab[BL]+'passion-music'),
                'po': I(self._vocab[BL]+'polonaises'),
                'pp': I(self._vocab[BL]+'popular-music'),
                'pr': I(self._vocab[BL]+'preludes'),
                'ps': I(self._vocab[BL]+'passacaglias'),
                'pt': I(self._vocab[BL]+'part-songs'),
                'pv': I(self._vocab[BL]+'pavans'),
                'rc': I(self._vocab[BL]+'rock-music'),
                'rd': I(self._vocab[BL]+'rondos'),
                'rg': I(self._vocab[BL]+'ragtime-music'),
                'ri': I(self._vocab[BL]+'ricercars'),
                'rp': I(self._vocab[BL]+'rhapsodies'),
                'rq': I(self._vocab[BL]+'requiems'),
                'sd': I(self._vocab[BL]+'square-dance-music'),
                'sg': I(self._vocab[BL]+'songs'),
                'sn': I(self._vocab[BL]+'sonatas'),
                'sp': I(self._vocab[BL]+'symphonic-poems'),
                'st': I(self._vocab[BL]+'studies-and-exercises'),
                'su': I(self._vocab[BL]+'suites'),
                'sy': I(self._vocab[BL]+'symphonies'),
                'tc': I(self._vocab[BL]+'toccatas'),
                'tl': I(self._vocab[BL]+'teatro-lirico'),
                'ts': I(self._vocab[BL]+'trio-sonatas'),
                'uu': I(self._vocab[BL]+'unknown-form-of-composition'),
                'vi': I(self._vocab[BL]+'villancicos'),
                'vr': I(self._vocab[BL]+'variations'),
                'wz': I(self._vocab[BL]+'waltzes'),
                'za': I(self._vocab[BL]+'zarzuelas'),
                'zz': I(self._vocab[BL]+'other-form-of-composition'),
            },
            FormatOfMusic = {
                'a': I(self._vocab[BL]+'full-score'),
                'b': I(self._vocab[BL]+'full-score-miniature-or-study-size'),
                'c': I(self._vocab[BL]+'accompaniment-reduced-for-keyboard'),
                'd': I(self._vocab[BL]+'voice-score-with-accompaniment-omitted'),
                'e': I(self._vocab[BL]+'condensed-score-or-piano-conductor-score'),
                'g': I(self._vocab[BL]+'close-score'),
                'h': I(self._vocab[BL]+'chorus-score'),
                'i': I(self._vocab[BL]+'condensed-score'),
                'j': I(self._vocab[BL]+'performer-conductor-part'),
                'k': I(self._vocab[BL]+'vocal-score'),
                'l': I(self._vocab[BL]+'score'),
                'm': I(self._vocab[BL]+'multiple-score-formats'),
                'n': I(self._vocab[BL]+'not-applicable'),
                'u': I(self._vocab[BL]+'unknown-music-format'),
                'z': I(self._vocab[BL]+'other-music-format'),
            },
            MusicParts = {
                'd': I(self._vocab[BL]+'instrumental-and-vocal-parts'),
                'e': I(self._vocab[BL]+'instrumental-parts'),
                'f': I(self._vocab[BL]+'vocal-parts'),
                'n': I(self._vocab[BL]+'not-applicable'),
                'u': I(self._vocab[BL]+'unknown-parts'),
            },
            AccompanyingMatter = {
                'a': I(self._vocab[BL]+'discography'),
                'b': I(self._vocab[BL]+'bibliography'),
                'c': I(self._vocab[BL]+'thematic-index'),
                'd': I(self._vocab[BL]+'libretto-or-text'),
                'e': I(self._vocab[BL]+'biography-of-composer-or-author'),
                'f': I(self._vocab[BL]+'biography-of-performer-or-history-of-ensemble'),
                'g': I(self._vocab[BL]+'technical-and-or-historical-information-on-instruments'),
                'h': I(self._vocab[BL]+'technical-information-on-music'),
                'i': I(self._vocab[BL]+'historical-information'),
                'k': I(self._vocab[BL]+'ethnological-information'),
                'r': I(self._vocab[BL]+'instructional-materials'),
                's': I(self._vocab[BL]+'music'),
                'z': I(self._vocab[BL]+'other-accompanying-matter'),
            },
            LiteraryTextForSoundRecordings = {
                'a': I(self._vocab[BL]+'autobiography'),
                'b': I(self._vocab[BL]+'biography'),
                'c': I(self._vocab[BL]+'conference-proceedings'),
                'd': I(self._vocab[BL]+'drama'),
                'e': I(self._vocab[BL]+'essays'),
                'f': I(self._vocab[BL]+'fiction'),
                'g': I(self._vocab[BL]+'reporting'),
                'h': I(self._vocab[BL]+'history'),
                'i': I(self._vocab[BL]+'instruction'),
                'j': I(self._vocab[BL]+'language-instruction'),
                'k': I(self._vocab[BL]+'comedy'),
                'l': I(self._vocab[BL]+'lectures-speeches'),
                'm': I(self._vocab[BL]+'memoirs'),
                'n': I(self._vocab[BL]+'not-applicable'),
                'o': I(self._vocab[BL]+'folktales'),
                'p': I(self._vocab[BL]+'poetry'),
                'r': I(self._vocab[BL]+'rehearsals'),
                's': I(self._vocab[BL]+'sounds'),
                't': I(self._vocab[BL]+'interviews'),
                'z': I(self._vocab[BL]+'other-literary-text-for-sound-recordings'),
            },
            TranspositionAndArrangement = {
                'a': I(self._vocab[BL]+'transposition'),
                'b': I(self._vocab[BL]+'arrangement'),
                'c': I(self._vocab[BL]+'both-transposed-and-arranged'),
                'n': I(self._vocab[BL]+'not-applicable-transposition-and-arrangement'),
                'u': I(self._vocab[BL]+'unknown-transposition-and-arrangement'),
            }
        )

        self.Maps = dict(
            Relief = {
                'a': I(self._vocab[BL]+'contours'),
                'b': I(self._vocab[BL]+'shading'),
                'c': I(self._vocab[BL]+'gradient-and-bathymetric-tints'),
                'd': I(self._vocab[BL]+'hachures'),
                'e': I(self._vocab[BL]+'bathymetry-soundings'),
                'f': I(self._vocab[BL]+'form-lines'),
                'g': I(self._vocab[BL]+'spot-heights'),
                'i': I(self._vocab[BL]+'pictorially'),
                'j': I(self._vocab[BL]+'land-forms'),
                'k': I(self._vocab[BL]+'bathymetry-isolines'),
                'm': I(self._vocab[BL]+'rock-drawings'),
                'z': I(self._vocab[BL]+'other-relief'),
            },
            Projection = {
                'aa': I(self._vocab[BL]+'aitoff'),
                'ab': I(self._vocab[BL]+'gnomic'),
                'ac': I(self._vocab[BL]+'lamberts-azimuthal-equal-area'),
                'ad': I(self._vocab[BL]+'orthographic'),
                'ae': I(self._vocab[BL]+'azimuthal-equidistant'),
                'af': I(self._vocab[BL]+'stereographic'),
                'ag': I(self._vocab[BL]+'general-vertical-near-sided'),
                'am': I(self._vocab[BL]+'modified-stereographic-for-alaska'),
                'an': I(self._vocab[BL]+'chamberlain-trimetric'),
                'ap': I(self._vocab[BL]+'polar-stereographic'),
                'au': I(self._vocab[BL]+'azimuthal-specific-type-unknown'),
                'az': I(self._vocab[BL]+'azimuthal-other'),
                'ba': I(self._vocab[BL]+'gall'),
                'bb': I(self._vocab[BL]+'goodes-homolographic'),
                'bc': I(self._vocab[BL]+'lamberts-cylindrical-equal-area'),
                'bd': I(self._vocab[BL]+'mercator'),
                'be': I(self._vocab[BL]+'miller'),
                'bf': I(self._vocab[BL]+'mollweide'),
                'bg': I(self._vocab[BL]+'sinusoidal'),
                'bh': I(self._vocab[BL]+'transverse-mercator'),
                'bi': I(self._vocab[BL]+'gauss-kruger'),
                'bj': I(self._vocab[BL]+'equirectangular'),
                'bk': I(self._vocab[BL]+'krovak'),
                'bl': I(self._vocab[BL]+'cassini-soldner'),
                'bo': I(self._vocab[BL]+'oblique-mercator'),
                'br': I(self._vocab[BL]+'robinson'),
                'bs': I(self._vocab[BL]+'space-oblique-mercator'),
                'bu': I(self._vocab[BL]+'cylindrical-specific-type-unknown'),
                'bz': I(self._vocab[BL]+'cylindrical-other'),
                'ca': I(self._vocab[BL]+'albers-equal-area'),
                'cb': I(self._vocab[BL]+'bonne'),
                'cc': I(self._vocab[BL]+'lamberts-conformal-conic'),
                'ce': I(self._vocab[BL]+'equidistant-conic'),
                'cp': I(self._vocab[BL]+'polyconic'),
                'cu': I(self._vocab[BL]+'conic-specific-type-unknown'),
                'cz': I(self._vocab[BL]+'conic-other'),
                'da': I(self._vocab[BL]+'armadillo'),
                'db': I(self._vocab[BL]+'butterfly'),
                'dc': I(self._vocab[BL]+'eckert'),
                'dd': I(self._vocab[BL]+'goodes-homolosine'),
                'de': I(self._vocab[BL]+'millers-bipolar-oblique-conformal-optic'),
                'df': I(self._vocab[BL]+'van-der-grinten'),
                'dg': I(self._vocab[BL]+'dimaxion'),
                'dh': I(self._vocab[BL]+'cordiform'),
                'dl': I(self._vocab[BL]+'lambert-conformal'),
                'zz': I(self._vocab[BL]+'other-projection'),
            },
            TypeOfCartographicMaterial = {
                'a': I(self._vocab[BL]+'single-map'),
                'b': I(self._vocab[BL]+'map-series'),
                'c': I(self._vocab[BL]+'map-serial'),
                'd': I(self._vocab[BL]+'globe'),
                'e': I(self._vocab[BL]+'atlas'),
                'f': I(self._vocab[BL]+'separate-supplement-to-another-work'),
                'g': I(self._vocab[BL]+'bound-as-part-of-another-work'),
                'u': I(self._vocab[BL]+'unknown-type-of-cartographic-material'),
                'z': I(self._vocab[BL]+'other-type-of-cartographic-material'),
            },
            SpecialFormatCharacteristics = {
                'e': I(self._vocab[BL]+'manuscript'),
                'j': I(self._vocab[BL]+'picture-card-post-card'),
                'k': I(self._vocab[BL]+'calendar'),
                'l': I(self._vocab[BL]+'puzzle'),
                'n': I(self._vocab[BL]+'game'),
                'o': I(self._vocab[BL]+'wall-map'),
                'p': I(self._vocab[BL]+'playing-cards'),
                'r': I(self._vocab[BL]+'loose-leaf'),
                'z': I(self._vocab[BL]+'other-special-format-characteristic'),
            },
        )

        self.VisualMaterials = dict(
            TypeOfVisualMaterial = {
                'a': I(self._vocab[BL]+'art-original'),
                'b': I(self._vocab[BL]+'kit'),
                'c': I(self._vocab[BL]+'art-reproduction'),
                'd': I(self._vocab[BL]+'diorama'),
                'f': I(self._vocab[BL]+'filmstrip'),
                'g': I(self._vocab[BL]+'game'),
                'i': I(self._vocab[BL]+'picture'),
                'k': I(self._vocab[BL]+'graphic'),
                'l': I(self._vocab[BL]+'technical-drawing'),
                'm': I(self._vocab[BL]+'motion-picture'),
                'n': I(self._vocab[BL]+'chart'),
                'o': I(self._vocab[BL]+'flash-card'),
                'p': I(self._vocab[BL]+'microscope-slide'),
                'q': I(self._vocab[BL]+'model'),
                'r': I(self._vocab[BL]+'realia'),
                's': I(self._vocab[BL]+'slide'),
                't': I(self._vocab[BL]+'transparency'),
                'v': I(self._vocab[BL]+'videorecording'),
                'w': I(self._vocab[BL]+'toy'),
                'z': I(self._vocab[BL]+'other-type-of-visual-material'),
            
            },
            Technique = {
                'a': I(self._vocab[BL]+'animation'),
                'c': I(self._vocab[BL]+'animation-and-live-action'),
                'l': I(self._vocab[BL]+'live-action'),
                'n': I(self._vocab[BL]+'not-applicable-technique'),
                'u': I(self._vocab[BL]+'unknown-technique'),
                'z': I(self._vocab[BL]+'other-technique'),
            }
        )

        self.ComputerFiles = dict( 
            FormOfItem = { # subset of FORM_OF_ITEM
                'o': I(self._vocab[BL]+'online'),
                'q': I(self._vocab[BL]+'direct-electronic'),
            },
            TypeOfComputerFile = {
                'a': I(self._vocab[BL]+'numeric-data'),
                'b': I(self._vocab[BL]+'computer-program'),
                'c': I(self._vocab[BL]+'representational'),
                'd': I(self._vocab[BL]+'document'),
                'e': I(self._vocab[BL]+'bibliographic-data'),
                'f': I(self._vocab[BL]+'font'),
                'g': I(self._vocab[BL]+'game'),
                'h': I(self._vocab[BL]+'sound'),
                'i': I(self._vocab[BL]+'interactive-multimedia'),
                'j': I(self._vocab[BL]+'online-system-or-service'),
                'm': I(self._vocab[BL]+'combination'),
                'u': I(self._vocab[BL]+'unknown-type-of-computer-file'),
                'z': I(self._vocab[BL]+'other-type-of-computer-file'),
            }
        )

        self.ContinuingResources = dict(
            Frequency = {
                'a': I(self._vocab[BL]+'annual'),
                'b': I(self._vocab[BL]+'bimonthly'),
                'c': I(self._vocab[BL]+'semiweekly'),
                'd': I(self._vocab[BL]+'daily'),
                'e': I(self._vocab[BL]+'biweekly'),
                'f': I(self._vocab[BL]+'semiannual'),
                'g': I(self._vocab[BL]+'biennial'),
                'h': I(self._vocab[BL]+'triennial'),
                'i': I(self._vocab[BL]+'three-times-a-week'),
                'j': I(self._vocab[BL]+'three-times-a-month'),
                'k': I(self._vocab[BL]+'continuously-updated'),
                'm': I(self._vocab[BL]+'monthly'),
                'q': I(self._vocab[BL]+'quarterly'),
                't': I(self._vocab[BL]+'three-times-a-year'),
                'u': I(self._vocab[BL]+'unknown-frequency'),
                'w': I(self._vocab[BL]+'weekly'),
                'z': I(self._vocab[BL]+'other-frequency'),
            },
            Regularity = {
                'n': I(self._vocab[BL]+'normalized-irregular'),
                'r': I(self._vocab[BL]+'regular'),
                'u': I(self._vocab[BL]+'unknown'),
                'x': I(self._vocab[BL]+'complete-irregular'),
            },
            TypeOfContinuingResource = {
                'd': I(self._vocab[BL]+'updating-database'),
                'l': I(self._vocab[BL]+'updating-loose-leaf'),
                'm': I(self._vocab[BL]+'monographic-series'),
                'n': I(self._vocab[BL]+'newspaper'),
                'p': I(self._vocab[BL]+'periodical'),
                'w': I(self._vocab[BL]+'updating-web-site'),
            },
            OriginalAlphabetOrScriptOfTitle = {
                'a': I(self._vocab[BL]+'basic-roman'),
                'b': I(self._vocab[BL]+'extended-roman'),
                'c': I(self._vocab[BL]+'cyrillic'),
                'd': I(self._vocab[BL]+'japanese'),
                'e': I(self._vocab[BL]+'chinese'),
                'f': I(self._vocab[BL]+'arabic'),
                'g': I(self._vocab[BL]+'greek'),
                'h': I(self._vocab[BL]+'hebrew'),
                'i': I(self._vocab[BL]+'thai'),
                'j': I(self._vocab[BL]+'devanagari'),
                'k': I(self._vocab[BL]+'korean'),
                'l': I(self._vocab[BL]+'tamil'),
                'u': I(self._vocab[BL]+'unknown-alphabet'),
                'z': I(self._vocab[BL]+'other-alphabet'),
            },
            EntryConvention = {
                '0': I(self._vocab[BL]+'successive-entry'),
                '1': I(self._vocab[BL]+'latest-entry'),
                '2': I(self._vocab[BL]+'integrated-entry'),
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

    def process_leader(self, leader, work, instance):
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
        >>> list(t.process_leader('03495cpcaa2200673 a 4500'))
        [(None, 'http://bibfra.me/purl/versa/type', I('Collection')), (None, 'http://bibfra.me/purl/versa/type', I('Multimedia')), (None, 'http://bibfra.me/purl/versa/type', I('Collection'))]
        """
        work_06 = dict(
            a=I(self._vocab[BL]+"LanguageMaterial"),
            c=(I(self._vocab[BL]+"LanguageMaterial"), I(self._vocab[BL]+"NotatedMusic")),
            d=(I(self._vocab[BL]+"LanguageMaterial"), I(self._vocab[BL]+"Manuscript"), I(self._vocab[BL]+"NotatedMusic")),
            e=(I(self._vocab[BL]+"StillImage"), I(self._vocab[BL]+"Cartography")),
            f=(I(self._vocab[BL]+"Manuscript"), I(self._vocab[BL]+"Cartography"), I(self._vocab[BL]+"StillImage")),
            g=I(self._vocab[BL]+"MovingImage"),
            i=(I(self._vocab[BL]+"Audio"), I(self._vocab[BL]+"Nonmusical"), I(self._vocab[BL]+"Sounds")),
            j=(I(self._vocab[BL]+"Audio"), I(self._vocab[BL]+"Musical")),
            k=I(self._vocab[BL]+"StillImage"),
            m=(I(self._vocab[BL]+"Multimedia"), I(self._vocab[BL]+"Software")),
            o=I(self._vocab[BL]+"Kit"),
            p=(I(self._vocab[BL]+"Collection"), I(self._vocab[BL]+"Multimedia")),
            r=I(self._vocab[BL]+"ThreeDimensionalObject"),
            t=(I(self._vocab[BL]+"LanguageMaterial"), I(self._vocab[BL]+"Manuscript"))
            )

        instance_06 = dict(
            )

        _06 = leader[6]
        if _06 in work_06.keys():
            yield work, I(self._vocab[VTYPE]), work_06[_06]
        if _06 in instance_06.keys():
            yield instance, I(self._vocab[VTYPE]), instance_06[_06]
        if leader[7] in ('c', 's'):
            yield None, I(self._vocab[VTYPE]), I(self._vocab[BL]+"Collection")

    def _process_fixed_length(self, info, leader, offset, work, instance):
        """
        Processes 008 and 006 control fields containing fixed length data elements,
        according to the MARC standard http://www.loc.gov/marc/umb/um07to10.html#part9

        :info: - text of 008 or a single 006 field, a character array
        :work: - work resource in context of which 008 is being processed. Useful in the return value.
        :instance: - instance resource in context of which leader is being processed. Useful in the return value.
        :offset: - byte offset into 'info' containing germane data. 18 for 008, 0 for 006

        yields - 0 or more 3-tuples, (origin, rel, target), each representing a new
            link generated from 008 data. origin is almost always the work or instance
            resource passed in. If origin is None, signal to the caller to default
            to the work as origin


        #>>> from bibframe.reader.marcextra import transforms
        #>>> t = transforms()
        #>>> list(t.process_008('790726||||||||||||                 eng  '))
        #[('date', '1979-07-26')]
        """

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
                (0, 1, 2, 3): lambda i: (None, I(self._vocab[VTYPE]), self.Books['Illustrations'].get(info[i])),
                4: lambda i: (None, I(self._vocab[BL]+'target-audience'), SLUG(self.AUDIENCE.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[BL]+'form-of-item'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                (6, 7, 8, 9): lambda i: (None, I(self._vocab[VTYPE]), self.Books['NatureOfContents'].get(info[i])),
                10: lambda i: (None, I(self._vocab[VTYPE]), self.GOVT_PUBLICATION.get(info[i])),
                11: lambda i: (None, I(self._vocab[VTYPE]), self.Books['ConferencePublication'].get(info[i])),
                12: lambda i: (None, I(self._vocab[VTYPE]), self.Books['Festschrift'].get(info[i])),
                13: lambda i: (None, I(self._vocab[BL]+'index'), self.INDEX.get(info[i])),
                15: lambda i: (None, I(self._vocab[VTYPE]), self.Books['LiteraryForm'].get(info[i])),
                16: lambda i: (None, I(self._vocab[VTYPE]), self.BIOGRAPHICAL.get(info[i])),
            },
            Music = {
                ('slice', 0, 2): lambda i: (None, I(self._vocab[VTYPE]), self.Music['FormOfComposition'].get(info[i])),
                2: lambda i: (None, I(self._vocab[VTYPE]), self.Music['FormatOfMusic'].get(info[i])),
                3: lambda i: (None, I(self._vocab[VTYPE]), self.Music['MusicParts'].get(info[i])),
                4: lambda i: (None, I(self._vocab[BL]+'target-audience'), SLUG(self.AUDIENCE.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[BL]+'form-of-item'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                (6, 7, 8, 9, 10, 11): lambda i: (None, I(self._vocab[VTYPE]), self.Music['AccompanyingMatter'].get(info[i])),
                (12, 13): lambda i: (None, I(self._vocab[VTYPE]), self.Music['LiteraryTextForSoundsRecordings'].get(info[i])),
                15: lambda i: (None, I(self._vocab[VTYPE]), self.Music['TranspositionAndArrangement'].get(info[i])),
            },
            Maps = {
                (0, 1, 2, 3): lambda i: (None, I(self._vocab[VTYPE]), self.Maps['Relief'].get(info[i])),
                ('slice', 4, 5): lambda i: (None, I(self._vocab[VTYPE]), self.Maps['Projection'].get(info[i])),
                7: lambda i: (None, I(self._vocab[VTYPE]), self.Maps['TypeOfCartographicMaterial'].get(info[i])),
                10: lambda i: (None, I(self._vocab[VTYPE]), self.GOVT_PUBLICATION.get(info[i])),
                11: lambda i: (instance, I(self._vocab[BL]+'form-of-item'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                13: lambda i: (None, I(self._vocab[VTYPE]), self.INDEX.get(info[i])),
                (15, 16): lambda i: (None, I(self._vocab[VTYPE]), self.Maps['SpecialFormatCharacteristics'].get(info[i])),
            },
            VisualMaterials = {
                ('slice', 0, 2): lambda i: (None, I(self._vocab[BL]+'runtime'), runtime(info[i])),
                4: lambda i: (None, I(self._vocab[BL]+'target-audience'), SLUG(self.AUDIENCE.get(info[i]))),
                10: lambda i: (None, I(self._vocab[VTYPE]), self.GOVT_PUBLICATION.get(info[i])),
                11: lambda i: (instance, I(self._vocab[BL]+'form-of-item'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                15: lambda i: (instance, I(self._vocab[VTYPE]), self.VisualMaterials['TypeOfVisualMaterial'].get(info[i])),
                16: lambda i: (None, I(self._vocab[BL]+'technique'), SLUG(self.VisualMaterials['Technique'].get(info[i]))),
            },
            ComputerFiles = {
                4: lambda i: (None, I(self._vocab[BL]+'target-audience'), SLUG(self.AUDIENCE.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[BL]+'form-of-item'), SLUG(self.ComputerFiles['FormOfItem'].get(info[i]))),
                8: lambda i: (None, I(self._vocab[VTYPE]), self.ComputerFiles['TypeOfComputerFile'].get(info[i])),
                10: lambda i: (None, I(self._vocab[VTYPE]), self.GOVT_PUBLICATION.get(info[i])),
            },
            MixedMaterials = {
                5: lambda i: (None, I(self._vocab[VTYPE]), self.FORM_OF_ITEM.get(info[i])),
            },
            #ContinuingResources = {
            #}
        )

        # build new patterns from existing patterns by byte shifting, i.e. 18 bytes for 006->008
        def shift_patterns(patterns, offset):
            from pprint import pprint
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
                print("unknown leader6/7", _06, _07)
       
        patterns = PATTERNS.get(typ)
        if patterns:
            if offset:
                patterns = shift_patterns(patterns, offset)

            yield from process_patterns(patterns)

    def process_008(self, info, leader, work, instance):

        #info = field008
        #ARE YOU FRIGGING KIDDING ME?! MARC/008 is NON-Y2K SAFE?!
        year = info[0:2]
        try:
            century = '19' if int(year) > 30 else '20' #I guess we can give an 18 year berth before this breaks ;)
            # remove date_008 from data export at this time
            # yield 'date_008', '{}{}-{}-{}'.format(century, year, info[2:4], info[4:6])
        except ValueError:
            #Completely Invalid date
            pass

        yield from self._process_fixed_length(info, leader, 18, work, instance)

    def process_006(self, infos, leader, work, instance):
        for info in infos:
            yield from self._process_fixed_length(info, leader, 0, work, instance)

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
