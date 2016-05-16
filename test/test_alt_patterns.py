'''

Requires http://pytest.org/ e.g.:

pip install pytest

----
'''

import sys
import logging
import asyncio
import difflib
from io import StringIO, BytesIO

from amara3.inputsource import factory, inputsource

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader import bfconvert, merge_transform_lookups, VTYPE_REL, PYBF_BOOTSTRAP_TARGET_REL, DEFAULT_MAIN_PHASE
from bibframe.util import hash_neutral_model

from bibframe import *
from bibframe.reader.util import *
from bibframe.reader.marcpatterns import BFLITE_TRANSFORMS_ID, MARC_TRANSFORMS_ID
from bibframe.reader.marcworkidpatterns import WORK_HASH_TRANSFORMS

import pytest


def file_diff(s_orig, s_new):
    diff = difflib.unified_diff(s_orig.split('\n'), s_new.split('\n'))
    return '\n'.join(list(diff))

logging.getLogger(__name__).setLevel(logging.DEBUG)

#Start here for the example of patterns for non-bibliographic data

AUTHOR_IN_MARC = b'''
<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
        <leader>00000nam  2200000   4500</leader>
        <controlfield tag="001">1024966</controlfield>
        <controlfield tag="008">030214s2003    nyu    d      000 1 eng||</controlfield>
        <datafield tag="040" ind1=" " ind2=" ">
            <subfield code="d">NOV</subfield>
            <subfield code="d">BT</subfield>
        </datafield>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Rowling, J. K.</subfield>
        </datafield>
        <datafield tag="249" ind1=" " ind2="0">
            <subfield code="a">Harry Potter and the Order of the Phoenix</subfield>
            <subfield code="c">2003</subfield>
            <subfield code="t">119344</subfield>
            <subfield code="r">2</subfield>
        </datafield>
        <datafield tag="440" ind1=" " ind2=" ">
            <subfield code="a">Harry Potter series</subfield>
            <subfield code="s">756579</subfield>
        </datafield>
        <datafield tag="520" ind1=" " ind2=" ">
            <subfield code="a">British author J.K. Rowling is best known for her fantasy series for older kids in which an orphaned boy discovers he's a wizard destined to be a hero. Popular with a wide age-range of readers, they include a large cast of highly developed characters living in a cleverly detailed and often amusing wizarding world, propelled by an engaging, fast-paced plot. Her character-driven adult fiction is equally detailed, and also concerns power struggles. She also writes mysteries under the name Robert Galbraith. Start with: The Casual Vacancy (Adults); Harry Potter and the Sorcerer's Stone (Older Kids).</subfield>
        </datafield>
        <datafield tag="650" ind1=" " ind2=" ">
            <subfield code="a">Magic</subfield>
            <subfield code="x">Study and teaching</subfield>
            <subfield code="9"> 23.44121</subfield>
        </datafield>
        <datafield tag="961" ind1=" " ind2=" ">
            <subfield code="u">http://www.jkrowling.com/</subfield>
            <subfield code="y">J. K. Rowling's Web Site</subfield>
            <subfield code="z"> : Author shares information about herself, her books, and addresses rumors.</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">Author</subfield>
        </datafield>
        <datafield tag="994" ind1=" " ind2=" ">
            <subfield code="a">572810</subfield>
            <subfield code="b">5</subfield>
            <subfield code="c">99</subfield>
        </datafield>
    </record>
</collection>
'''

#Utility lookup since the type info is in simple string info within the subfield text
AUTH_IN_MARC_TYPES_LOOKUP = {
    'Author': BL+'Person',
    'Series': BL+'Series',
}

#What's actually passed into config is set of tables, identified (and invoked) by URI keys
#After all, Could be more than one lookup table used
AUTH_IN_MARC_TYPES = 'http://example.org/vocab/authinmark#types-table'
LOOKUPS = {AUTH_IN_MARC_TYPES: AUTH_IN_MARC_TYPES_LOOKUP}

