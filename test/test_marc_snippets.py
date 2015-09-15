# -*- coding: utf-8 -*-
'''
Test some small, simple MARC snippets.

Requires http://pytest.org/ e.g.:

pip install pytest

Each test case is a triple of e.g. [SNIPPET_1, CONFIG_1, EXPECTED_1]

You must have matched series each with all 3 components matched up, otherwise the entire test suite will fall over like a stack of dominoes

----

Recipe for regenerating the test case expected outputs:

python -i test/test_marc_snippets.py #Ignore the SystemExit

Then:

all_snippets = sorted([ sym for sym in globals() if sym.startswith('SNIPPET') ])
all_config = sorted([ sym for sym in globals() if sym.startswith('CONFIG') ])
all_expected = sorted([ sym for sym in globals() if sym.startswith('EXPECTED') ])

for s, c, e in zip(all_snippets, all_config, all_expected):
    sobj, cobj, eobj = globals()[s], globals()[c], globals()[e]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    m = memory.connection()
    instream = BytesIO(sobj.encode('utf-8'))
    outstream = StringIO()
    bfconvert(factory(instream), model=m, out=outstream, config=cobj, canonical=True, loop=loop)
    print('EXPECTED from {0}:'.format(s))
    print(outstream.getvalue()) #This output becomes the EXPECTED stanza

'''

import sys
import logging
import asyncio
import difflib
from io import StringIO, BytesIO
import tempfile

from amara3.inputsource import factory

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader import bfconvert
import bibframe.plugin
from bibframe.util import hash_neutral_model

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

