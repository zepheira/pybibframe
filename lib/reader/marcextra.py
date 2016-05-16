'''
Treatment of certain special MARC fields, leader, 006, 007, 008, etc.
'''

from versa import I, VERSA_BASEIRI
from amara3.iri import is_absolute
from bibframe import BL, BA, REL, MARC, RBMS, AV

BL = 'http://bibfra.me/vocab/lite/'

#TODO: Also split on multiple 260 fields

VTYPE = VERSA_BASEIRI+'type'
LANG= BL+'language'
DEFAULT_VOCAB_ITEMS = [BL, BA, REL, MARC, RBMS, AV, LANG, VTYPE]

# Though most MARC lookups below result in URI, for now we only want to treat
# them as text, hence SLUG. This could change in the future, so we keep the URI
# around for that purpose. Those that are already text literals are so because
# of the awkwardness of conversion to URI form
def SLUG(s):
    if not s: return None

    if is_absolute(s): # URI
        return s.rsplit('/')[-1].replace('-',' ')
    else:
        return s

def marc_date_yymmdd(d): # used in 008
    #ARE YOU FRIGGING KIDDING ME?! MARC/008 is NON-Y2K SAFE?!
    d = d.ljust(6)

    date = None
    year = d[0:2]
    try:
        century = '19' if int(year) > 30 else '20' #I guess we can give an 18 year berth before this breaks ;)
        date = '{}{}-{}-{}'.format(century, year, d[2:4], d[4:6])
    except ValueError:
        #Completely Invalid date
        pass

    return date

