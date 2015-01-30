# -*- coding: utf-8 -*-
'''
Test some small, simple MARC snippets.

Requires http://pytest.org/ e.g.:

pip install pytest

Each test case is a triple of e.g. [SNIPPET_1, CONFIG_1, EXPECTED_1]

You must have matched series each with all 3 components matched up, otherwise the entire test suite will fall over like a stack of dominoes

----

Example of how to add another test case, assumign correct pybibframe state:

import asyncio
from io import StringIO

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader.marcxml import bfconvert

SNIPPET = '<collection xmlns="http://www.loc.gov/MARC21/slim"><record><leader>...</leader></record></collection>'
CONFIG = None

loop = asyncio.new_event_loop()
asyncio.set_event_loop(None)
m = memory.connection()
instream = StringIO(SNIPPET)
outstream = StringIO()
bfconvert(instream, model=m, out=outstream, canonical=True, loop=loop)
print(outstream.getvalue()) #This output becomes the EXPECTED stanza

'''

import sys
import logging
import asyncio
import difflib
from io import StringIO

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader.marcxml import bfconvert
import bibframe.plugin

import pytest

#Bits from http://www.loc.gov/standards/marcxml/Sandburg/sandburg.xml

#Leader + 008 + 1 control
SNIPPET_1 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="001">92005291</controlfield>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
</record>
</collection>'''

CONFIG_1 = None

EXPECTED_1 = '''[
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/LanguageMaterial",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/encyclopedias",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/legal-articles",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/surveys-of-literature",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ]
]
'''

#Leader + 008 + 1 data
SNIPPET_2 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Arithmetic /</subfield>
    <subfield code="c">Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.</subfield>
  </datafield>
</record>
</collection>'''

CONFIG_2 = None

EXPECTED_2 = '''[
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/LanguageMaterial",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/encyclopedias",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/legal-articles",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/surveys-of-literature",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/vocab/marc/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/vocab/rda/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/vocab/lite/instantiates",
        "X76tY3SC",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/vocab/rda/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ]
]
'''

#Leader + 008 + 1 control + 1 data field
SNIPPET_3 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="001">92005291</controlfield>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Arithmetic /</subfield>
    <subfield code="c">Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.</subfield>
  </datafield>
</record>
</collection>'''

CONFIG_3 = None

EXPECTED_3 = '''[
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/LanguageMaterial",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/encyclopedias",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/legal-articles",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/surveys-of-literature",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/vocab/marc/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "X76tY3SC",
        "http://bibfra.me/vocab/rda/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/vocab/lite/instantiates",
        "X76tY3SC",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "bwbrjGVf",
        "http://bibfra.me/vocab/rda/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ]
]
'''

SNIPPET_4 = SNIPPET_1

CONFIG_4 = {
    "plugins": [
        {"id": "http://bibfra.me/tool/pybibframe#labelizer",
                "lookup": {
                    "http://bibfra.me/vocab/lite/Work": "http://bibfra.me/vocab/lite/title",
                    "http://bibfra.me/vocab/lite/Instance": "http://bibfra.me/vocab/lite/title",
                    "http://bibfra.me/vocab/lite/Agent": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Person": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Organization": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Place": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Collection": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Meeting": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Topic": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Genre": "http://bibfra.me/vocab/lite/name"}
                }
    ]
}

EXPECTED_4 = '''[
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/LanguageMaterial",
        {}
    ],
    [
        "kP2G4QhW",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/encyclopedias",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/legal-articles",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/surveys-of-literature",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ]
]
'''

SNIPPET_5 = '''<record xmlns="http://www.loc.gov/MARC21/slim">
<leader>02915cam a2200601 a 4500</leader>
<controlfield tag="008">020613s1860 ja a 000 0 jpn</controlfield>
<datafield tag="245" ind1="1" ind2="0">
  <subfield code="6">880-02</subfield>
  <subfield code="a">Ishinpō /</subfield>
  <subfield code="c">Tanba no Sukune Yasuyori sen.</subfield>
</datafield>
<datafield tag="880" ind1="1" ind2="0">
  <subfield code="6">245-02/$1</subfield>
  <subfield code="a">醫心方 /</subfield>
  <subfield code="c">丹波宿袮康頼撰.</subfield>
</datafield>
</record>
'''

CONFIG_5 = None

EXPECTED_5 = '''[
    [
        "nFBFsha6",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/LanguageMaterial",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/programmed-texts",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/surveys-of-literature",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/vocab/lite/title",
        "Ishinp\u014d /",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/vocab/lite/title",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/vocab/marc/tag-008",
        "020613s1860 ja a 000 0 jpn",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/vocab/marc/tag-880-10-6",
        "245-02/$1",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/vocab/marc/tag-880-10-a",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/vocab/marc/tag-880-10-c",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/vocab/rda/titleStatement",
        "Tanba no Sukune Yasuyori sen.",
        {}
    ],
    [
        "nFBFsha6",
        "http://bibfra.me/vocab/rda/titleStatement",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ],
    [
        "zRg2BG3T",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {}
    ],
    [
        "zRg2BG3T",
        "http://bibfra.me/vocab/lite/instantiates",
        "nFBFsha6",
        {}
    ],
    [
        "zRg2BG3T",
        "http://bibfra.me/vocab/lite/title",
        "Ishinp\u014d /",
        {}
    ],
    [
        "zRg2BG3T",
        "http://bibfra.me/vocab/lite/title",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "zRg2BG3T",
        "http://bibfra.me/vocab/rda/titleStatement",
        "Tanba no Sukune Yasuyori sen.",
        {}
    ],
    [
        "zRg2BG3T",
        "http://bibfra.me/vocab/rda/titleStatement",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ]
]
'''

#Test the uncombined version of the character after testing the combined one
#Another useful test would be using e.g. '\u2166', which is NFKC normalized to 3 separate characters VII
SNIPPET_6 = SNIPPET_5.replace('ō', 'ō')

CONFIG_6 = None

EXPECTED_6 = EXPECTED_5

all_snippets = sorted([ sym for sym in globals() if sym.startswith('SNIPPET') ])
all_config = sorted([ sym for sym in globals() if sym.startswith('CONFIG') ])
all_expected = sorted([ sym for sym in globals() if sym.startswith('EXPECTED') ])

all_snippets = [ globals()[sym] for sym in all_snippets ]
all_config = [ globals()[sym] for sym in all_config ]
all_expected = [ globals()[sym] for sym in all_expected ]

def file_diff(s_orig, s_new):
    diff = difflib.unified_diff(s_orig.split('\n'), s_new.split('\n'))
    return '\n'.join(list(diff))


def run_one(snippet, expected, entbase=None, config=None, loop=None, canonical=True):
    m = memory.connection()
    m_expected = memory.connection()
    instream = StringIO(snippet)
    outstream = StringIO()
    bfconvert(instream, model=m, out=outstream, config=config, canonical=canonical, loop=loop)
    outstream.seek(0)
    jsonload(m, outstream)

    expected_stream = StringIO(expected)
    jsonload(m_expected, expected_stream)

    assert m == m_expected, "Discrepancies found:\n{0}".format(file_diff(repr(m_expected), repr(m)))


@pytest.mark.parametrize('snippet, config, expected', zip(all_snippets, all_config, all_expected))
def test_snippets(snippet, config, expected):
    #Use a new event loop per test instance, and so one call of bfconvert per test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    run_one(snippet, expected, config=config, loop=loop)


if __name__ == '__main__':
    raise SystemExit("use py.test")

