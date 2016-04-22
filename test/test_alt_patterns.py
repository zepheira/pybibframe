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

from bibframe.reader import bfconvert, VTYPE_REL, PYBF_BOOTSTRAP_TARGET_REL
from bibframe.util import hash_neutral_model

from bibframe import *
from bibframe.reader.util import *

import pytest

def file_diff(s_orig, s_new):
    diff = difflib.unified_diff(s_orig.split('\n'), s_new.split('\n'))
    return '\n'.join(list(diff))

SERIES_STUB = b'''
<datafield tag="980" ind1=" " ind2=" ">
        <subfield code="a">Series</subfield>
</datafield>
'''

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


AUTH_IN_MARC_TYPES_LOOKUP = {
    'Author': 'http://example.org/vocab/Author',
    'Series': 'http://example.org/vocab/Series',
}

#There could be more than one lookup table, so it's actually a global mapping that's passed in
AUTH_IN_MARC_TYPES = 'http://example.org/vocab/authinmark#types-table'
LOOKUPS = {AUTH_IN_MARC_TYPES: AUTH_IN_MARC_TYPES_LOOKUP}


AUTHOR_IN_MARC_BOOTSTRAP = {
    '980$a': link(rel=PYBF_BOOTSTRAP_TARGET_REL, value=lookup(AUTH_IN_MARC_TYPES, target())),
    '100$a': link(rel=BL + 'name'),
}


AUTHOR_IN_MARC_MAIN = {
    '100$a': link(rel=BL + 'name'),
    '520$a': link(rel=BL + 'description'),
}


register_transforms("http://example.org/vocab/authinmark#bootstrap", AUTHOR_IN_MARC_BOOTSTRAP)
register_transforms("http://example.org/vocab/authinmark#main", AUTHOR_IN_MARC_MAIN)

AUTHOR_IN_MARC_TRANSFORMS = {
    #Start with these transforms to determine the targeted resource of the main phase
    "bootstrap": ["http://example.org/vocab/authinmark#bootstrap"],
    #If the target from the bootstrap is of this author type URL, use this specified set of patterns
    "http://example.org/vocab/Author": ["http://example.org/vocab/authinmark#main"],
}


AUTHOR_IN_MARC_EXPECTED = '''[
    [
        "1YiQn_ehZGk",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ]
]
'''

def test_author_in_marc():
    m = memory.connection()
    m_expected = memory.connection()
    s = StringIO()

    config = {'transforms': AUTHOR_IN_MARC_TRANSFORMS, 'lookups': LOOKUPS}
    bfconvert([BytesIO(AUTHOR_IN_MARC)], model=m, out=s, config=config, canonical=True)
    s.seek(0)
    hashmap, m = hash_neutral_model(s)
    hashmap = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap.items() ]))

    hashmap_expected, m_expected = hash_neutral_model(StringIO(AUTHOR_IN_MARC_EXPECTED))
    hashmap_expected = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap_expected.items() ]))

    assert hashmap == hashmap_expected, "Changes to hashes found:\n{0}\n\nActual model structure diff:\n{0}".format(file_diff(hashmap_expected, hashmap), file_diff(repr(m_expected), repr(m)))
    assert m == m_expected, "Discrepancies found:\n{0}".format(file_diff(repr(m_expected), repr(m)))


if __name__ == '__main__':
    raise SystemExit("use py.test")