def marc_date_yyyymm(d): # used in 007
    d = d.ljust(6)

    year = d[0:4]
    month = None
    try:
        month = int(d[4:6])
    except ValueError:
        #month is unknown
        pass

    date = '{}-{:0>2}'.format(year, month) if month else year

    return date

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
            "z": I(self._vocab[MARC]+"other")}

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
            "u": I(self._vocab[MARC]+'unknown')
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
                'uu': I(self._vocab[MARC]+'unknown'),
                'vi': I(self._vocab[MARC]+'villancicos'),
                'vr': I(self._vocab[MARC]+'variations'),
                'wz': I(self._vocab[MARC]+'waltzes'),
                'za': I(self._vocab[MARC]+'zarzuelas'),
                'zz': I(self._vocab[MARC]+'other'),
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
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            MusicParts = {
                'd': I(self._vocab[MARC]+'instrumental-and-vocal-parts'),
                'e': I(self._vocab[MARC]+'instrumental-parts'),
                'f': I(self._vocab[MARC]+'vocal-parts'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
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
                'z': I(self._vocab[MARC]+'other'),
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
                'z': I(self._vocab[MARC]+'other'),
            },
            TranspositionAndArrangement = {
                'a': I(self._vocab[MARC]+'transposition'),
                'b': I(self._vocab[MARC]+'arrangement'),
                'c': I(self._vocab[MARC]+'both-transposed-and-arranged'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
            }
        )

        self.Maps = dict( #006/008
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
                'z': I(self._vocab[MARC]+'other'),
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
                'zz': I(self._vocab[MARC]+'other'),
            },
            TypeOfCartographicMaterial = {
                'a': I(self._vocab[MARC]+'single-map'),
                'b': I(self._vocab[MARC]+'map-series'),
                'c': I(self._vocab[MARC]+'map-serial'),
                'd': I(self._vocab[MARC]+'globe'),
                'e': I(self._vocab[MARC]+'atlas'),
                'f': I(self._vocab[MARC]+'separate-supplement-to-another-work'),
                'g': I(self._vocab[MARC]+'bound-as-part-of-another-work'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
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
                'z': I(self._vocab[MARC]+'other'),
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
                'z': I(self._vocab[MARC]+'other'),

            },
            Technique = {
                'a': I(self._vocab[MARC]+'animation'),
                'c': I(self._vocab[MARC]+'animation-and-live-action'),
                'l': I(self._vocab[MARC]+'live-action'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
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
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
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
                'u': I(self._vocab[MARC]+'unknown'),
                'w': I(self._vocab[MARC]+'weekly'),
                'z': I(self._vocab[MARC]+'other'),
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
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
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

        # the following are for 007
        self.COLOR = {
            'a': I(self._vocab[MARC]+'one-color'),
            'b': I(self._vocab[MARC]+'black-and-white'),
            'c': I(self._vocab[MARC]+'multicolored'),
            'h': I(self._vocab[MARC]+'hand-colored'),
            'm': I(self._vocab[MARC]+'mixed'),
            'n': I(self._vocab[MARC]+'not-applicable'),
            'z': I(self._vocab[MARC]+'other'),
        }

        self.PHYSICAL_MEDIUM = {
            'a': I(self._vocab[MARC]+'paper'),
            'b': I(self._vocab[MARC]+'wood'),
            'c': I(self._vocab[MARC]+'stone'),
            'd': I(self._vocab[MARC]+'metal'),
            'e': I(self._vocab[MARC]+'synthetic'),
            'f': I(self._vocab[MARC]+'skin'),
            'g': I(self._vocab[MARC]+'textiles'),
            'i': I(self._vocab[MARC]+'plastic'),
            'j': I(self._vocab[MARC]+'glass'),
            'l': I(self._vocab[MARC]+'vinyl'),
            'n': I(self._vocab[MARC]+'vellum'),
            'p': I(self._vocab[MARC]+'plaster'),
            'q': I(self._vocab[MARC]+'flexible-base-photographic-positive'),
            'r': I(self._vocab[MARC]+'flexible-base-photographic-negative'),
            's': I(self._vocab[MARC]+'non-flexible-base-photographic-positive'),
            't': I(self._vocab[MARC]+'non-flexible-base-photographic-negative'),
            'u': I(self._vocab[MARC]+'unknown'),
            'v': I(self._vocab[MARC]+'leather'),
            'w': I(self._vocab[MARC]+'parchment'),
            'y': I(self._vocab[MARC]+'other-photographic-medium'),
            'z': I(self._vocab[MARC]+'other'),
        }

        self.TYPE_OF_REPRODUCTION = {
            'f': I(self._vocab[MARC]+'facsimile'),
            'n': I(self._vocab[MARC]+'not-applicable'),
            'u': I(self._vocab[MARC]+'unknown'),
            'z': I(self._vocab[MARC]+'other'),
        }

        self.PRODUCTION_REPRODUCTION_DETAILS = {
            'a': I(self._vocab[MARC]+'photocopy-blueline-print'),
            'b': I(self._vocab[MARC]+'photocopy'),
            'c': I(self._vocab[MARC]+'pre-production'),
            'd': I(self._vocab[MARC]+'film'),
            'u': I(self._vocab[MARC]+'unknown'),
            'z': I(self._vocab[MARC]+'other'),
        }

        self.POSITIVE_NEGATIVE_ASPECT = {
            'a': I(self._vocab[MARC]+'positive'),
            'b': I(self._vocab[MARC]+'negative'),
            'm': I(self._vocab[MARC]+'mixed-polarity'),
            'n': I(self._vocab[MARC]+'not-applicable'),
        }

        self.SUPPORT_MATERIAL = {
            'a': I(self._vocab[MARC]+'canvas'),
            'b': I(self._vocab[MARC]+'bristol-board'),
            'c': I(self._vocab[MARC]+'cardboard'),
            'd': I(self._vocab[MARC]+'glass'),
            'e': I(self._vocab[MARC]+'synthetic'),
            'f': I(self._vocab[MARC]+'skin'),
            'g': I(self._vocab[MARC]+'textile'),
            'h': I(self._vocab[MARC]+'metal'),
            'i': I(self._vocab[MARC]+'plastic'),
            'j': I(self._vocab[MARC]+'metal-and-glass'),
            'k': I(self._vocab[MARC]+'synthetic-and-glass'),
            'l': I(self._vocab[MARC]+'vinyl'),
            'm': I(self._vocab[MARC]+'mixed-collection'),
            'n': I(self._vocab[MARC]+'vellum'),
            'o': I(self._vocab[MARC]+'paper'),
            'p': I(self._vocab[MARC]+'plaster'),
            'q': I(self._vocab[MARC]+'hardboard'),
            'r': I(self._vocab[MARC]+'porcelain'),
            's': I(self._vocab[MARC]+'stone'),
            't': I(self._vocab[MARC]+'wood'),
            'u': I(self._vocab[MARC]+'unknown'),
            'v': I(self._vocab[MARC]+'leather'),
            'w': I(self._vocab[MARC]+'parchment'),
            'z': I(self._vocab[MARC]+'other'),
        }

        self.SOUND_ON_MEDIUM_OR_SEPARATE = {
            'a': I(self._vocab[MARC]+'sound-on-medium'),
            'b': I(self._vocab[MARC]+'sound-separate-from-medium'),
            'u': I(self._vocab[MARC]+'unknown'),
        }

        self.MEDIUM_FOR_SOUND = {
            'a': I(self._vocab[MARC]+'optical-sound-track-on-motion-picture-film'),
            'b': I(self._vocab[MARC]+'magnetic-sound-track-on-motion-picture-film'),
            'c': I(self._vocab[MARC]+'magnetic-audio-tape-in-cartridge'),
            'd': I(self._vocab[MARC]+'sound-disc'),
            'e': I(self._vocab[MARC]+'magnetic-audio-tape-on-reel'),
            'f': I(self._vocab[MARC]+'magnetic-audio-tape-in-cassette'),
            'g': I(self._vocab[MARC]+'optical-and-magnetic-sound-track-on-motion-picture-film'),
            'h': I(self._vocab[MARC]+'videotape'),
            'i': I(self._vocab[MARC]+'videodisc'),
            'n': I(self._vocab[MARC]+'not-applicable'),
            'u': I(self._vocab[MARC]+'unknown'),
            'z': I(self._vocab[MARC]+'other'),
        }

        # Motion pictures use a subset of this but we reuse it anyway
        self.DIMENSIONS_FILM = {
            'a': 'standard 8mm. film width',
            'b': 'super 8mm./single 8mm. film width',
            'c': '9.5mm. film width',
            'd': '16mm. film width',
            'e': '28mm. film width',
            'f': '35mm. film width',
            'g': '70mm. film width',
            'j': '2x2 in. or 5x5 cm. slide',
            'k': '2 1/4 x 2 1/4 in. or 6x6 cm. slide',
            's': '4x5 in. or 10x13 cm. transparency',
            't': '5x7 in. or 13x18 cm. transparency',
            'v': '8x10 in. or 21x26 cm. transparency',
            'w': '9x9 in. or 23x23 cm. transparency',
            'x': '10x10 in. or 26x26 cm. transparency',
            'y': '7x7 in. or 18x18 cm. transparency',
            'u': I(self._vocab[MARC]+'unknown'),
            'z': I(self._vocab[MARC]+'other'),
        }

        self.BASE_OF_FILM = {
            'a': I(self._vocab[MARC]+'safety-base-undetermined'),
            'c': I(self._vocab[MARC]+'safety-base-acetate-undetermined'),
            'd': I(self._vocab[MARC]+'safety-base-diacetate'),
            'i': I(self._vocab[MARC]+'nitrate-base'),
            'm': I(self._vocab[MARC]+'mixed-base-nitrate-and-safety'),
            'n': I(self._vocab[MARC]+'not-applicable'),
            'p': I(self._vocab[MARC]+'safety-base-polyester'),
            'r': I(self._vocab[MARC]+'safety-base-mixed'),
            't': I(self._vocab[MARC]+'safety-base-triacetate'),
            'u': I(self._vocab[MARC]+'unknown'),
            'z': I(self._vocab[MARC]+'other'),
        }

        self.CONFIGURATION_OF_PLAYBACK_CHANNELS = {
            'k': I(self._vocab[MARC]+'mixed'),
            'm': I(self._vocab[MARC]+'monaural'),
            'n': I(self._vocab[MARC]+'not-applicable'),
            'q': I(self._vocab[MARC]+'quadrophonic-multichannel-or-surround'),
            's': I(self._vocab[MARC]+'stereophonic'),
            'u': I(self._vocab[MARC]+'unknown'),
            'z': I(self._vocab[MARC]+'other'),
        }

        self.Map = dict( #007
            SpecificMaterialDesignation = {
                'd': I(self._vocab[MARC]+'atlas'),
                'g': I(self._vocab[MARC]+'diagram'),
                'j': I(self._vocab[MARC]+'map'),
                'k': I(self._vocab[MARC]+'profile'),
                'q': I(self._vocab[MARC]+'model'),
                'r': I(self._vocab[MARC]+'remote-sensing-image'),
                's': I(self._vocab[MARC]+'section'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'y': I(self._vocab[MARC]+'view'),
                'z': I(self._vocab[MARC]+'other'),
            },

        )

        self.ElectronicResource = dict(
            SpecificMaterialDesignation = {
                'a': I(self._vocab[MARC]+'tape-cartridge'),
                'b': I(self._vocab[MARC]+'chip-cartridge'),
                'c': I(self._vocab[MARC]+'computer-optical-disc-cartridge'),
                'd': I(self._vocab[MARC]+'computer-disc-type-unspecified'),
                'e': I(self._vocab[MARC]+'computer-disc-cartridge-type-unspecified'),
                'f': I(self._vocab[MARC]+'tape-cassette'),
                'h': I(self._vocab[MARC]+'tape-reel'),
                'j': I(self._vocab[MARC]+'magnetic-disk'),
                'k': I(self._vocab[MARC]+'computer-card'),
                'm': I(self._vocab[MARC]+'magneto-optical-disk'),
                'o': I(self._vocab[MARC]+'optical-disk'),
                'r': I(self._vocab[MARC]+'remote'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
            Dimensions = { # forced literals for coding-sensitive info
                'a': '3 1/2 in.',
                'e': '12 in.',
                'g': '4 3/4 in. or 12 cm.',
                'a': '1 1/8 x 2 3/8 in.',
                'j': '3 7/8 x 2 1/2 in.',
                'n': I(self._vocab[MARC]+'not-applicable'),
                'o': "5 1/4 in.",
                'n': I(self._vocab[MARC]+'unknown'),
                'v': "8 in.",
                'u': I(self._vocab[MARC]+'other'),
            },
            Sound = {
                #'#': I(self._vocab[MARC]+'no-sound'), # presumably equivalent to absence of a/u/|
                'a': I(self._vocab[MARC]+'sound'),
                'u': I(self._vocab[MARC]+'unknown-sound'),
            },
            FileFormats = {
                'a': I(self._vocab[MARC]+'one-file-format'),
                'm': I(self._vocab[MARC]+'multiple-file-formats'),
                'u': I(self._vocab[MARC]+'unknown'),
            },
            QualityAssuranceTargets = {
                'a': I(self._vocab[MARC]+'absent'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'p': I(self._vocab[MARC]+'present'),
                'u': I(self._vocab[MARC]+'unknown'),
            },
            AntecedentSource = {
                'a': I(self._vocab[MARC]+'file-reproduced-from-original'),
                'b': I(self._vocab[MARC]+'file-reproduced-from-microform'),
                'c': I(self._vocab[MARC]+'file-reproduced-from-an-electronic-resource'),
                'd': I(self._vocab[MARC]+'file-reproduced-from-an-intermediate-not-microform'),
                'm': I(self._vocab[MARC]+'mixed'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
            },
            LevelOfCompression = {
                'a': I(self._vocab[MARC]+'uncompressed'),
                'b': I(self._vocab[MARC]+'lossless'),
                'd': I(self._vocab[MARC]+'lossy'),
                'm': I(self._vocab[MARC]+'mixed'),
                'u': I(self._vocab[MARC]+'unknown'),
            },
            ReformattingQuality = {
                'a': I(self._vocab[MARC]+'access'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'p': I(self._vocab[MARC]+'preservation'),
                'r': I(self._vocab[MARC]+'replacement'),
                'u': I(self._vocab[MARC]+'unknown'),
            }
        )

        self.Globe = dict(
            SpecificMaterialDesignation = {
                'a': I(self._vocab[MARC]+'celestial-globe'),
                'b': I(self._vocab[MARC]+'planetary-or-lunar-globe'),
                'c': I(self._vocab[MARC]+'terrestrial-globe'),
                'e': I(self._vocab[MARC]+'earth-moon-globe'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
        )

        self.TactileMaterial = dict(
            SpecificMaterialDesignation = {
                'a': I(self._vocab[MARC]+'moon'),
                'b': I(self._vocab[MARC]+'braille'),
                'c': I(self._vocab[MARC]+'combination'),
                'd': I(self._vocab[MARC]+'tactile-with-no-writing-system'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
            ClassOfBrailleWriting = {
                'a': I(self._vocab[MARC]+'literary-braille'),
                'b': I(self._vocab[MARC]+'format-code-braille'),
                'c': I(self._vocab[MARC]+'mathematics-and-scientific-braille'),
                'd': I(self._vocab[MARC]+'computer-braille'),
                'e': I(self._vocab[MARC]+'music-braille'),
                'm': I(self._vocab[MARC]+'multiple-braille-types'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            LevelOfContraction = {
                'a': I(self._vocab[MARC]+'uncontracted'),
                'b': I(self._vocab[MARC]+'contracted'),
                'm': I(self._vocab[MARC]+'combination'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            BrailleMusicFormat = {
                'a': I(self._vocab[MARC]+'bar-over-bar'),
                'b': I(self._vocab[MARC]+'bar-by-bar'),
                'c': I(self._vocab[MARC]+'line-over-line'),
                'd': I(self._vocab[MARC]+'paragraph'),
                'e': I(self._vocab[MARC]+'single-line'),
                'f': I(self._vocab[MARC]+'section-by-section'),
                'g': I(self._vocab[MARC]+'line-by-line'),
                'h': I(self._vocab[MARC]+'open-score'),
                'i': I(self._vocab[MARC]+'spanner-short-form-scoring'),
                'j': I(self._vocab[MARC]+'short-form-scoring'),
                'k': I(self._vocab[MARC]+'outline'),
                'l': I(self._vocab[MARC]+'vertical-score'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            SpecialPhysicalCharacteristics = {
                'a': I(self._vocab[MARC]+'print-braille'),
                'b': I(self._vocab[MARC]+'jumbo-or-enlarged-braille'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            }
        )

        self.ProjectedGraphic = dict(
            SpecificMaterialDesignation = {
                'c': I(self._vocab[MARC]+'filmstrip-cartridge'),
                'd': I(self._vocab[MARC]+'filmslip'),
                'f': I(self._vocab[MARC]+'fimlstrip-type-unspecified'),
                'o': I(self._vocab[MARC]+'filmstrip-roll'),
                's': I(self._vocab[MARC]+'slide'),
                't': I(self._vocab[MARC]+'transparency'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
            BaseOfEmulsion = {
                'd': I(self._vocab[MARC]+'glass'),
                'e': I(self._vocab[MARC]+'synthetic'),
                'j': I(self._vocab[MARC]+'safety-film'),
                'k': I(self._vocab[MARC]+'film-base-other-than-safety-film'),
                'm': I(self._vocab[MARC]+'mixed-collection'),
                'o': I(self._vocab[MARC]+'paper'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            SecondarySupportMaterial = {
                'c': I(self._vocab[MARC]+'cardboard'),
                'd': I(self._vocab[MARC]+'glass'),
                'e': I(self._vocab[MARC]+'synthetic'),
                'h': I(self._vocab[MARC]+'metal'),
                'j': I(self._vocab[MARC]+'metal-and-glass'),
                'k': I(self._vocab[MARC]+'synthetic-and-glass'),
                'm': I(self._vocab[MARC]+'mixed-collection'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            }
        )

        self.Microform = dict(
            SpecificMaterialDesignation = {
                'a': I(self._vocab[MARC]+'aperture-card'),
                'b': I(self._vocab[MARC]+'microfilm-cartridge'),
                'c': I(self._vocab[MARC]+'microfilm-cassette'),
                'd': I(self._vocab[MARC]+'microfilm-reel'),
                'e': I(self._vocab[MARC]+'microfiche'),
                'f': I(self._vocab[MARC]+'microfiche-cassette'),
                'g': I(self._vocab[MARC]+'microopaque'),
                'h': I(self._vocab[MARC]+'microfilm-slip'),
                'j': I(self._vocab[MARC]+'microfilm-roll'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
            Dimensions = {
                'a': '8mm.',
                'd': '16mm.',
                'f': '35mm.',
                'g': '70mm.',
                'h': '105mm.',
                'l': '3x5 in. or 8x13 cm.',
                'm': '4x6 in. or 11x15 cm.',
                'o': '6x9 in. or 16x23 cm.',
                'p': '3 1/4 x 7 3/8 in. or 9x19 cm.',
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            ReductionRatioRange = {
                'a': I(self._vocab[MARC]+'low-reduction-ratio'),
                'b': I(self._vocab[MARC]+'normal-reduction'),
                'c': I(self._vocab[MARC]+'high-reduction'),
                'd': I(self._vocab[MARC]+'very-high-reduction'),
                'e': I(self._vocab[MARC]+'ultra-high-reduction'),
                'u': I(self._vocab[MARC]+'unknown'),
                'v': I(self._vocab[MARC]+'reduction-rate-varies'),
            },
            EmulsionOnFilm = {
                'a': I(self._vocab[MARC]+'silver-halide'),
                'b': I(self._vocab[MARC]+'diazo'),
                'c': I(self._vocab[MARC]+'vesicular'),
                'm': I(self._vocab[MARC]+'mixed-emulsion'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            Generation = {
                'a': I(self._vocab[MARC]+'first-generation-master'),
                'b': I(self._vocab[MARC]+'printing-master'),
                'c': I(self._vocab[MARC]+'service-copy'),
                'm': I(self._vocab[MARC]+'mixed-generation'),
                'u': I(self._vocab[MARC]+'unknown'),
            },
        )

        self.NonprojectedGraphic = dict(
            SpecificMaterialDesignation = {
                'a': I(self._vocab[MARC]+'activity-card'),
                'c': I(self._vocab[MARC]+'collage'),
                'd': I(self._vocab[MARC]+'drawing'),
                'e': I(self._vocab[MARC]+'painting'),
                'f': I(self._vocab[MARC]+'photomechanical-print'),
                'g': I(self._vocab[MARC]+'photonegative'),
                'h': I(self._vocab[MARC]+'photoprint'),
                'i': I(self._vocab[MARC]+'picture'),
                'j': I(self._vocab[MARC]+'print'),
                'k': I(self._vocab[MARC]+'poster'),
                'l': I(self._vocab[MARC]+'technical-drawing'),
                'n': I(self._vocab[MARC]+'chart'),
                'o': I(self._vocab[MARC]+'flash-card'),
                'p': I(self._vocab[MARC]+'postcard'),
                'q': I(self._vocab[MARC]+'icon'),
                'r': I(self._vocab[MARC]+'radiograph'),
                's': I(self._vocab[MARC]+'study-print'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'v': I(self._vocab[MARC]+'photograph-type-unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
        )

        self.MotionPicture = dict(
            SpecificMaterialDesignation = {
                'c': I(self._vocab[MARC]+'film-cartridge'),
                'f': I(self._vocab[MARC]+'film-cassette'),
                'o': I(self._vocab[MARC]+'film-roll'),
                'r': I(self._vocab[MARC]+'film-reel'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
            MotionPicturePresentationFormat = {
                'a': I(self._vocab[MARC]+'standard-sound-aperture-reduced-frame'),
                'b': I(self._vocab[MARC]+'nonamorphic'),
                'c': I(self._vocab[MARC]+'3d'),
                'd': I(self._vocab[MARC]+'anomorphic-wide-screen'),
                'e': I(self._vocab[MARC]+'other-wide-screen-format'),
                'f': I(self._vocab[MARC]+'standard-silent-aperture-full-frame'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            ProductionElements = {
                'a': I(self._vocab[MARC]+'workprint'),
                'b': I(self._vocab[MARC]+'trims'),
                'c': I(self._vocab[MARC]+'outtakes'),
                'd': I(self._vocab[MARC]+'rushes'),
                'e': I(self._vocab[MARC]+'mixing-tracks'),
                'f': I(self._vocab[MARC]+'title-bands-inter-title-rolls'),
                'g': I(self._vocab[MARC]+'production-rolls'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'z': I(self._vocab[MARC]+'other'),
            },
            Generation = {
                'd': I(self._vocab[MARC]+'duplicate'),
                'e': I(self._vocab[MARC]+'master'),
                'o': I(self._vocab[MARC]+'original'),
                'r': I(self._vocab[MARC]+'reference-print-viewing-copy'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            RefinedCategoriesOfColor = {
                'a': I(self._vocab[MARC]+'3-layer-color'),
                'b': I(self._vocab[MARC]+'2-color-single-strip'),
                'c': I(self._vocab[MARC]+'undetermined-2-color'),
                'd': I(self._vocab[MARC]+'undetermined-3-color'),
                'e': I(self._vocab[MARC]+'3-strip-color'),
                'f': I(self._vocab[MARC]+'2-strip-color'),
                'g': I(self._vocab[MARC]+'red-strip'),
                'h': I(self._vocab[MARC]+'blue-or-green-strip'),
                'i': I(self._vocab[MARC]+'cyan-strip'),
                'j': I(self._vocab[MARC]+'magenta-strip'),
                'k': I(self._vocab[MARC]+'yellow-strip'),
                'l': I(self._vocab[MARC]+'s-e-n-2'),
                'm': I(self._vocab[MARC]+'s-e-n-3'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'p': I(self._vocab[MARC]+'sepia-tone'),
                'q': I(self._vocab[MARC]+'other-tone'),
                'r': I(self._vocab[MARC]+'tint'),
                's': I(self._vocab[MARC]+'tined-and-toned'),
                't': I(self._vocab[MARC]+'stencil-color'),
                'u': I(self._vocab[MARC]+'unknown'),
                'v': I(self._vocab[MARC]+'hand-colored'),
                'z': I(self._vocab[MARC]+'other'),
            },
            KindOfColorStockOrPrint = {
                'a': I(self._vocab[MARC]+'imbibition-dye-transfer-prints'),
                'b': I(self._vocab[MARC]+'three-layer-stock'),
                'c': I(self._vocab[MARC]+'three-layer-stock-low-fade'),
                'd': I(self._vocab[MARC]+'duplitized-stock'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            DeteriorationStage = {
                'a': I(self._vocab[MARC]+'none-apparent'),
                'b': I(self._vocab[MARC]+'nitrate-suspicious-odor'),
                'c': I(self._vocab[MARC]+'nitrate-pungent-odor'),
                'd': I(self._vocab[MARC]+'nitrade-brownish-discoloration-fading-dusty'),
                'e': I(self._vocab[MARC]+'nitrate-sticky'),
                'f': I(self._vocab[MARC]+'nitrate-frothy-bubbles-blisters'),
                'g': I(self._vocab[MARC]+'nitrate-congealed'),
                'h': I(self._vocab[MARC]+'nitrate-powder'),
                'k': I(self._vocab[MARC]+'non-nitrate-detectable-deterioration'),
                'l': I(self._vocab[MARC]+'non-nitrate-advanced-deterioration'),
                'm': I(self._vocab[MARC]+'non-nitrate-disaster'),
            },
            Completeness = {
                'c': I(self._vocab[MARC]+'complete'),
                'i': I(self._vocab[MARC]+'incomplete'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
            }
        )

        self.Kit = dict(
            SpecificMaterialDesignation = {
                'u': I(self._vocab[MARC]+'unspecified'),
            },
        )

        self.NotatedMusic = dict(
            SpecificMaterialDesignation = {
                'u': I(self._vocab[MARC]+'unspecified'),
            },
        )

        self.RemoteSensingImage = dict(
            SpecificMaterialDesignation = {
                'u': I(self._vocab[MARC]+'unspecified'),
            },
            AltitudeOfSensor = {
                'a': I(self._vocab[MARC]+'surface'),
                'b': I(self._vocab[MARC]+'airborne'),
                'c': I(self._vocab[MARC]+'spaceborne'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            AttitudeOfSensor = {
                'a': I(self._vocab[MARC]+'low-oblique'),
                'b': I(self._vocab[MARC]+'high-oblique'),
                'c': I(self._vocab[MARC]+'vertical'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
            },
            CloudCover = {
                '0': '0-9%',
                '1': '10-19%',
                '2': '20-29%',
                '3': '30-39%',
                '4': '40-49%',
                '5': '50-59%',
                '6': '60-69%',
                '7': '70-79%',
                '8': '80-89%',
                '9': '90-100%',
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
            },
            PlatformConstructionType = {
                'a': I(self._vocab[MARC]+'balloon'),
                'b': I(self._vocab[MARC]+'aircraft-low-altitude'),
                'c': I(self._vocab[MARC]+'aircraft-medium-altitude'),
                'd': I(self._vocab[MARC]+'aircraft-high-altitude'),
                'e': I(self._vocab[MARC]+'manned-spacecraft'),
                'f': I(self._vocab[MARC]+'unmanned-spacecraft'),
                'g': I(self._vocab[MARC]+'land-based-remote-sensing-device'),
                'h': I(self._vocab[MARC]+'water-surface-based-remote-sensing-device'),
                'i': I(self._vocab[MARC]+'submersible-remote-sensing-device'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            PlatformUseCategory = {
                'a': I(self._vocab[MARC]+'meterological'),
                'b': I(self._vocab[MARC]+'surface-observing'),
                'c': I(self._vocab[MARC]+'space-observing'),
                'm': I(self._vocab[MARC]+'mixed-uses'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            SensorType = {
                'a': I(self._vocab[MARC]+'active'),
                'b': I(self._vocab[MARC]+'passive'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            DataType = {
                'aa': I(self._vocab[MARC]+'visible-light'),
                'da': I(self._vocab[MARC]+'near-infrared'),
                'db': I(self._vocab[MARC]+'middle-infrared'),
                'dc': I(self._vocab[MARC]+'far-infrared'),
                'dd': I(self._vocab[MARC]+'thermal-infrared'),
                'de': I(self._vocab[MARC]+'shortwave-infrared'),
                'df': I(self._vocab[MARC]+'reflective-infrared'),
                'dv': I(self._vocab[MARC]+'infrared-combinations'),
                'dz': I(self._vocab[MARC]+'other-infrared-data'),
                'ga': I(self._vocab[MARC]+'sidelooking-airborne-radar'),
                'gb': I(self._vocab[MARC]+'synthetic-aperture-radar-single-frequency'),
                'gc': I(self._vocab[MARC]+'sar-multi-frequency-multichannel'),
                'gd': I(self._vocab[MARC]+'sar-like-polarization'),
                'gd': I(self._vocab[MARC]+'sar-cross-polarization'),
                'gg': I(self._vocab[MARC]+'polarmetric-sar'),
                'gu': I(self._vocab[MARC]+'passive-microwave-mapping'),
                'gz': I(self._vocab[MARC]+'other-microwave-data'),
                'ja': I(self._vocab[MARC]+'far-ultraviolet'),
                'jb': I(self._vocab[MARC]+'middle-ultraviolet'),
                'jc': I(self._vocab[MARC]+'near-ultraviolet'),
                'jd': I(self._vocab[MARC]+'ultraviolet-combinations'),
                'ja': I(self._vocab[MARC]+'far-ultraviolet'),
                'jz': I(self._vocab[MARC]+'other-ultraviolet-data'),
                'ma': I(self._vocab[MARC]+'multi-spectral-multidata'),
                'mb': I(self._vocab[MARC]+'multi-temporal'),
                'mm': I(self._vocab[MARC]+'combination-of-various-data-types'),
                'nn': I(self._vocab[MARC]+'not-applicable'),
                'pa': I(self._vocab[MARC]+'sonar-water-depth'),
                'pb': I(self._vocab[MARC]+'sonar-bottom-topography-images-sidescan'),
                'pc': I(self._vocab[MARC]+'sonar-bottom-topography-near-surface'),
                'pd': I(self._vocab[MARC]+'sonar-bottom-topography-near-buttom'),
                'pe': I(self._vocab[MARC]+'seismic-surveys'),
                'pz': I(self._vocab[MARC]+'other-acoustical-data'),
                'ra': I(self._vocab[MARC]+'gravity-anomalies-general'),
                'rb': I(self._vocab[MARC]+'free-air'),
                'rc': I(self._vocab[MARC]+'bouger'),
                'rd': I(self._vocab[MARC]+'isostatic'),
                'sa': I(self._vocab[MARC]+'magnetic-field'),
                'ta': I(self._vocab[MARC]+'radiometric-surveys'),
                'uu': I(self._vocab[MARC]+'unknown'),
                'zz': I(self._vocab[MARC]+'other'),
            }
        )

        self.SoundRecording = dict(
            SpecificMaterialDesignation = {
                'd': I(self._vocab[MARC]+'sound-disc'),
                'e': I(self._vocab[MARC]+'cylinder'),
                'g': I(self._vocab[MARC]+'sound-cartridge'),
                'i': I(self._vocab[MARC]+'sound-track-film'),
                'q': I(self._vocab[MARC]+'roll'),
                's': I(self._vocab[MARC]+'sound-cassette'),
                't': I(self._vocab[MARC]+'sound-tape-reel'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'w': I(self._vocab[MARC]+'wire-recording'),
                'z': I(self._vocab[MARC]+'other'),
            },
            Speed = {
                'a': '16 rpm (discs)',
                'b': '33 1/3 rpm (discs)',
                'c': '45 rpm (discs)',
                'd': '78 rpm (discs)',
                'e': '8 rpm (discs)',
                'f': '1.4m. per second (discs)',
                'h': '120 rpm (cylinders)',
                'i': '160 rpm (cylinders)',
                'k': '15/16 ips (tapes)',
                'l': '1 7/8 ips (tapes)',
                'm': '3 3/4 ips (tapes)',
                'o': '7 1/2 ips (tapes)',
                'p': '15 ips (tapes)',
                'r': '30 ips (tape)',
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            GrooveWidthPitch = {
                'm': I(self._vocab[MARC]+'microgroove-fine'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                's': I(self._vocab[MARC]+'coarse-standard'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            Dimensions = {
                'a': '3 in. diameter',
                'b': '5 in. diameter',
                'c': '7 in. diameter',
                'd': '10 in. diameter',
                'e': '12 in. diameter',
                'f': '16 in. diameter',
                'g': '4 3/4 in. or 12 cm. diameter',
                'j': '3 7/8 x 2 1/2 in.',
                'n': I(self._vocab[MARC]+'not-applicable'),
                'o': '5 1/4 x 3 7/8 in.',
                's': '2 3/4 x 4 in.',
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            TapeWidth = {
                'l': '1/8 in.',
                'm': '1/4 in.',
                'n': I(self._vocab[MARC]+'not-applicable'),
                'o': '1/2 in.',
                'p': '1 in.',
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            TapeConfiguration = {
                'a': I(self._vocab[MARC]+'full-1-track'),
                'b': I(self._vocab[MARC]+'half-2-track'),
                'c': I(self._vocab[MARC]+'quarter-4-track'),
                'd': I(self._vocab[MARC]+'eight-track'),
                'e': I(self._vocab[MARC]+'twelve-track'),
                'f': I(self._vocab[MARC]+'sixteen-track'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            KindOfDiscCylinderOrTape = {
                'a': I(self._vocab[MARC]+'master-tape'),
                'b': I(self._vocab[MARC]+'tape-duplication-master'),
                'd': I(self._vocab[MARC]+'disc-master-negative'),
                'i': I(self._vocab[MARC]+'instantaneous-recorded-on-the-spot'),
                'm': I(self._vocab[MARC]+'mass-produced'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'r': I(self._vocab[MARC]+'mother-positive'),
                's': I(self._vocab[MARC]+'stamper-negative'),
                't': I(self._vocab[MARC]+'test-pressing'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            KindOfMaterial = {
                'a': I(self._vocab[MARC]+'lacquer-coating'),
                'b': I(self._vocab[MARC]+'cellulose-nitrate'),
                'c': I(self._vocab[MARC]+'acetate-tape-with-ferrous-oxide'),
                'g': I(self._vocab[MARC]+'glass-with-lacquer'),
                'i': I(self._vocab[MARC]+'aluminum-with-lacquer'),
                'l': I(self._vocab[MARC]+'metal'),
                'm': I(self._vocab[MARC]+'plastic-with-metal'),
                'p': I(self._vocab[MARC]+'plastic'),
                'r': I(self._vocab[MARC]+'paper-with-lacquer-or-ferrous-oxide'),
                's': I(self._vocab[MARC]+'shellac'),
                'w': I(self._vocab[MARC]+'wax'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            KindOfCutting = {
                'h': I(self._vocab[MARC]+'hill-and-dale-cutting'),
                'l': I(self._vocab[MARC]+'lateral-or-combined-cutting'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
            },
            SpecialPlaybackCharacteristics = {
                'a': I(self._vocab[MARC]+'nab-standard'),
                'b': I(self._vocab[MARC]+'ccir-standard'),
                'c': I(self._vocab[MARC]+'dolby-b-encoded'),
                'd': I(self._vocab[MARC]+'dbx-encoded'),
                'e': I(self._vocab[MARC]+'digital-recording'),
                'f': I(self._vocab[MARC]+'dolby-a-encoded'),
                'g': I(self._vocab[MARC]+'dolby-c-encoded'),
                'h': I(self._vocab[MARC]+'cx-encoded'),
                'n': I(self._vocab[MARC]+'not-applicable'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            CaptureAndStorageTechnique = {
                'a': I(self._vocab[MARC]+'acoustical-capture-direct-storage'),
                'b': I(self._vocab[MARC]+'direct-storage-not-acoustical'),
                'd': I(self._vocab[MARC]+'digital-storage'),
                'e': I(self._vocab[MARC]+'analog-electrical-storage'),
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            }
        )

        self.Text = dict(
            SpecificMaterialDesignation = {
                'a': I(self._vocab[MARC]+'regular-print'),
                'b': I(self._vocab[MARC]+'large-print'),
                'c': I(self._vocab[MARC]+'braille'),
                'd': I(self._vocab[MARC]+'loose-leaf'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
        )

        self.VideoRecording = dict(
            SpecificMaterialDesignation = {
                'c': I(self._vocab[MARC]+'videocartridge'),
                'd': I(self._vocab[MARC]+'videodisc'),
                'f': I(self._vocab[MARC]+'videocassette'),
                'r': I(self._vocab[MARC]+'videoreel'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            },
            VideorecordingFormat = {
                'a': 'Beta (1/2 in., videocassette)',
                'b': 'VHS (1/2 in., videocassette)',
                'c': 'U-matic (3/4 in., videocasstte)',
                'd': 'EIAJ (1/2 in., reel)',
                'e': 'Type C (1 in., reel)',
                'f': 'Quadruplex (1 in. or 2 in., reel)',
                'g': 'laserdisc',
                'h': 'CED (Capacitance Electronic Disc) videodisc',
                'i': 'Betacam (1/2 in., videocassette)',
                'j': 'Betacam SP (1/2 in., videocassette)',
                'k': 'Super-VHS (1/2 in., videocassette)',
                'm': 'M-II (1/2 in., videocassette)',
                'o': 'D-2 (3/4 in., videocassette)',
                'p': '8mm.',
                'q': 'Hi-8 mm.',
                's': 'Blu-ray disc',
                'v': 'DVD',
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            },
            Dimensions = {
                'a': '8 mm.',
                'm': '1/4 in.',
                'o': '1/2 in.',
                'p': '1 in.',
                'q': '2 in.',
                'r': '3/4 in.',
                'u': I(self._vocab[MARC]+'unknown'),
                'z': I(self._vocab[MARC]+'other'),
            }
        )

        self.UnspecifiedCategory = dict(
            SpecificMaterialDesignation = {
                'm': I(self._vocab[MARC]+'multiple-physical-forms'),
                'u': I(self._vocab[MARC]+'unspecified'),
                'z': I(self._vocab[MARC]+'other'),
            }
        )

        self.MATERIAL_CATEGORY = {
            'a': 'Map',
            'c': 'ElectronicResource',
            'd': 'Globe',
            'f': 'TactileMaterial',
            'g': 'ProjectedGraphic',
            'h': 'Microform',
            'k': 'NonprojectedGraphic',
            'm': 'MotionPicture',
            'o': 'Kit',
            'q': 'NotatedMusic',
            'r': 'RemoteSensingImage',
            's': 'SoundRecording',
            't': 'Text',
            'v': 'VideoRecording',
            'z': 'UnspecifiedCategory',
        }

        return

    def marc_int(self, rt):
        '''
        Handle encoded integers with fallback
        '''
        mi = None # no property produced
        try:
            mi = int(rt)
        except ValueError:
            if rt == 'nnn':
                mi = I(self._vocab[MARC]+"not-applicable")
            elif rt == 'mmm':
                mi = I(self._vocab[MARC]+"multiple")
            elif rt == '---':
                mi = I(self._vocab[MARC]+"unknown")
            else:
                pass #None

        return mi

    def material_type_by_leader(self, leader, logger):

        # first perform 6/7 lookup, then fallback to 6 lookup
        leader = leader.ljust(24) if leader is not None else ' '*24
        _06 = leader[6]
        _07 = leader[7] if leader[7] != ' ' else ''
        typ = self.MATERIAL_TYPE.get(_06+_07)
        if not typ:
            typ = self.MATERIAL_TYPE.get(_06)
            if not typ:
                logger.debug('Unknown leader 6/7 combination "{}"'.format(_06+_07))

        return typ

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
        >>> list(t.process_leader({'leader':'03495cpcaa2200673 a 4500','default-origin':None,'instanceids':[None]}))
        [(None, I(http://bibfra.me/purl/versa/type), (I(http://bibfra.me/vocab/marc/Collection), I(http://bibfra.me/vocab/marc/Multimedia))), (None, I(http://bibfra.me/purl/versa/type), I(http://bibfra.me/vocab/marc/Collection))]
        """
        if 'leader' not in params: return

        leader = params['leader']
        leader = leader.ljust(24) if leader is not None else ' '*24

        work = I(params['default-origin'])
        instance = params['instanceids'][0]
        instance = I(instance) if instance else None
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

    def _process_fixed_length(self, typ, info, offset, params):
        """
        Processes 006, 007, and 008 control fields containing fixed length data elements,
        according to the MARC standards http://www.loc.gov/marc/umb/um07to10.html#part9
        and http://www.loc.gov/marc/bibliographic/bd007.html

        :typ: - the map for the category used to interpret the text in 'info'
        :info: - text string or list thereof containing 006/007/008 data
        :offset: - byte offset into 'info' containing germane data. 18 for 008, 0 for 006 and 007 (007 patterns just avoid index 0)
        :params: - work and instance resources in context of which 008 is being processed. Useful in the return value.

        yields - 0 or more 3-tuples, (origin, rel, target), each representing a new
            link generated from 008 data. origin is almost always the work or instance
            resource passed in. If origin is None, signal to the caller to default
            to the work as origin

        """
        if info is None: return

        work = I(params['default-origin'])
        instance = params['instanceids'][0]
        instance = I(instance) if instance else None
        logger = params['logger']

        #MARC characters skipped in the 008 field by convention
        #In most cases we dont have to actually check for these, as they'll just not be in the value lookup tables above
        SKIP_CHARS = ('#', ' ', '|')

        # Registry of patterns to be processed from 008 field {index key: value function}
        # There are 3 types of index keys to this dict
        # 1) An int, simply processed as a character position passed to the value function
        # 2) A tuple of ints, processed once for each character position in the list, each int passed to the value function
        # 3) A tuple starting with 'slice' and then 2 ints, processed as a character chunk/slice passed as a whole to the value function
        # If the value function returns None or a tuple with None in the last position, it's a signal to do nothing for the case at hand
        #
        # The current pattern structure could be simplified greatly if it
        # internalized the common relationship between property name and the map
        # for that field FIXME
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
            Maps = { #006/008
                (0, 1, 2, 3): lambda i: (None, I(self._vocab[MARC]+'relief'), SLUG(self.Maps['Relief'].get(info[i]))),
                ('slice', 4, 5): lambda i: (None, I(self._vocab[MARC]+'projection'), SLUG(self.Maps['Projection'].get(info[i]))),
                7: lambda i: (None, I(self._vocab[MARC]+'characteristic'), SLUG(self.Maps['TypeOfCartographicMaterial'].get(info[i]))),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
                11: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                13: lambda i: (None, I(self._vocab[MARC]+'index'), SLUG(self.INDEX.get(info[i]))),
                (15, 16): lambda i: (None, I(self._vocab[MARC]+'specialFormatCharacteristics'), SLUG(self.Maps['SpecialFormatCharacteristics'].get(info[i]))),
            },
            VisualMaterials = {
                ('slice', 0, 3): lambda i: (None, I(self._vocab[MARC]+'runtime'), self.marc_int(info[i])),
                4: lambda i: (None, I(self._vocab[MARC]+'targetAudience'), SLUG(self.AUDIENCE.get(info[i]))),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
                11: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                15: lambda i: (None, I(self._vocab[MARC]+'characteristic'), SLUG(self.VisualMaterials['TypeOfVisualMaterial'].get(info[i]))),
                16: lambda i: (None, I(self._vocab[MARC]+'technique'), SLUG(self.VisualMaterials['Technique'].get(info[i]))),
            },
            ComputerFiles = {
                4: lambda i: (None, I(self._vocab[MARC]+'targetAudience'), SLUG(self.AUDIENCE.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.ComputerFiles['FormOfItem'].get(info[i]))),
                8: lambda i: (None, I(self._vocab[MARC]+'characteristic'), SLUG(self.ComputerFiles['TypeOfComputerFile'].get(info[i]))),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
            },
            MixedMaterials = {
                5: lambda i: (None, I(self._vocab[VTYPE]), self.FORM_OF_ITEM.get(info[i])),
            },
            ContinuingResources = {
                0: lambda i: (None, I(self._vocab[MARC]+'frequency'), SLUG(self.ContinuingResources['Frequency'].get(info[i]))),
                1: lambda i: (None, I(self._vocab[MARC]+'regularity'), SLUG(self.ContinuingResources['Regularity'].get(info[i]))),
                3: lambda i: (None, I(self._vocab[MARC]+'characteristic'), SLUG(self.ContinuingResources['TypeOfContinuingResource'].get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'formOfOriginalItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'formOfItem'), SLUG(self.FORM_OF_ITEM.get(info[i]))),
                6: lambda i: (None, I(self._vocab[MARC]+'natureOfEntireWork'), SLUG(self.NATURE_OF_CONTENTS.get(info[i]))),
                (7,8,9): lambda i: (None, I(self._vocab[MARC]+'natureOfContents'), SLUG(self.NATURE_OF_CONTENTS.get(info[i]))),
                10: lambda i: (None, I(self._vocab[MARC]+'governmentPublication'), SLUG(self.GOVT_PUBLICATION.get(info[i]))),
                11: lambda i: (None, I(self._vocab[VTYPE]), self.CONFERENCE_PUBLICATION.get(info[i])),
                15: lambda i: (None, I(self._vocab[MARC]+'originalAlphabetOrScriptOfTitle'), SLUG(self.ContinuingResources['OriginalAlphabetOrScriptOfTitle'].get(info[i]))),
                16: lambda i: (None, I(self._vocab[MARC]+'entryConvention'), SLUG(self.ContinuingResources['EntryConvention'].get(info[i]))),
            },
            Map = { #007
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.Map['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'color'), SLUG(self.COLOR.get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'physicalMedium'), SLUG(self.PHYSICAL_MEDIUM.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'typeOfReproduction'), SLUG(self.TYPE_OF_REPRODUCTION.get(info[i]))),
                6: lambda i: (instance, I(self._vocab[MARC]+'productionReproductionDetails'), SLUG(self.PRODUCTION_REPRODUCTION_DETAILS.get(info[i]))),
                7: lambda i: (instance, I(self._vocab[MARC]+'positiveNegativeAspect'), SLUG(self.POSITIVE_NEGATIVE_ASPECT.get(info[i]))),
            },
            ElectronicResource = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.ElectronicResource['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'color'), SLUG(self.COLOR.get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'dimensions'), SLUG(self.ElectronicResource['Dimensions'].get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'sound'), SLUG(self.ElectronicResource['Sound'].get(info[i]))),
                ('slice', 6, 8): lambda i: (None, I(self._vocab[MARC]+'imageBitDepth'), self.marc_int(info[i])),
                9: lambda i: (instance, I(self._vocab[MARC]+'fileFormat'), SLUG(self.ElectronicResource['FileFormats'].get(info[i]))),
                10: lambda i: (instance, I(self._vocab[MARC]+'qualityAssuranceTargets'), SLUG(self.ElectronicResource['QualityAssuranceTargets'].get(info[i]))),
                11: lambda i: (instance, I(self._vocab[MARC]+'antecedentSource'), SLUG(self.ElectronicResource['AntecedentSource'].get(info[i]))),
                12: lambda i: (instance, I(self._vocab[MARC]+'levelOfCompression'), SLUG(self.ElectronicResource['LevelOfCompression'].get(info[i]))),
                13: lambda i: (instance, I(self._vocab[MARC]+'reformattingQuality'), SLUG(self.ElectronicResource['ReformattingQuality'].get(info[i]))),
            },
            Globe = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.Globe['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'color'), SLUG(self.COLOR.get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'physicalMedium'), SLUG(self.PHYSICAL_MEDIUM.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'typeOfReproduction'), SLUG(self.TYPE_OF_REPRODUCTION.get(info[i]))),
            },
            TactileMaterial = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.TactileMaterial['SpecificMaterialDesignation'].get(info[i]))),
                ('slice', 3, 4): lambda i: (instance, I(self._vocab[MARC]+'classOfBrailleWriting'), SLUG(self.TactileMaterial['ClassOfBrailleWriting'].get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'levelOfContraction'), SLUG(self.TactileMaterial['LevelOfContraction'].get(info[i]))),
                (6, 7, 8): lambda i: (instance, I(self._vocab[MARC]+'brailleMusicFormat'), SLUG(self.TactileMaterial['BrailleMusicFormat'].get(info[i]))),
                9: lambda i: (instance, I(self._vocab[MARC]+'specialPhysicalCharacteristics'), SLUG(self.TactileMaterial['SpecialPhysicalCharacteristics'].get(info[i]))),
            },
            ProjectedGraphic = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.ProjectedGraphic['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'color'), SLUG(self.COLOR.get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'baseOfEmulsion'), SLUG(self.ProjectedGraphic['SpecificMaterialDesignation'].get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'soundOnMediumOrSeparate'), SLUG(self.SOUND_ON_MEDIUM_OR_SEPARATE.get(info[i]))),
                6: lambda i: (instance, I(self._vocab[MARC]+'mediumForSound'), SLUG(self.MEDIUM_FOR_SOUND.get(info[i]))),
                7: lambda i: (instance, I(self._vocab[MARC]+'dimensions'), SLUG(self.DIMENSIONS_FILM.get(info[i]))),
                8: lambda i: (instance, I(self._vocab[MARC]+'secondarySupportMaterial'), SLUG(self.SUPPORT_MATERIAL.get(info[i]))),
            },
            Microform = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.Microform['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'positiveNegativeAspect'), SLUG(self.POSITIVE_NEGATIVE_ASPECT.get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'dimensions'), SLUG(self.Microform['Dimensions'].get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'reductionRatioRange'), SLUG(self.Microform['ReductionRatioRange'].get(info[i]))),
                ('slice', 6, 8): lambda i: (instance, I(self._vocab[MARC]+'reductionRatio'), info[i]),
                9: lambda i: (instance, I(self._vocab[MARC]+'color'), SLUG(self.COLOR.get(info[i]))),
               10: lambda i: (instance, I(self._vocab[MARC]+'emulsionOnFilm'), SLUG(self.Microform['EmulsionOnFilm'].get(info[i]))),
               11: lambda i: (instance, I(self._vocab[MARC]+'generation'), SLUG(self.Microform['Generation'].get(info[i]))),
               12: lambda i: (instance, I(self._vocab[MARC]+'baseOfFilm'), SLUG(self.BASE_OF_FILM.get(info[i]))),
            },
            NonprojectedGraphic = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.NonprojectedGraphic['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'color'), SLUG(self.COLOR.get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'primarySupportMaterial'), SLUG(self.SUPPORT_MATERIAL.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'secondarySupportMaterial'), SLUG(self.SUPPORT_MATERIAL.get(info[i]))),
            },
            MotionPicture = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.MotionPicture['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'color'), SLUG(self.COLOR.get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'motionPicturePresentationFormat'), SLUG(self.MotionPicture['MotionPicturePresentationFormat'].get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'soundOnMediumOrSeparate'), SLUG(self.SOUND_ON_MEDIUM_OR_SEPARATE.get(info[i]))),
                6: lambda i: (instance, I(self._vocab[MARC]+'mediumForSound'), SLUG(self.MEDIUM_FOR_SOUND.get(info[i]))),
                7: lambda i: (instance, I(self._vocab[MARC]+'dimensions'), SLUG(self.DIMENSIONS_FILM.get(info[i]))),
                8: lambda i: (instance, I(self._vocab[MARC]+'configurationOfPlaybackChannels'), SLUG(self.CONFIGURATION_OF_PLAYBACK_CHANNELS.get(info[i]))),
                9: lambda i: (instance, I(self._vocab[MARC]+'productionElements'), SLUG(self.MotionPicture['ProductionElements'].get(info[i]))),
               10: lambda i: (instance, I(self._vocab[MARC]+'positiveNegativeAspect'), SLUG(self.POSITIVE_NEGATIVE_ASPECT.get(info[i]))),
               11: lambda i: (instance, I(self._vocab[MARC]+'generation'), SLUG(self.MotionPicture['Generation'].get(info[i]))),
               12: lambda i: (instance, I(self._vocab[MARC]+'baseOfFilm'), SLUG(self.BASE_OF_FILM.get(info[i]))),
               13: lambda i: (instance, I(self._vocab[MARC]+'refinedCategoriesOfColor'), SLUG(self.MotionPicture['RefinedCategoriesOfColor'].get(info[i]))),
               14: lambda i: (instance, I(self._vocab[MARC]+'kindOfColorStockOrPrint'), SLUG(self.MotionPicture['KindOfColorStockOrPrint'].get(info[i]))),
               15: lambda i: (instance, I(self._vocab[MARC]+'deteriorationStage'), SLUG(self.MotionPicture['DeteriorationStage'].get(info[i]))),
               16: lambda i: (instance, I(self._vocab[MARC]+'completeness'), SLUG(self.MotionPicture['Completeness'].get(info[i]))),
               ('slice', 17, 23): lambda i: (instance, I(self._vocab[MARC]+'filmInspectionDate'), marc_date_yyyymm(info[i])),
            },
            Kit = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.Kit['SpecificMaterialDesignation'].get(info[i]))),
            },
            NotatedMusic = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.NotatedMusic['SpecificMaterialDesignation'].get(info[i]))),
            },
            RemoteSensingImage = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.RemoteSensingImage['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'altitudeOfSensor'), SLUG(self.RemoteSensingImage['AltitudeOfSensor'].get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'attitudeOfSensor'), SLUG(self.RemoteSensingImage['AttitudeOfSensor'].get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'cloudCover'), SLUG(self.RemoteSensingImage['CloudCover'].get(info[i]))),
                6: lambda i: (instance, I(self._vocab[MARC]+'platformConstructionType'), SLUG(self.RemoteSensingImage['PlatformConstructionType'].get(info[i]))),
                7: lambda i: (instance, I(self._vocab[MARC]+'platformUseCategory'), SLUG(self.RemoteSensingImage['PlatformUseCategory'].get(info[i]))),
                8: lambda i: (instance, I(self._vocab[MARC]+'sensorType'), SLUG(self.RemoteSensingImage['SensorType'].get(info[i]))),
                ('slice', 9, 10): lambda i: (instance, I(self._vocab[MARC]+'dataType'), SLUG(self.RemoteSensingImage['DataType'].get(info[i]))),
            },
            SoundRecording = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.SoundRecording['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'speed'), SLUG(self.SoundRecording['Speed'].get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'configurationOfPlaybackChannels'), SLUG(self.CONFIGURATION_OF_PLAYBACK_CHANNELS.get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'grooveWidthPitch'), SLUG(self.SoundRecording['GrooveWidthPitch'].get(info[i]))),
                6: lambda i: (instance, I(self._vocab[MARC]+'dimensions'), SLUG(self.SoundRecording['Dimensions'].get(info[i]))),
                7: lambda i: (instance, I(self._vocab[MARC]+'tapeWidth'), SLUG(self.SoundRecording['TapeWidth'].get(info[i]))),
                8: lambda i: (instance, I(self._vocab[MARC]+'tapeConfiguration'), SLUG(self.SoundRecording['TapeConfiguration'].get(info[i]))),
                9: lambda i: (instance, I(self._vocab[MARC]+'kindOfDiscCylinderOrTape'), SLUG(self.SoundRecording['KindOfDiscCylinderOrTape'].get(info[i]))),
               10: lambda i: (instance, I(self._vocab[MARC]+'kindOfMaterial'), SLUG(self.SoundRecording['KindOfMaterial'].get(info[i]))),
               11: lambda i: (instance, I(self._vocab[MARC]+'kindOfCutting'), SLUG(self.SoundRecording['KindOfCutting'].get(info[i]))),
               12: lambda i: (instance, I(self._vocab[MARC]+'specialPlaybackCharacteristics'), SLUG(self.SoundRecording['SpecialPlaybackCharacteristics'].get(info[i]))),
               13: lambda i: (instance, I(self._vocab[MARC]+'captureAndStorageTechnique'), SLUG(self.SoundRecording['CaptureAndStorageTechnique'].get(info[i]))),
            },
            Text = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.Text['SpecificMaterialDesignation'].get(info[i]))),
            },
            VideoRecording = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.VideoRecording['SpecificMaterialDesignation'].get(info[i]))),
                3: lambda i: (instance, I(self._vocab[MARC]+'color'), SLUG(self.COLOR.get(info[i]))),
                4: lambda i: (instance, I(self._vocab[MARC]+'videorecordingFormat'), SLUG(self.VideoRecording['VideorecordingFormat'].get(info[i]))),
                5: lambda i: (instance, I(self._vocab[MARC]+'soundOnMediumOrSeparate'), SLUG(self.SOUND_ON_MEDIUM_OR_SEPARATE.get(info[i]))),
                6: lambda i: (instance, I(self._vocab[MARC]+'mediumForSound'), SLUG(self.MEDIUM_FOR_SOUND.get(info[i]))),
                7: lambda i: (instance, I(self._vocab[MARC]+'dimensions'), SLUG(self.VideoRecording['Dimensions'].get(info[i]))),
                8: lambda i: (instance, I(self._vocab[MARC]+'configurationOfPlaybackChannels'), SLUG(self.CONFIGURATION_OF_PLAYBACK_CHANNELS.get(info[i]))),
            },
            UnspecifiedCategory = {
                1: lambda i: (instance, I(self._vocab[MARC]+'specificMaterialDesignation'), SLUG(self.UnspecifiedCategory['SpecificMaterialDesignation'].get(info[i]))),
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
        #>>> list(t.process_008(ld,{'leader':ld,'default-origin':None,'instanceids':[None],'logger':logging}))
        #[('date_008', '1979-07-26')]
        '''
        if info is None: return

        leader = params['leader']
        work = I(params['default-origin'])
        #instance = params['instanceids'][0]
        #instance = I(instance) if instance else None
        logger = params['logger']

        # pad to expected size
        info = info.ljust(40)

        # special case language tag
        lang = info[35:38]
        if lang not in ("###", "|||", "zxx", "mul", "sgn", "und", "   "):
            yield work, I(self._vocab[LANG]), lang

        # see marc_date above re date_008

        typ = self.material_type_by_leader(leader, logger)
        if typ:
            yield work, I(self._vocab[VTYPE]), I(self._vocab[MARC]+typ)

        yield from self._process_fixed_length(typ, info, 18, params)

    def process_006(self, infos, params):
        '''
        Re: Multiple 006 fields see page 2 of University of Colorado Boulder University Libraries Cataloging Procedures Manual,
        "Books with Accompanying Media" https://ucblibraries.colorado.edu/cataloging/cpm/bookswithmedia.pdf
        '''

        leader = params['leader']
        work = I(params['default-origin'])
        #instance = params['instanceids'][0]
        #instance = I(instance) if instance else None
        logger = params['logger']

        typ = self.material_type_by_leader(leader, logger)

        # add a type statement for this type too
        if typ:
            yield work, I(self._vocab[VTYPE]), I(self._vocab[MARC]+typ)

        for info in infos:
            # pad to expected size
            info = info.ljust(18)

            yield from self._process_fixed_length(typ, info, 1, params)

    def process_007(self, infos, params):
        '''
        Process multiple 007 control fields per http://www.loc.gov/marc/bibliographic/bd007.html
        '''
        instance = params['instanceids'][0]
        instance = I(instance) if instance else None

        for info in infos:
            info = info.ljust(23)
            _00 = info[0] # index 0 indicates material category
            typ = self.MATERIAL_CATEGORY.get(_00)
            if not typ:
                params['logger'].debug('Unknown 007 material category "{}"'.format(_00))
            else:
                yield instance, I(self._vocab[VTYPE]), I(self._vocab[MARC]+typ)

            yield from self._process_fixed_length(typ, info, 0, params)

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