#First, bootstrap phase is used to designate the resource being described
AUTHOR_IN_MARC_BOOTSTRAP = {
    #Use 980$a to designate the resource being described, by specifying its resource type (via lookup table)
    '980$a': link(rel=PYBF_BOOTSTRAP_TARGET_REL, value=lookup(AUTH_IN_MARC_TYPES, target())),
    #All other output links become inputs to the hash ID of the described resource
    '100$a': link(rel=BL + 'name'),
}

AUTHOR_IN_MARC_BOOTSTRAP_PLUS_BIB = merge_transform_lookups(WORK_HASH_TRANSFORMS, AUTHOR_IN_MARC_BOOTSTRAP)

#Getting reliable hashes requires controlling the order of relationships used to compute the hash
#Each bootstrap phase transform set is actually a pair witht he transforms and a mapping of target resource types to hash output relationship ordering
AUTHOR_IN_MARC_HASH_ORDERING = {
    BL+'Person': [BL + 'name'],
}

#Main phase describes the resource designated in the bootstrap phase
AUTHOR_IN_MARC_MAIN = {
    '100$a': link(rel=BL + 'name'),
    '520$a': link(rel=BL + 'description'),
}

#Register these transform sets so they can be invoked by URL in config
register_transforms("http://example.org/vocab/authinmark#bootstrap", AUTHOR_IN_MARC_BOOTSTRAP, AUTHOR_IN_MARC_HASH_ORDERING)
register_transforms("http://example.org/vocab/authinmark#bootstrap-plus-bib", AUTHOR_IN_MARC_BOOTSTRAP_PLUS_BIB, AUTHOR_IN_MARC_HASH_ORDERING)
register_transforms("http://example.org/vocab/authinmark#main", AUTHOR_IN_MARC_MAIN)

#Need to specify both phases in config
AUTHOR_IN_MARC_TRANSFORMS = {
    #Start with these transforms to determine the targeted resource of the main phase
    "bootstrap": ["http://example.org/vocab/authinmark#bootstrap"],
    #If the target from the bootstrap is of this author type URL, use this specified set of patterns
    BL+'Person': ["http://example.org/vocab/authinmark#main"],
}

AUTHOR_IN_MARC_TRANSFORMS_PLUS_BIB = {
    #Start with these transforms to determine the targeted resource of the main phase
    "bootstrap": ["http://example.org/vocab/authinmark#bootstrap-plus-bib"],
    #If the target from the bootstrap is of this author type URL, use this specified set of patterns
    BL+'Person': ["http://example.org/vocab/authinmark#main"],
}


AUTHOR_IN_MARC_CONFIG = {'transforms': AUTHOR_IN_MARC_TRANSFORMS, 'lookups': LOOKUPS}

AUTHOR_IN_MARC_EXPECTED = '''[
    [
        "djDZl1J0kY8",
        "http://bibfra.me/vocab/lite/description",
        "British author J.K. Rowling is best known for her fantasy series for older kids in which an orphaned boy discovers he's a wizard destined to be a hero. Popular with a wide age-range of readers, they include a large cast of highly developed characters living in a cleverly detailed and often amusing wizarding world, propelled by an engaging, fast-paced plot. Her character-driven adult fiction is equally detailed, and also concerns power struggles. She also writes mysteries under the name Robert Galbraith. Start with: The Casual Vacancy (Adults); Harry Potter and the Sorcerer's Stone (Older Kids).",
        {}
    ],
    [
        "djDZl1J0kY8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "djDZl1J0kY8",
        "http://bibfra.me/vocab/lite/name",
        "Rowling, J. K.",
        {}
    ]
]
'''

