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

class transforms(object):
    def __init__(self, vocab=None):
        DEFAULT_VOCAB = { i:i for i in DEFAULT_VOCAB_ITEMS }
        vocab = vocab or {}
        #Use any provided, overridden vocab items, or just the defaults
        self._vocab = { i: vocab.get(i, i) for i in DEFAULT_VOCAB_ITEMS }
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

    def process_008(self, info, work, instance):
        """
        Processes 008 control field according to the MARC standard.
        http://www.loc.gov/marc/umb/um07to10.html#part9

        :info: - text of 008 field, a character array
        :work: - work resource in context of which 008 is being processed. Useful in the return value.
        :instance: - instance resource in context of which leader is being processed. Useful in the return value.

        yields - 0 or more 3-tuples, (origin, rel, target), each representing a new
            link generated from 008 data. origin is almost always the work or instance
            resource passed in. If origin is None, signal to the caller to default
            to the work as origin


        #>>> from bibframe.reader.marcextra import transforms
        #>>> t = transforms()
        #>>> list(t.process_008('790726||||||||||||                 eng  '))
        #[('date', '1979-07-26')]
        """
        audiences = {
            'a': I(self._vocab[BL]+"preschool"),
            'b': I(self._vocab[BL]+"primary"),
            'c': I(self._vocab[BL]+"pre-adolescent"),
            'd': I(self._vocab[BL]+"adolescent"),
            'e': I(self._vocab[BL]+"adult"),
            'f': I(self._vocab[BL]+"specialized"),
            'g': I(self._vocab[BL]+"general"),
            'j': I(self._vocab[BL]+"juvenile")}

        media = {
            'a': I(self._vocab[BL]+"microfilm"),
            'b': I(self._vocab[BL]+"microfiche"),
            'c': I(self._vocab[BL]+"microopaque"),
            'd': I(self._vocab[BL]+"large-print"),
            'f': I(self._vocab[BL]+"braille"),
            'r': I(self._vocab[BL]+"regular-print-reproduction"),
            's': I(self._vocab[BL]+"electronic")
            }

        types = {
            "a": I(self._vocab[BL]+"abstracts-summaries"),
            #Don't use + in marcextra values because of problems with dumb RDF reserialization
            #"a": I(self._vocab[BL]+"abstracts+summaries"),
            "b": I(self._vocab[BL]+"bibliography"), #"bibliographies (is one or contains one)"
            "c": I(self._vocab[BL]+"catalogs"),
            "d": I(self._vocab[BL]+"dictionaries"),
            "e": I(self._vocab[BL]+"encyclopedias"),
            "f": I(self._vocab[BL]+"handbooks"),
            "g": I(self._vocab[BL]+"legal-articles"),
            "i": I(self._vocab[BL]+"indexes"),
            "j": I(self._vocab[BL]+"patent-document"),
            "k": I(self._vocab[BL]+"discographies"),
            "l": I(self._vocab[BL]+"legislation"),
            "m": I(self._vocab[BL]+"theses"),
            "n": I(self._vocab[BL]+"surveys-of-literature"),
            "o": I(self._vocab[BL]+"reviews"),
            "p": I(self._vocab[BL]+"programmed-texts"),
            "q": I(self._vocab[BL]+"filmographies"),
            "r": I(self._vocab[BL]+"directories"),
            "s": I(self._vocab[BL]+"statistics"),
            "t": I(self._vocab[BL]+"technical-reports"),
            "u": I(self._vocab[BL]+"standards-specifications"),
            #Don't use + in marcextra values because of problems with dumb RDF reserialization
            #"u": I(self._vocab[BL]+"standards+specifications"),
            "v": I(self._vocab[BL]+"legal-cases-and-notes"),
            "w": I(self._vocab[BL]+"law-reports-and-digests"),
            "z": I(self._vocab[BL]+"treaties")}
    
        govt_publication = {
            "i": I(self._vocab[BL]+"international-or-intergovernmental-publication"),
            "f": I(self._vocab[BL]+"federal-national-government-publication"),
            "a": I(self._vocab[BL]+"publication-of-autonomous-or-semi-autonomous-component-of-government"),
            "s": I(self._vocab[BL]+"government-publication-of-a-state-province-territory-dependency-etc"),
            "m": I(self._vocab[BL]+"multistate-government-publication"),
            "c": I(self._vocab[BL]+"publication-from-multiple-local-governments"),
            "l": I(self._vocab[BL]+"local-government-publication"),
            "z": I(self._vocab[BL]+"other-type-of-government-publication"),
            "o": I(self._vocab[BL]+"government-publication-level-undetermined"),
            "u": I(self._vocab[BL]+"unknown-if-item-is-government-publication")}

        genres = {
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
            "s": I(self._vocab[BL]+"speeches")}

        biographical = dict(
            a=I(self._vocab[BL]+"autobiography"),
            b=I(self._vocab[BL]+'individual-biography'),
            c=I(self._vocab[BL]+'collective-biography'),
            d=I(self._vocab[BL]+'contains-biographical-information'))

        #Marc chaacters skipped in the 008 field by convention
        #In most cases we dont have to actually check for these, as they'll just not be in the value lookup tables above
        SKIP_CHARS = ('#', ' ', '|')
        #Registry of patterns to be processed from 008 field {index key: value function}
        #There are 3 types of index keys to this dict
        #1) An int, simply processed as a character position passed to the value function
        #2) A tuple of ints, processed once for each character position in the list, each int passed to the value function
        #3) A tuple starting with 'slice' and then 2 ints, processed as a character chunk/slice passed as a whole to the value function
        #If the value function returns None or a tuple with None in the lats position, it's a signal to do nothing for the case at hand
        FIELD_008_PATTERNS = {
            23: lambda i: (None, I(self._vocab[BL]+'medium'), media.get(info[i])),
            (24, 25, 26, 27): lambda i: (None, I(self._vocab[VTYPE]), types.get(info[i])),
            28: lambda i: (None, I(self._vocab[VTYPE]), govt_publication.get(info[i])),
            29: lambda i: (None, I(self._vocab[VTYPE]), I(self._vocab[BL]+'conference-publication'))
                            if info[i] == '1' else None,
            30: lambda i: (None, I(self._vocab[VTYPE]), I(self._vocab[BL]+'festschrift'))
                            if info[i] == '1' else None,
            33: lambda i: (None, I(self._vocab[VTYPE]), genres.get(info[i]))
                            if info[i] != 'u' else None, #'u' means unknown?
            34: lambda i: (None, I(self._vocab[VTYPE]), biographical.get(info[i])),
            ('slice', 35, 38): lambda i: (None, I(self._vocab[LANG]), info[i.start:i.stop])
                            if info[i.start:i.stop] not in
                                ("###", "zxx", "mul", "sgn", "und", "   ", "") else None,
        }
        
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

        yield from process_patterns(FIELD_008_PATTERNS)

    def process_006(self, infos, leader, work, instance):
        """
        Process 006 control fields

        :info: - list of the text from any 006 fields
        :leader - leader header, a character array

        Rest of params and yield, same as for process_008
        """

        # 006 requires a multi-stage lookup of everything in this page
        # and beneath the subtypes
        # http://www.loc.gov/marc/bibliographic/bd008.html

        Books = dict(
            Illustrations = dict(
                a=I(self._vocab[BL]+'illustrations'),
                b=I(self._vocab[BL]+'maps'),
                c=I(self._vocab[BL]+'portraits'),
                d=I(self._vocab[BL]+'charts'),
                e=I(self._vocab[BL]+'plans'),
                f=I(self._vocab[BL]+'plates'),
                g=I(self._vocab[BL]+'music'),
                h=I(self._vocab[BL]+'facsimiles'),
                i=I(self._vocab[BL]+'coats-of-arms'),
                j=I(self._vocab[BL]+'genealogical-tables'),
                k=I(self._vocab[BL]+'forms'),
                l=I(self._vocab[BL]+'samples'),
                m=I(self._vocab[BL]+'phonodisk'),
                o=I(self._vocab[BL]+'photographs'),
                p=I(self._vocab[BL]+'illuminations'),
            ),
            TargetAudience = dict(
                a=I(self._vocab[BL]+'preschool'),
                b=I(self._vocab[BL]+'primary'),
                c=I(self._vocab[BL]+'pre-adolescent'),
                d=I(self._vocab[BL]+'adolescent'),
                e=I(self._vocab[BL]+'adult'),
                f=I(self._vocab[BL]+'specialized'),
                g=I(self._vocab[BL]+'general'),
                j=I(self._vocab[BL]+'juvenile'),
            ),
            FormOfItem = dict(
                a=I(self._vocab[BL]+'microfilm'),
                b=I(self._vocab[BL]+'microfiche'),
                c=I(self._vocab[BL]+'microopaque'),
                d=I(self._vocab[BL]+'large-print'),
                f=I(self._vocab[BL]+'braille'),
                o=I(self._vocab[BL]+'online'),
                q=I(self._vocab[BL]+'direct-electronic'),
                r=I(self._vocab[BL]+'regular-print-reproduction'),
                s=I(self._vocab[BL]+'electronic'),
            ),
            NatureOfContents = { # numeric keys
                'a': I(self._vocab[BL]+'abstracts-summaries'),
                'b': I(self._vocab[BL]+'bibliographies'),
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
                'n': I(self._vocab[BL]+'surveys-of-literature-in-a-subject-area'),
                'o': I(self._vocab[BL]+'reviews'),
                'p': I(self._vocab[BL]+'programmed-texts'),
                'q': I(self._vocab[BL]+'filmographies'),
                'r': I(self._vocab[BL]+'directories'),
                's': I(self._vocab[BL]+'statistics'),
                't': I(self._vocab[BL]+'technical-reports'),
                'u': I(self._vocab[BL]+'standards-specifications'),
                'v': I(self._vocab[BL]+'legal-cases-and-case-notes'),
                'w': I(self._vocab[BL]+'law-reports-and-digests'),
                'y': I(self._vocab[BL]+'yearbooks'),
                'z': I(self._vocab[BL]+'treaties'),
                '2': I(self._vocab[BL]+'offprints'),
                '5': I(self._vocab[BL]+'calendars'),
                '6': I(self._vocab[BL]+'comics-graphic-novels'),
            },
            GovernmentPublication = dict(
            ),
            ConferencePublication = dict(
            ),
            Festschrift = dict(
            ),
            Index = dict(
            ),
            LiteraryForm = dict(
            ),
            Biography = dict(
            ),
        )

        Music = dict(
        )

        Maps = dict(
        )

        VisualMaterials = dict(
        )

        ComputerFiles = dict( 
        )

        MixedMaterials = dict(
        )

        # From http://www.itsmarc.com/crs/mergedprojects/helptop1/helptop1/variable_control_fields/idh_006_00_bib.htm
        material_form_type = dict(
            a='Books',
            c='Music',
            d='Music',
            e='Maps',
            f='Maps',
            g='VisualMaterials',
            i='Music',
            j='Music',
            k='VisualMaterials',
            m='ComputerFiles',
            o='VisualMaterials',
            p='MixedMaterials',
            r='VisualMaterials',
            t='Books'
            )

        Patterns_Books = {
            ('slice', 18, 22): lambda i: [(None, I(self._vocab[VTYPE]), Books['Illustrations'].get(x)) for x in info[i]],
            22: lambda i: (None, I(self._vocab[VTYPE]), Books['TargetAudience'].get(info[i])),
            23: lambda i: (None, I(self._vocab[VTYPE]), Books['FormOfItem'].get(info[i])),
            ('slice', 24, 28): lambda i: [(None, I(self._vocab[VTYPE]), Books['NatureOfContents'].get(x)) for x in info[i]],
            28: lambda i: (None, I(self._vocab[VTYPE]), Books['GovernmentPublication'].get(info[i])),
            29: lambda i: (None, I(self._vocab[VTYPE]), Books['ConferencePublication'].get(info[i])),
            30: lambda i: (None, I(self._vocab[VTYPE]), Books['Festschrift'].get(info[i])),
            31: lambda i: (None, I(self._vocab[VTYPE]), Books['Index'].get(info[i])),
            33: lambda i: (None, I(self._vocab[VTYPE]), Books['LiteraryForm'].get(info[i])),
            34: lambda i: (None, I(self._vocab[VTYPE]), Books['Biography'].get(info[i])),
        }

        Patterns_Music = {
        }

        _06 = leader[6]
        typ = material_form_type.get(_06, {})
        patterns = locals().get('Patterns_{}'.format(typ))
        if patterns:
            for info in infos: # FIXME unintuitive late binding of "info" to lambdas in patterns dicts
                yield from process_patterns(patterns)

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
