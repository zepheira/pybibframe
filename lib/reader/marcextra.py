'''
Treatment of certain special MARC fields, leader and 008
'''

#TODO: Also split on multiple 260 fields

def process_leader(leader):
    """
    http://www.loc.gov/marc/marc2dc.html#ldr06conversionrules
    http://www.loc.gov/marc/bibliographic/bdleader.html

    >>> from btframework.marc import process_leader
    >>> list(process_leader('03495cpcaa2200673 a 4500'))
    [('resourceType', 'Collection'), ('resourceType', 'mixed materials'), ('resourceType', 'Collection')]
    """
    broad_06 = dict(
        a="LanguageMaterial",
        c="LanguageMaterial",
        d="LanguageMaterial",
        e="StillImage",
        f="StillImage",
        g="MovingImage",
        i="Audio",
        j="Audio",
        k="StillImage",
        m="Software",
        p="Collection",
        t="LanguageMaterial")
    
    detailed_06 = dict(
        a="LanguageMaterial",
        c="NotatedMusic",
        d="Manuscript+NotatedMusic",
        e="Cartography",
        f="Manuscript+Cartography",
        g="MovingImage",
        i="Nonmusical+Sounds",
        j="Musical",
        k="StillImage",
        m="Multimedia",
        o="Kit",
        p="Multimedia",
        r="ThreeDimensionalObject",
        t="LanguageMaterial+Manuscript")
    
    _06 = leader[6]
    if _06 in broad_06.keys():
        yield 'resourceType', broad_06[_06]
    if _06 in detailed_06.keys():
        yield 'resourceType', detailed_06[_06]
    if leader[7] in ('c', 's'):
        yield 'resourceType', 'Collection'


def process_008(info):
    """
    http://www.loc.gov/marc/umb/um07to10.html#part9

    >>> from btframework.marc import process_008
    >>> list(process_008('790726||||||||||||                 eng  '))
    [('date', '1979-07-26')]
    """
    audiences = {
        'a':'preschool',
        'b':'primary',
        'c':'pre-adolescent',
        'd':'adolescent',
        'e':'adult',
        'f':'specialized',
        'g':'general',
        'j':'juvenile'}

    media = {
        'a':'microfilm',
        'b':'microfiche',
        'c':'microopaque',
        'd':'large print',
        'f':'braille',
        'r':'regular print reproduction',
        's':'electronic'
        }

    types = {
        "a":"abstracts/summaries",
        "b":"bibliographies (is one or contains one)",
        "c":"catalogs",
        "d":"dictionaries",
        "e":"encyclopedias",
        "f":"handbooks",
        "g":"legal articles",
        "i":"indexes",
        "j":"patent document",
        "k":"discographies",
        "l":"legislation",
        "m":"theses",
        "n":"surveys of literature",
        "o":"reviews",
        "p":"programmed texts",
        "q":"filmographies",
        "r":"directories",
        "s":"statistics",
        "t":"technical reports",
        "u":"standards/specifications",
        "v":"legal cases and notes",
        "w":"law reports and digests",
        "z":"treaties"}
    
    govt_publication = {
        "i":"international or intergovernmental publication",
        "f":"federal/national government publication",
        "a":"publication of autonomous or semi-autonomous component of government",
        "s":"government publication of a state, province, territory, dependency, etc.",
        "m":"multistate government publication",
        "c": "publication from multiple local governments",
        "l": "local government publication",
        "z":"other type of government publication",
        "o":"government publication -- level undetermined",
        "u":"unknown if item is government publication"}

    genres = {
        "0":"not fiction",
        "1":"fiction",
        "c":"comic strips",
        "d":"dramas",
        "e":"essays",
        "f":"novels",
        "h":"humor, satires, etc.",
        "i":"letters",
        "j":"short stories",
        "m":"mixed forms",
        "p":"poetry",
        "s":"speeches"}

    biographical = dict(
        a="autobiography",
        b='individual biography',
        c='collective biography',
        d='contains biographical information')
    
    #info = field008
    #ARE YOU FRIGGING KIDDING ME?! NON-Y2K SAFE?!
    year = info[0:2]
    try:
        century = '19' if int(year) > 30 else '20' #I guess we can give an 18 year berth before this breaks ;)
        yield 'date_008', '{}{}-{}-{}'.format(century, year, info[2:4], info[4:6])
    except ValueError:
        pass
        #Completely Invalid date
    for i, field in enumerate(info):
        try:
            if i < 23 or field in ('#',  ' ', '|'):
                continue
            elif i == 23:
                yield 'medium', media[info[23]]
            elif i >= 24 and i <= 27:
                yield 'resourceType', types[info[i]]
            elif i == 28:
                yield 'resourceType', govt_publication[info[28]]
            elif i == 29 and field == '1':
                yield 'resourceType', 'conference publication'
            elif i == 30 and field == '1':
                yield 'resourceType', 'festschrift'
            elif i == 33:
                if field != 'u': #unknown
                        yield 'resourceType', genres[info[33]]
            elif i == 34:
                try:
                    yield 'resourceType', biographical[info[34]]
                except KeyError :
                    # logging.warn('something')
                    pass
            else:
                continue
        except KeyError:
            # ':('
            pass

#TODO languages