def test_author_in_marc():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    m = memory.connection()
    m_expected = memory.connection()
    s = StringIO()

    bfconvert([BytesIO(AUTHOR_IN_MARC)], model=m, out=s, config=AUTHOR_IN_MARC_CONFIG, canonical=True, loop=loop)
    s.seek(0)

    #with open('/tmp/foo.versa.json', 'w') as f:
    #    f.write(s.read())
    #s.seek(0)

    #sys.exit(-1)

    hashmap, m = hash_neutral_model(s)
    hashmap = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap.items() ]))

    removals = []
    #Strip out tag-XXX relationships
    for ix, (o, r, t, a) in m:
        #logging.debug(r)
        if r.startswith('http://bibfra.me/vocab/marcext/tag-') or r.startswith('http://bibfra.me/vocab/marcext/sf-'):
            removals.append(ix)
    m.remove(removals)

    #with open('/tmp/foo.versa.json', 'w') as f:
    #    f.write(repr(m))

    hashmap_expected, m_expected = hash_neutral_model(StringIO(AUTHOR_IN_MARC_EXPECTED))
    hashmap_expected = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap_expected.items() ]))

    assert hashmap == hashmap_expected, "Changes to hashes found:\n{0}\n\nActual model structure diff:\n{0}".format(file_diff(hashmap_expected, hashmap), file_diff(repr(m_expected), repr(m)))
    assert m == m_expected, "Discrepancies found:\n{0}".format(file_diff(repr(m_expected), repr(m)))


#Just test/resource/zweig.mrx
REGULAR_MARC_EXAMPLE = b'''<?xml version="1.0" encoding="UTF-8" ?><marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
<marc:record><marc:leader>03531cgm a2200709Ia 4500</marc:leader>
<marc:datafield tag="245" ind1="0" ind2="0"><marc:subfield code="a">Letter from an unknown woman</marc:subfield><marc:subfield code="h">[videorecording] /</marc:subfield><marc:subfield code="c">Melange Pictures ; written by Howard Koch ; produced by John Houseman ; directed by Max Ophuls.</marc:subfield></marc:datafield><marc:datafield tag="600" ind1="1" ind2="0"><marc:subfield code="a">Zweig, Stefan,</marc:subfield><marc:subfield code="d">1881-1942</marc:subfield><marc:subfield code="v">Film adaptations.</marc:subfield></marc:datafield><marc:datafield tag="700" ind1="1" ind2="2"><marc:subfield code="a">Zweig, Stefan,</marc:subfield><marc:subfield code="d">1881-1942</marc:subfield><marc:subfield code="t">Briefe einer Unbekannten.</marc:subfield><marc:subfield code="l">English.</marc:subfield></marc:datafield></marc:record>
<marc:record><marc:leader>01913cam a22004814a 4500</marc:leader>
<marc:datafield tag="100" ind1="1" ind2=" "><marc:subfield code="a">Zweig, Stefan,</marc:subfield><marc:subfield code="d">1881-1942</marc:subfield></marc:datafield><marc:datafield tag="245" ind1="1" ind2="0"><marc:subfield code="a">Beware of pity /</marc:subfield><marc:subfield code="c">Stefan Zweig ; translated by Phyllis and Trevor Blewitt ; introduction by Joan Acocella.</marc:subfield></marc:datafield></marc:record>
</marc:collection>'''

#Need to specify both phases in config
WORK_FALLBACK_AUTHOR_IN_MARC_TRANSFORMS = {
    #Start with these transforms to determine the targeted resource of the main phase
    "bootstrap": ["http://example.org/vocab/authinmark#bootstrap", BFLITE_TRANSFORMS_ID, MARC_TRANSFORMS_ID],
    #If the target from the bootstrap is of this author type URL, use this specified set of patterns
    BL+'Person': ["http://example.org/vocab/authinmark#main"],
    #In the fallback case use only core BF Lite patterns, not the MARC layer as well
    DEFAULT_MAIN_PHASE: [BFLITE_TRANSFORMS_ID],
    #DEFAULT_MAIN_PHASE: [BFLITE_TRANSFORMS_ID, MARC_TRANSFORMS_ID],
}

#Need to specify both phases in config
WORK_FALLBACK_AUTHOR_IN_MARC_TRANSFORMS_PLUS_BIB = {
    #Start with these transforms to determine the targeted resource of the main phase
    "bootstrap": ["http://example.org/vocab/authinmark#bootstrap-plus-bib", BFLITE_TRANSFORMS_ID, MARC_TRANSFORMS_ID],
    #If the target from the bootstrap is of this author type URL, use this specified set of patterns
    BL+'Person': ["http://example.org/vocab/authinmark#main"],
    #In the fallback case use only core BF Lite patterns, not the MARC layer as well
    DEFAULT_MAIN_PHASE: [BFLITE_TRANSFORMS_ID],
    #DEFAULT_MAIN_PHASE: [BFLITE_TRANSFORMS_ID, MARC_TRANSFORMS_ID],
}

