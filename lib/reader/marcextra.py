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
        http://www.loc.gov/marc/marc2dc.html#ldr06conversionrules
        http://www.loc.gov/marc/bibliographic/bdleader.html

        >>> from bibframe.reader.marcextra import transforms
        >>> t = transforms()
        >>> list(t.process_leader('03495cpcaa2200673 a 4500'))
        [(None, 'http://bibfra.me/purl/versa/type', I('Collection')), (None, 'http://bibfra.me/purl/versa/type', I('Multimedia')), (None, 'http://bibfra.me/purl/versa/type', I('Collection'))]
        """
        broad_06 = dict(
            a=I(self._vocab[BL]+"LanguageMaterial"),
            c=I(self._vocab[BL]+"LanguageMaterial"),
            d=I(self._vocab[BL]+"LanguageMaterial"),
            e=I(self._vocab[BL]+"StillImage"),
            f=I(self._vocab[BL]+"StillImage"),
            g=I(self._vocab[BL]+"MovingImage"),
            i=I(self._vocab[BL]+"Audio"),
            j=I(self._vocab[BL]+"Audio"),
            k=I(self._vocab[BL]+"StillImage"),
            m=I(self._vocab[BL]+"Software"),
            p=I(self._vocab[BL]+"Collection"),
            t=I(self._vocab[BL]+"LanguageMaterial"))
    
        detailed_06 = dict(
            a=I(self._vocab[BL]+"LanguageMaterial"),
            c=I(self._vocab[BL]+"NotatedMusic"),
            d=(self._vocab[BL]+I("Manuscript"), self._vocab[BL]+I("NotatedMusic")),
            e=I(self._vocab[BL]+"Cartography"),
            f=(self._vocab[BL]+I("Manuscript"), self._vocab[BL]+I("Cartography")),
            g=I(self._vocab[BL]+"MovingImage"),
            i=(self._vocab[BL]+I("Nonmusical"), self._vocab[BL]+I("Sounds")),
            j=I(self._vocab[BL]+"Musical"),
            k=I(self._vocab[BL]+"StillImage"),
            m=I(self._vocab[BL]+"Multimedia"),
            o=I(self._vocab[BL]+"Kit"),
            p=I(self._vocab[BL]+"Multimedia"),
            r=I(self._vocab[BL]+"ThreeDimensionalObject"),
            t=(self._vocab[BL]+I("LanguageMaterial"), self._vocab[BL]+I("Manuscript")))
    
        _06 = leader[6]
        if _06 in broad_06.keys():
            yield None, self._vocab[VTYPE], broad_06[_06]
        if _06 in detailed_06.keys():
            yield None, self._vocab[VTYPE], detailed_06[_06]
        if leader[7] in ('c', 's'):
            yield None, self._vocab[VTYPE], self._vocab[BL]+I("Collection")


    def process_008(self, info, work, instance):
        """
        http://www.loc.gov/marc/umb/um07to10.html#part9

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
        FiELD_OO8_PATTERNS = {
            23: lambda i: (None, self._vocab[BL]+'medium', media.get(info[i])),
            (24, 25, 26, 27): lambda i: (None, self._vocab[VTYPE], types.get(info[i])),
            28: lambda i: (None, self._vocab[VTYPE], govt_publication.get(info[i])),
            29: lambda i: (None, self._vocab[VTYPE], self._vocab[BL]+'conference-publication')
                            if info[i] == '1' else None,
            30: lambda i: (None, self._vocab[VTYPE], self._vocab[BL]+'festschrift')
                            if info[i] == '1' else None,
            33: lambda i: (None, self._vocab[VTYPE], genres.get(info[i]))
                            if info[i] != 'u' else None, #'u' means unknown?
            34: lambda i: (None, self._vocab[VTYPE], biographical.get(info[i])),
            ('slice', 35, 38): lambda i: (None, self._vocab[LANG], info[i.start:i.stop])
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

        #Execute the rules detailed in the "Registry of patterns" comment above
        for i, func in FiELD_OO8_PATTERNS.items():
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
                    if result and result[2] is not None:
                        yield result
                except IndexError:
                    pass #Truncated 008 field