EXPECTED_1 = '''
[
    [
        "NouDokf-xFo",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "v1XyZK1wpsE",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "v1XyZK1wpsE",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "v1XyZK1wpsE",
        "http://bibfra.me/vocab/lite/instantiates",
        "NouDokf-xFo",
        {
            "@target-type": "@iri-ref"
        }
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

EXPECTED_2 = '''
[
    [
        "PanWwf3I97w",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PanWwf3I97w",
        "http://bibfra.me/vocab/lite/instantiates",
        "h58F-0EmyII",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PanWwf3I97w",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "PanWwf3I97w",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
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

EXPECTED_3 = '''
[
    [
        "PanWwf3I97w",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PanWwf3I97w",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "PanWwf3I97w",
        "http://bibfra.me/vocab/lite/instantiates",
        "h58F-0EmyII",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PanWwf3I97w",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "PanWwf3I97w",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "h58F-0EmyII",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
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

EXPECTED_4 = '''
[
    [
        "NouDokf-xFo",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "NouDokf-xFo",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "v1XyZK1wpsE",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "v1XyZK1wpsE",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "v1XyZK1wpsE",
        "http://bibfra.me/vocab/lite/instantiates",
        "NouDokf-xFo",
        {
            "@target-type": "@iri-ref"
        }
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

EXPECTED_5 = '''
[
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/lite/title",
        "Ishinp\u014d /",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/lite/title",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "programmed texts",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Tanba no Sukune Yasuyori sen.",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/marc/titleStatement",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/marcext/tag-008",
        "020613s1860 ja a 000 0 jpn",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/marcext/tag-880-10-6",
        "245-02/$1",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/marcext/tag-880-10-a",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "pYh90ts1NyQ",
        "http://bibfra.me/vocab/marcext/tag-880-10-c",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ],
    [
        "tqvQ2cRw2BQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "tqvQ2cRw2BQ",
        "http://bibfra.me/vocab/lite/instantiates",
        "pYh90ts1NyQ",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "tqvQ2cRw2BQ",
        "http://bibfra.me/vocab/lite/title",
        "Ishinp\u014d /",
        {}
    ],
    [
        "tqvQ2cRw2BQ",
        "http://bibfra.me/vocab/lite/title",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "tqvQ2cRw2BQ",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Tanba no Sukune Yasuyori sen.",
        {}
    ],
    [
        "tqvQ2cRw2BQ",
        "http://bibfra.me/vocab/marc/titleStatement",
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

SNIPPET_7 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
  <datafield tag="100" ind1="1" ind2=" ">
    <subfield code="a">Sandburg, Carl,</subfield>
    <subfield code="d">1878-1967.</subfield>
  </datafield>
  </record>
</collection>'''

CONFIG_7 = None

EXPECTED_7 = '''
[
    [
        "OgrstWjgDTA",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "OgrstWjgDTA",
        "http://bibfra.me/vocab/lite/instantiates",
        "gG4c5Mo7VN4",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gG4c5Mo7VN4",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gG4c5Mo7VN4",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gG4c5Mo7VN4",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gG4c5Mo7VN4",
        "http://bibfra.me/vocab/lite/creator",
        "sgr9kXobvQA",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gG4c5Mo7VN4",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "gG4c5Mo7VN4",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "gG4c5Mo7VN4",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "gG4c5Mo7VN4",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "sgr9kXobvQA",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "sgr9kXobvQA",
        "http://bibfra.me/vocab/lite/date",
        "1878-1967.",
        {}
    ],
    [
        "sgr9kXobvQA",
        "http://bibfra.me/vocab/lite/name",
        "Sandburg, Carl,",
        {}
    ],
    [
        "sgr9kXobvQA",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Sandburg, Carl,",
        {}
    ],
    [
        "sgr9kXobvQA",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1878-1967.",
        {}
    ]
]
'''

SNIPPET_8 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>02415cas a2200637 a 4500</leader>
  <controlfield tag="008">010806c20019999ru br p       0   a0eng d</controlfield>
  <datafield tag="780" ind1="1" ind2="4">
    <subfield code="t">Doklady biochemistry</subfield>
    <subfield code="x">0012-4958</subfield>
    <subfield code="w">(DLC)   96646621</subfield>
    <subfield code="w">(OCoLC)1478787</subfield>
    <subfield code="w">(DNLM)7505458</subfield>
  </datafield>
  </record>
</collection>'''

CONFIG_8 = None

EXPECTED_8 = '''
[
    [
        "MNjNtudJQrA",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "MNjNtudJQrA",
        "http://bibfra.me/vocab/lite/instantiates",
        "sqGEfrw0oik",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/vocab/marc/characteristic",
        "periodical",
        {}
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/vocab/marc/frequency",
        "bimonthly",
        {}
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/vocab/marc/originalAlphabetOrScriptOfTitle",
        "basic roman",
        {}
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/vocab/marc/regularity",
        "regular",
        {}
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/vocab/marcext/tag-008",
        "010806c20019999ru br p       0   a0eng d",
        {}
    ],
    [
        "sqGEfrw0oik",
        "http://bibfra.me/vocab/relation/unionOf",
        "zRQW4379QEs",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://lccn.loc.gov/96646621",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://www.ncbi.nlm.nih.gov/nlmcatalog?term=7505458",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://www.worldcat.org/oclc/1478787",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/marc/issn",
        "0012-4958",
        {}
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/marcext/sf-t",
        "Doklady biochemistry",
        {}
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(DLC)   96646621",
        {}
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(DNLM)7505458",
        {}
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(OCoLC)1478787",
        {}
    ],
    [
        "zRQW4379QEs",
        "http://bibfra.me/vocab/marcext/sf-x",
        "0012-4958",
        {}
    ]
]
'''

#Leader + 008 + 1 data
SNIPPET_9 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01025cas a22003251  4500</leader>
  <controlfield tag="008">821218d18821919ja uu p       0||||0jpn b</controlfield>
  <datafield tag="260" ind1=" " ind2=" ">
      <subfield code="a">Tokyo.</subfield>
  </datafield>
</record>
</collection>'''

CONFIG_9 = None

EXPECTED_9 = '''
[
    [
        "FY7LsglzmTY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/vocab/lite/language",
        "jpn",
        {}
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/vocab/marc/characteristic",
        "periodical",
        {}
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/vocab/marc/frequency",
        "unknown",
        {}
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/vocab/marc/regularity",
        "unknown",
        {}
    ],
    [
        "FY7LsglzmTY",
        "http://bibfra.me/vocab/marcext/tag-008",
        "821218d18821919ja uu p       0||||0jpn b",
        {}
    ],
    [
        "WSlIR8368a8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Agent",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WSlIR8368a8",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Tokyo.",
        {}
    ],
    [
        "_mMAJ9x4VJE",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/ProviderEvent",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_mMAJ9x4VJE",
        "http://bibfra.me/vocab/lite/providerAgent",
        "WSlIR8368a8",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_mMAJ9x4VJE",
        "http://bibfra.me/vocab/lite/providerPlace",
        "uyjKUm6vQ_0",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_mMAJ9x4VJE",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Tokyo.",
        {}
    ],
    [
        "ipQLD2eCpyw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ipQLD2eCpyw",
        "http://bibfra.me/vocab/lite/instantiates",
        "FY7LsglzmTY",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ipQLD2eCpyw",
        "http://bibfra.me/vocab/marc/publication",
        "_mMAJ9x4VJE",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uyjKUm6vQ_0",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Place",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uyjKUm6vQ_0",
        "http://bibfra.me/vocab/lite/name",
        "Tokyo.",
        {}
    ],
    [
        "uyjKUm6vQ_0",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Tokyo.",
        {}
    ]
]
'''

SNIPPET_10 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>02386cas a2200637 a 4500</leader>
  <controlfield tag="001">37263290</controlfield>
  <controlfield tag="003">OCoLC</controlfield>
  <controlfield tag="005">20141208144405.0</controlfield>
  <controlfield tag="006">m     o  d f      </controlfield>
  <controlfield tag="007">cr gn|||||||||</controlfield>
  <controlfield tag="008">970709c19679999dcugr   o hr f0   a0eng  </controlfield>
</record></collection>
'''

CONFIG_10 = {}

EXPECTED_10 = '''
[
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marc/frequency",
        "biennial",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marc/governmentPublication",
        "federal national government publication",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "dictionaries",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "directories",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marc/originalAlphabetOrScriptOfTitle",
        "basic roman",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marc/regularity",
        "regular",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marcext/tag-003",
        "OCoLC",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marcext/tag-005",
        "20141208144405.0",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marcext/tag-006",
        "m     o  d f      ",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marcext/tag-007",
        "cr gn|||||||||",
        {}
    ],
    [
        "Vlu2XkBEtAg",
        "http://bibfra.me/vocab/marcext/tag-008",
        "970709c19679999dcugr   o hr f0   a0eng  ",
        {}
    ],
    [
        "YpqZjCgKPkk",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YpqZjCgKPkk",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ElectronicResource",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YpqZjCgKPkk",
        "http://bibfra.me/vocab/lite/controlCode",
        "37263290",
        {}
    ],
    [
        "YpqZjCgKPkk",
        "http://bibfra.me/vocab/lite/instantiates",
        "Vlu2XkBEtAg",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YpqZjCgKPkk",
        "http://bibfra.me/vocab/marc/dimensions",
        "unknown",
        {}
    ],
    [
        "YpqZjCgKPkk",
        "http://bibfra.me/vocab/marc/formOfItem",
        "online",
        {}
    ],
    [
        "YpqZjCgKPkk",
        "http://bibfra.me/vocab/marc/specificMaterialDesignation",
        "remote",
        {}
    ]
]
'''

# a couple degenerate cases
SNIPPET_11 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
<record xmlns="http://www.loc.gov/MARC21/slim"><leader>00000ngm a2200000Ka 4500</leader><controlfield tag="001">881466</controlfield></record>
</collection>
'''

CONFIG_11 = {}

EXPECTED_11 = '''
[
    [
        "8T9lplbpAV8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/vocab/lite/controlCode",
        "881466",
        {}
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/vocab/lite/instantiates",
        "Vgjhhv2QmbI",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vgjhhv2QmbI",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vgjhhv2QmbI",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MovingImage",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vgjhhv2QmbI",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/VisualMaterials",
        {
            "@target-type": "@iri-ref"
        }
    ]
]
'''

SNIPPET_12 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
<record><controlfield tag="001">881466</controlfield></record>
</collection>
'''

CONFIG_12 = {}

EXPECTED_12 = '''
[
    [
        "8T9lplbpAV8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/vocab/lite/controlCode",
        "881466",
        {}
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/vocab/lite/instantiates",
        "Vgjhhv2QmbI",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vgjhhv2QmbI",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ]
]
'''

SNIPPET_13 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <leader>02173pam a22004694a 4500</leader>
    <controlfield tag="001">1247500</controlfield>
    <controlfield tag="008">050506s2005    gw a     b    001 0 eng  </controlfield>
    <datafield tag="020" ind1=" " ind2=" ">
      <subfield code="a">9783136128046 (GTV)</subfield>
    </datafield>
    <datafield tag="020" ind1=" " ind2=" ">
      <subfield code="a">3136128044 (GTV)</subfield>
    </datafield>
    <datafield tag="020" ind1=" " ind2=" ">
      <subfield code="a">9781588902153 (TNY)</subfield>
    </datafield>
    <datafield tag="020" ind1=" " ind2=" ">
      <subfield code="a">1588902153 (TNY)</subfield>
    </datafield>
  </record>
</collection>
'''

CONFIG_13 = {}

EXPECTED_13 = '''
[
    [
        "74F9_XRBVT0",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "74F9_XRBVT0",
        "http://bibfra.me/vocab/lite/controlCode",
        "1247500",
        {}
    ],
    [
        "74F9_XRBVT0",
        "http://bibfra.me/vocab/lite/instantiates",
        "cqVVTvjtB-0",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "74F9_XRBVT0",
        "http://bibfra.me/vocab/marc/isbn",
        "9783136128046",
        {}
    ],
    [
        "74F9_XRBVT0",
        "http://bibfra.me/vocab/marc/isbnType",
        "(GTV)",
        {}
    ],
    [
        "ZQ2iZK4O8gw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ZQ2iZK4O8gw",
        "http://bibfra.me/vocab/lite/controlCode",
        "1247500",
        {}
    ],
    [
        "ZQ2iZK4O8gw",
        "http://bibfra.me/vocab/lite/instantiates",
        "cqVVTvjtB-0",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ZQ2iZK4O8gw",
        "http://bibfra.me/vocab/marc/isbn",
        "9781588902153",
        {}
    ],
    [
        "ZQ2iZK4O8gw",
        "http://bibfra.me/vocab/marc/isbnType",
        "(TNY)",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marc/illustrations",
        "illustrations",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marc/index",
        "index present",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marc/literaryForm",
        "non fiction",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "bibliography",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marcext/tag-008",
        "050506s2005    gw a     b    001 0 eng  ",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "1588902153 (TNY)",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "3136128044 (GTV)",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "9781588902153 (TNY)",
        {}
    ],
    [
        "cqVVTvjtB-0",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "9783136128046 (GTV)",
        {}
    ]
]
'''

# authority link syntax
SNIPPET_14 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <leader>02467cam a2200505 a 4500</leader>
    <datafield tag="100" ind1="1" ind2=" ">
      <subfield code="a">Austen, Jane,</subfield>
      <subfield code="0">http://id.loc.gov/authorities/names/n79032879</subfield>
      <subfield code="0">(ZZZ)x9898989898</subfield>
      <subfield code="0">(ZZZ)  x9898989898</subfield>
      <subfield code="0">(ZZZ)  Ishinp\u014d /</subfield>
      <subfield code="0">http://viaf.org/viaf/102333412</subfield>
      <subfield code="0">(viaf)102333412</subfield>
    </datafield>
  </record>
</collection>
'''

CONFIG_14 = {}

EXPECTED_14 = '''
[
    [
        "fcH68OIIhv0",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/%28ZZZ%29%20%20Ishinp%C5%8D%20%2F",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/%28ZZZ%29%20%20x9898989898",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/(ZZZ)x9898989898",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/n79032879",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://viaf.org/viaf/102333412",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)  Ishinp\u014d /",
        {}
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)  x9898989898",
        {}
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)x9898989898",
        {}
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "fcH68OIIhv0",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "kWESATjOekw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kWESATjOekw",
        "http://bibfra.me/vocab/lite/instantiates",
        "n09KVR0-HI8",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "n09KVR0-HI8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "n09KVR0-HI8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "n09KVR0-HI8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "n09KVR0-HI8",
        "http://bibfra.me/vocab/lite/creator",
        "fcH68OIIhv0",
        {
            "@target-type": "@iri-ref"
        }
    ]
]
'''

# some dates in a fixed length field
SNIPPET_15 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <controlfield tag="007">m                1992</controlfield>
    <controlfield tag="007">m                1993--</controlfield>
    <controlfield tag="007">m                199402</controlfield>
  </record>
</collection>
'''

CONFIG_15 = {}

EXPECTED_15 = '''
[
    [
        "8T9lplbpAV8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MotionPicture",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/vocab/lite/instantiates",
        "Vgjhhv2QmbI",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1992",
        {}
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1993",
        {}
    ],
    [
        "8T9lplbpAV8",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1994-02",
        {}
    ],
    [
        "Vgjhhv2QmbI",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Vgjhhv2QmbI",
        "http://bibfra.me/vocab/marcext/tag-007",
        "m                1992",
        {}
    ],
    [
        "Vgjhhv2QmbI",
        "http://bibfra.me/vocab/marcext/tag-007",
        "m                1993--",
        {}
    ],
    [
        "Vgjhhv2QmbI",
        "http://bibfra.me/vocab/marcext/tag-007",
        "m                199402",
        {}
    ]
]
'''

# test integer extraction from 006
SNIPPET_16 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>      g                 </leader>
  <controlfield tag="006">c001              </controlfield>
  <controlfield tag="006">c 02              </controlfield>
  <controlfield tag="006">c123              </controlfield>
  <controlfield tag="006">c---              </controlfield>
  <controlfield tag="006">cnnn              </controlfield>
  <controlfield tag="006">cmmm              </controlfield>
  <controlfield tag="006">cXXX              </controlfield>
</record></collection>
'''

CONFIG_16 = {}

EXPECTED_16 = '''
[
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MovingImage",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/VisualMaterials",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/multiple",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/not-applicable",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/unknown",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marc/runtime",
        1,
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marc/runtime",
        123,
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marc/runtime",
        2,
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c 02              ",
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c---              ",
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c001              ",
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c123              ",
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cXXX              ",
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cmmm              ",
        {}
    ],
    [
        "5NHfFS4gC2Q",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cnnn              ",
        {}
    ],
    [
        "9FS71QIYKLg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "9FS71QIYKLg",
        "http://bibfra.me/vocab/lite/instantiates",
        "5NHfFS4gC2Q",
        {
            "@target-type": "@iri-ref"
        }
    ]
]
'''

SNIPPET_17 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <leader>01420cam a2200349 a 4500</leader>
    <controlfield tag="005">20140814163144.0</controlfield>
    <controlfield tag="008">980828s1996    xxu           000 0 eng  </controlfield>
    <datafield ind1="1" tag="600" ind2="0">
      <subfield code="a">Austen, Jane,</subfield>
      <subfield code="d">1775-1817</subfield>
      <subfield code="v">Quotations.</subfield>
      <subfield code="0">http://id.loc.gov/authorities/names/n79032879</subfield>
      <subfield code="0">(LoC)n79032879</subfield>
      <subfield code="0">http://viaf.org/viaf/102333412</subfield>
      <subfield code="0">(viaf)102333412</subfield>
    </datafield>
    <datafield ind1=" " tag="650" ind2="0">
      <subfield code="a">Friendship</subfield>
      <subfield code="v">Quotations, maxims, etc.</subfield>
      <subfield code="0">http://id.loc.gov/authorities/subjects/sh2008104170</subfield>
      <subfield code="0">(LoC)sh2008104170</subfield>
    </datafield>
  </record>
</collection>
'''

CONFIG_17 = {}

EXPECTED_17 = '''
[
    [
        "4MkBOQR97tU",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "4MkBOQR97tU",
        "http://bibfra.me/vocab/lite/creator",
        "zs5XG6SgswE",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "4MkBOQR97tU",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "4MkBOQR97tU",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "4MkBOQR97tU",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "4MkBOQR97tU",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "4MkBOQR97tU",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "4MkBOQR97tU",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "4MkBOQR97tU",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations.",
        {}
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/sh2008104170",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/lite/focus",
        "c9vkY0XbRlc",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/lite/name",
        "Friendship",
        {}
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/marc/formSubdivision",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "CdpVuclnsho",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "EselD7S-3kU",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "EselD7S-3kU",
        "http://bibfra.me/vocab/lite/instantiates",
        "LtLspj0H5ls",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LgpsHQ30fM8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Form",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LgpsHQ30fM8",
        "http://bibfra.me/vocab/lite/name",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "LgpsHQ30fM8",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "LgpsHQ30fM8",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "LgpsHQ30fM8",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "LgpsHQ30fM8",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/lite/genre",
        "LgpsHQ30fM8",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/lite/genre",
        "TP7TYoLWS-M",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/lite/subject",
        "CdpVuclnsho",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/lite/subject",
        "RZs38ralTEQ",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/marc/index",
        "no index present",
        {}
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/marc/literaryForm",
        "non fiction",
        {}
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/marcext/tag-005",
        "20140814163144.0",
        {}
    ],
    [
        "LtLspj0H5ls",
        "http://bibfra.me/vocab/marcext/tag-008",
        "980828s1996    xxu           000 0 eng  ",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/n79032879",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://viaf.org/viaf/102333412",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/lite/date",
        "1775-1817",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/lite/focus",
        "4MkBOQR97tU",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/marc/formSubdivision",
        "Quotations.",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "RZs38ralTEQ",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations.",
        {}
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Form",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/vocab/lite/name",
        "Quotations.",
        {}
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "TP7TYoLWS-M",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations.",
        {}
    ],
    [
        "c9vkY0XbRlc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Topic",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "c9vkY0XbRlc",
        "http://bibfra.me/vocab/lite/name",
        "Friendship",
        {}
    ],
    [
        "c9vkY0XbRlc",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "c9vkY0XbRlc",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "c9vkY0XbRlc",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "c9vkY0XbRlc",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/lite/date",
        "1775-1817",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "zs5XG6SgswE",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations.",
        {}
    ]
]
'''

SNIPPET_18 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <datafield tag="650" ind1=" " ind2="0">
      <subfield code="a">Name goes here</subfield>
      <subfield code="z">Region 1</subfield>
      <subfield code="x">General Sub1</subfield>
      <subfield code="b">Alt name not used in label</subfield>
      <subfield code="x">General Sub2</subfield>
      <subfield code="z">Region 2</subfield>
    </datafield>
  </record>
</collection>
'''

CONFIG_18 = {
    "versa-attr-cls": "collections.OrderedDict",
    "versa-attr-list-cls": "bibframe.util.LoggedList",
    "plugins": [{
      "id": "http://bibfra.me/tool/pybibframe#labelizer",
      "lookup": {
        "http://bibfra.me/vocab/lite/Concept": [" > $",
                                            "http://bibfra.me/vocab/lite/name",
                                            "http://bibfra.me/vocab/marc/formSubdivision",
                                            "http://bibfra.me/vocab/marc/generalSubdivision",
                                            "http://bibfra.me/vocab/marc/chronologicalSubdivision",
                                            "http://bibfra.me/vocab/marc/geographicSubdivision",
                                            "http://bibfra.me/vocab/lite/title"],
       "http://bibfra.me/vocab/lite/Topic": "http://bibfra.me/vocab/lite/name"
      }
    }]
}

EXPECTED_18 = '''
[
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/lite/focus",
        "1DZG6FP6EgU",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/lite/name",
        "Name goes here",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marc/generalSubdivision",
        "General Sub1",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marc/generalSubdivision",
        "General Sub2",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marc/geographicSubdivision",
        "Region 1",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marc/geographicSubdivision",
        "Region 2",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Name goes here",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marcext/sf-b",
        "Alt name not used in label",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub1",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub2",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 1",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 2",
        {}
    ],
    [
        "-GRzYUG_YDU",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "Name goes here > Region 1 > General Sub1 | General Sub2 > Region 2",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Topic",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/vocab/lite/name",
        "Name goes here",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/vocab/marc/additionalName",
        "Alt name not used in label",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Name goes here",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/vocab/marcext/sf-b",
        "Alt name not used in label",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub1",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub2",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 1",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 2",
        {}
    ],
    [
        "1DZG6FP6EgU",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "Name goes here",
        {}
    ],
    [
        "qbeBjnlr_6o",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "qbeBjnlr_6o",
        "http://bibfra.me/vocab/lite/subject",
        "-GRzYUG_YDU",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "xt0zhFspLCc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "xt0zhFspLCc",
        "http://bibfra.me/vocab/lite/instantiates",
        "qbeBjnlr_6o",
        {
            "@target-type": "@iri-ref"
        }
    ]
]
'''

all_snippets = sorted([ sym for sym in globals() if sym.startswith('SNIPPET') ])
all_config = sorted([ sym for sym in globals() if sym.startswith('CONFIG') ])
all_expected = sorted([ sym for sym in globals() if sym.startswith('EXPECTED') ])

all_snippets = [ (sym, globals()[sym]) for sym in all_snippets ]
all_config = [ (sym, globals()[sym]) for sym in all_config ]
all_expected = [ (sym, globals()[sym]) for sym in all_expected ]

def file_diff(s_orig, s_new):
    diff = difflib.unified_diff(s_orig.split('\n'), s_new.split('\n'))
    return '\n'.join(list(diff))


def run_one(snippet, expected, desc, entbase=None, config=None, loop=None, canonical=True):
    m = memory.connection()
    m_expected = memory.connection()
    infile = tempfile.NamedTemporaryFile()
    infile.write(snippet.encode('utf-8'))
    infile.seek(0)
    outstream = StringIO()
    bfconvert(factory(infile), model=m, out=outstream, config=config, canonical=canonical, loop=loop)
    infile.close()
    outstream.seek(0)
    hashmap, m = hash_neutral_model(outstream)
    hashmap = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap.items() ]))

    expected_stream = StringIO(expected)
    hashmap_expected, m_expected = hash_neutral_model(expected_stream)
    hashmap_expected = '\n'.join(sorted([ repr((i[1], i[0])) for i in hashmap_expected.items() ]))

    assert hashmap == hashmap_expected, "Changes to hashes found ({0}):\n{1}\n\nActual model structure diff:\n{2}".format(desc, file_diff(hashmap_expected, hashmap), file_diff(repr(m_expected), repr(m)))
    assert m == m_expected, "Discrepancies found ({0}):\n{1}".format(desc, file_diff(repr(m_expected), repr(m)))


@pytest.mark.parametrize('snippet, config, expected', zip(all_snippets, all_config, all_expected))
def test_snippets(snippet, config, expected):
    #Use a new event loop per test instance, and so one call of bfconvert per test
    desc = '|'.join([ t[0] for t in (snippet, config, expected) ])
    snippet, config, expected = [ t[1] for t in (snippet, config, expected) ]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    run_one(snippet, expected, desc, config=config, loop=loop)


if __name__ == '__main__':
    raise SystemExit("use py.test")
