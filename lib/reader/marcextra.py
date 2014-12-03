'''
Treatment of certain special MARC fields, leader, 006, 007, 008, etc.
'''

from versa import I, VERSA_BASEIRI
from bibframe import BL, BA, REL, RDA, RBMS, AV

BL = 'http://bibfra.me/vocab/lite/'

#TODO: Also split on multiple 260 fields

VTYPE = VERSA_BASEIRI+'type'
DEFAULT_VOCAB_ITEMS = [BL, BA, REL, RDA, RBMS, AV, VTYPE]

class transforms(object):
    def __init__(self, vocab=None):
        DEFAULT_VOCAB = { i:i for i in DEFAULT_VOCAB_ITEMS }
        vocab = vocab or {}
        #Use any provided, overriden vocab items, or just the defaults
        self._vocab = { i: vocab.get(i, i) for i in DEFAULT_VOCAB_ITEMS }
        return

    def process_leader(self, leader):
        """
        http://www.loc.gov/marc/marc2dc.html#ldr06conversionrules
        http://www.loc.gov/marc/bibliographic/bdleader.html

        >>> from bibframe.reader.marcextra import transforms
        >>> t = transforms()
        >>> list(t.process_leader('03495cpcaa2200673 a 4500'))
        [(None, 'http://bibfra.me/purl/versa/type', I('Collection')), (None, 'http://bibfra.me/purl/versa/type', I('Multimedia')), (None, 'http://bibfra.me/purl/versa/type', I('Collection'))]
        """
        broad_06 = dict(
            a=I(self._vocab[BA]+"LanguageMaterial"),
            c=I("LanguageMaterial"),
            d=I("LanguageMaterial"),
            e=I("StillImage"),
            f=I("StillImage"),
            g=I("MovingImage"),
            i=I("Audio"),
            j=I("Audio"),
            k=I("StillImage"),
            m=I("Software"),
            p=I("Collection"),
            t=I("LanguageMaterial"))
    
        detailed_06 = dict(
            a=I("LanguageMaterial"),
            c=I("NotatedMusic"),
            d=(I("Manuscript"), I("NotatedMusic")),
            e=I("Cartography"),
            f=(I("Manuscript"), I("Cartography")),
            g=I("MovingImage"),
            i=(I("Nonmusical"), I("Sounds")),
            j=I("Musical"),
            k=I("StillImage"),
            m=I("Multimedia"),
            o=I("Kit"),
            p=I("Multimedia"),
            r=I("ThreeDimensionalObject"),
            t=(I("LanguageMaterial"), I("Manuscript")))
    
        _06 = leader[6]
        if _06 in broad_06.keys():
            yield None, self._vocab[VTYPE], broad_06[_06]
        if _06 in detailed_06.keys():
            yield None, self._vocab[VTYPE], detailed_06[_06]
        if leader[7] in ('c', 's'):
            yield None, self._vocab[VTYPE], I("Collection")


    def process_008(self, info):
        """
        http://www.loc.gov/marc/umb/um07to10.html#part9

        #>>> from bibframe.reader.marcextra import transforms
        #>>> t = transforms()
        #>>> list(t.process_008('790726||||||||||||                 eng  '))
        #[('date', '1979-07-26')]
        """
        audiences = {
            'a': I("preschool"),
            'b': I("primary"),
            'c': I("pre-adolescent"),
            'd': I("adolescent"),
            'e': I("adult"),
            'f': I("specialized"),
            'g': I("general"),
            'j': I("juvenile")}

        media = {
            'a': I("microfilm"),
            'b': I("microfiche"),
            'c': I("microopaque"),
            'd': I("large-print"),
            'f': I("braille"),
            'r': I("regular-print-reproduction"),
            's': I("electronic")
            }

        types = {
            "a": I("abstracts+summaries"),
            "b": I("bibliography"), #"bibliographies (is one or contains one)"
            "c": I("catalogs"),
            "d": I("dictionaries"),
            "e": I("encyclopedias"),
            "f": I("handbooks"),
            "g": I("legal-articles"),
            "i": I("indexes"),
            "j": I("patent-document"),
            "k": I("discographies"),
            "l": I("legislation"),
            "m": I("theses"),
            "n": I("surveys-of-literature"),
            "o": I("reviews"),
            "p": I("programmed-texts"),
            "q": I("filmographies"),
            "r": I("directories"),
            "s": I("statistics"),
            "t": I("technical-reports"),
            "u": I("standards+specifications"),
            "v": I("legal-cases-and-notes"),
            "w": I("law-reports-and-digests"),
            "z": I("treaties")}
    
        govt_publication = {
            "i": I("international-or-intergovernmental-publication"),
            "f": I("federal/national-government-publication"),
            "a": I("publication-of-autonomous-or-semi-autonomous-component-of-government"),
            "s": I("government-publication-of-a-state,-province,-territory,-dependency,-etc."),
            "m": I("multistate-government-publication"),
            "c": I("publication-from-multiple-local-governments"),
            "l": I("local-government-publication"),
            "z": I("other-type-of-government-publication"),
            "o": I("government-publication-level-undetermined"),
            "u": I("unknown-if-item-is-government-publication")}

        genres = {
            "0": I("non-fiction"),
            "1": I("fiction"),
            "c": I("comic-strips"),
            "d": I("dramas"),
            "e": I("essays"),
            "f": I("novels"),
            "h": I("humor-satires-etc."),
            "i": I("letters"),
            "j": I("short-stories"),
            "m": I("mixed-forms"),
            "p": I("poetry"),
            "s": I("speeches")}

        biographical = dict(
            a=I("autobiography"),
            b=I('individual-biography'),
            c=I('collective-biography'),
            d=I('contains-biographical-information'))
    
        #info = field008
        #ARE YOU FRIGGING KIDDING ME?! NON-Y2K SAFE?!
        year = info[0:2]
        try:
            century = '19' if int(year) > 30 else '20' #I guess we can give an 18 year berth before this breaks ;)
            # remove date_008 from data export at this time
            # yield 'date_008', '{}{}-{}-{}'.format(century, year, info[2:4], info[4:6])
        except ValueError:
            #Completely Invalid date
            pass
        for i, field in enumerate(info):
            try:
                if i < 23 or field in ('#', ' ', '|'):
                    continue
                elif i == 23:
                    yield None, 'medium', media[info[23]]
                elif i >= 24 and i <= 27:
                    yield None, self._vocab[VTYPE], types[info[i]]
                elif i == 28:
                    yield None, self._vocab[VTYPE], govt_publication[info[28]]
                elif i == 29 and field == '1':
                    yield None, self._vocab[VTYPE], 'conference-publication'
                elif i == 30 and field == '1':
                    yield None, self._vocab[VTYPE], 'festschrift'
                elif i == 33:
                    if field != 'u': #unknown
                            yield None, self._vocab[VTYPE], genres[info[33]]
                elif i == 34:
                    try:
                        yield None, self._vocab[VTYPE], biographical[info[34]]
                    except KeyError :
                        # logging.warn('something')
                        pass
                else:
                    continue
            except KeyError:
                # ':('
                pass