WORK_FALLBACK_AUTHOR_IN_MARC_CONFIG = {'transforms': WORK_FALLBACK_AUTHOR_IN_MARC_TRANSFORMS, 'lookups': LOOKUPS}

WORK_FALLBACK_AUTHOR_IN_MARC_CONFIG_PLUS_BIB = {'transforms': WORK_FALLBACK_AUTHOR_IN_MARC_TRANSFORMS_PLUS_BIB, 'lookups': LOOKUPS}


WORK_FALLBACK_AUTHOR_IN_MARC_EXPECTED = '''[
    [
        "AEftkgMSspw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "AEftkgMSspw",
        "http://bibfra.me/vocab/lite/creator",
        "bviSxLAmzYc",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "AEftkgMSspw",
        "http://bibfra.me/vocab/lite/language",
        "English.",
        {}
    ],
    [
        "AEftkgMSspw",
        "http://bibfra.me/vocab/lite/title",
        "Briefe einer Unbekannten.",
        {}
    ],
    [
        "Gsn6xQ5CxCE",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Gsn6xQ5CxCE",
        "http://bibfra.me/vocab/lite/date",
        "1881-1942",
        {}
    ],
    [
        "Gsn6xQ5CxCE",
        "http://bibfra.me/vocab/lite/focus",
        "bviSxLAmzYc",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Gsn6xQ5CxCE",
        "http://bibfra.me/vocab/lite/name",
        "Zweig, Stefan,",
        {}
    ],
    [
        "Gsn6xQ5CxCE",
        "http://bibfra.me/vocab/marc/formSubdivision",
        "Film adaptations.",
        {}
    ],
    [
        "YySXWgbJQ8Y",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YySXWgbJQ8Y",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MovingImage",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YySXWgbJQ8Y",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/VisualMaterials",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YySXWgbJQ8Y",
        "http://bibfra.me/vocab/lite/genre",
        "eWVHN_tTY6I",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YySXWgbJQ8Y",
        "http://bibfra.me/vocab/lite/related",
        "AEftkgMSspw",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YySXWgbJQ8Y",
        "http://bibfra.me/vocab/lite/subject",
        "Gsn6xQ5CxCE",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YySXWgbJQ8Y",
        "http://bibfra.me/vocab/lite/title",
        "Letter from an unknown woman",
        {}
    ],
    [
        "YySXWgbJQ8Y",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Melange Pictures ; written by Howard Koch ; produced by John Houseman ; directed by Max Ophuls.",
        {}
    ],
    [
        "bviSxLAmzYc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "bviSxLAmzYc",
        "http://bibfra.me/vocab/lite/date",
        "1881-1942",
        {}
    ],
    [
        "bviSxLAmzYc",
        "http://bibfra.me/vocab/lite/name",
        "Zweig, Stefan,",
        {}
    ],
    [
        "eWVHN_tTY6I",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Form",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "eWVHN_tTY6I",
        "http://bibfra.me/vocab/lite/name",
        "Film adaptations.",
        {}
    ],
    [
        "jgL8vvn9K-g",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "jgL8vvn9K-g",
        "http://bibfra.me/vocab/lite/instantiates",
        "YySXWgbJQ8Y",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "jgL8vvn9K-g",
        "http://bibfra.me/vocab/lite/medium",
        "[videorecording] /",
        {}
    ],
    [
        "jgL8vvn9K-g",
        "http://bibfra.me/vocab/lite/title",
        "Letter from an unknown woman",
        {}
    ],
    [
        "jgL8vvn9K-g",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Melange Pictures ; written by Howard Koch ; produced by John Houseman ; directed by Max Ophuls.",
        {}
    ],
    [
        "lqZdjJ7Mdcg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "lqZdjJ7Mdcg",
        "http://bibfra.me/vocab/lite/instantiates",
        "uYSoMuClP4k",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "lqZdjJ7Mdcg",
        "http://bibfra.me/vocab/lite/title",
        "Beware of pity /",
        {}
    ],
    [
        "lqZdjJ7Mdcg",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Stefan Zweig ; translated by Phyllis and Trevor Blewitt ; introduction by Joan Acocella.",
        {}
    ],
    [
        "uYSoMuClP4k",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uYSoMuClP4k",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uYSoMuClP4k",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uYSoMuClP4k",
        "http://bibfra.me/vocab/lite/creator",
        "bviSxLAmzYc",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uYSoMuClP4k",
        "http://bibfra.me/vocab/lite/title",
        "Beware of pity /",
        {}
    ],
    [
        "uYSoMuClP4k",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Stefan Zweig ; translated by Phyllis and Trevor Blewitt ; introduction by Joan Acocella.",
        {}
    ]
]'''


#Different initial work hashes because 100$a maps to different rel when merged in from default work hash patterns
WORK_FALLBACK_AUTHOR_IN_MARC_EXPECTED_PLUS_BIB = WORK_FALLBACK_AUTHOR_IN_MARC_EXPECTED.replace('lqZdjJ7Mdcg', '0GExrYlzZRs').replace('uYSoMuClP4k', '8MAi-oktTck')

def test_work_fallback_author_in_marc_simple():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    m = memory.connection()
    m_expected = memory.connection()
    s = StringIO()

    bfconvert([BytesIO(REGULAR_MARC_EXAMPLE)], model=m, out=s, config=WORK_FALLBACK_AUTHOR_IN_MARC_CONFIG, canonical=True, loop=loop)
    s.seek(0)

    #with open('/tmp/foo.versa.json', 'w') as f:
    #    f.write(s.read())
    #s.seek(0)

    hashmap, m = hash_neutral_model(s)
    hashmap = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap.items() ]))

    removals = []
    #Strip out tag-XXX relationships
    for ix, (o, r, t, a) in m:
        #logging.debug(r)
        if r.startswith('http://bibfra.me/vocab/marcext/tag-') or r.startswith('http://bibfra.me/vocab/marcext/sf-'):
            removals.append(ix)
    m.remove(removals)

    hashmap_expected, m_expected = hash_neutral_model(StringIO(WORK_FALLBACK_AUTHOR_IN_MARC_EXPECTED))
    hashmap_expected = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap_expected.items() ]))

    assert hashmap == hashmap_expected, "Changes to hashes found:\n{0}\n\nActual model structure diff:\n{0}".format(file_diff(hashmap_expected, hashmap), file_diff(repr(m_expected), repr(m)))
    assert m == m_expected, "Discrepancies found:\n{0}".format(file_diff(repr(m_expected), repr(m)))

AUTHOR_IN_MARC_TRANSFORMS_PLUS_BIB
def test_work_fallback_author_in_marc_with_plusbib():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    m = memory.connection()
    m_expected = memory.connection()
    s = StringIO()

    bfconvert([BytesIO(REGULAR_MARC_EXAMPLE)], model=m, out=s, config=WORK_FALLBACK_AUTHOR_IN_MARC_CONFIG_PLUS_BIB, canonical=True, loop=loop)
    s.seek(0)

    #with open('/tmp/foo.versa.json', 'w') as f:
    #    f.write(s.read())
    #s.seek(0)

    hashmap, m = hash_neutral_model(s)
    hashmap = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap.items() ]))

    removals = []
    #Strip out tag-XXX relationships
    for ix, (o, r, t, a) in m:
        #logging.debug(r)
        if r.startswith('http://bibfra.me/vocab/marcext/tag-') or r.startswith('http://bibfra.me/vocab/marcext/sf-'):
            removals.append(ix)
    m.remove(removals)

    hashmap_expected, m_expected = hash_neutral_model(StringIO(WORK_FALLBACK_AUTHOR_IN_MARC_EXPECTED_PLUS_BIB))
    hashmap_expected = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap_expected.items() ]))

    assert hashmap == hashmap_expected, "Changes to hashes found:\n{0}\n\nActual model structure diff:\n{0}".format(file_diff(hashmap_expected, hashmap), file_diff(repr(m_expected), repr(m)))
    assert m == m_expected, "Discrepancies found:\n{0}".format(file_diff(repr(m_expected), repr(m)))


if __name__ == '__main__':
    raise SystemExit("use py.test")
