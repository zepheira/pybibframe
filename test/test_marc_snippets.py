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
    bfconvert(instream, model=m, out=outstream, config=cobj, canonical=True, loop=loop)
    print('EXPECTED from {0}:'.format(s))
    print(outstream.getvalue()) #This output becomes the EXPECTED stanza

'''

import sys
import logging
import asyncio
import difflib
from io import StringIO, BytesIO
import tempfile

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
        "_keig4s2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_keig4s2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_keig4s2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_keig4s2",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "_keig4s2",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "_keig4s2",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "_keig4s2",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "yvQzzOiH",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "yvQzzOiH",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "yvQzzOiH",
        "http://bibfra.me/vocab/lite/instantiates",
        "_keig4s2",
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
        "JkH7BZ-H",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/vocab/lite/instantiates",
        "JkH7BZ-H",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/vocab/marc/titleStatement",
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

EXPECTED_3 = '''
[
    [
        "JkH7BZ-H",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "JkH7BZ-H",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/vocab/lite/instantiates",
        "JkH7BZ-H",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "VwZodQP2",
        "http://bibfra.me/vocab/marc/titleStatement",
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

EXPECTED_4 = '''
[
    [
        "_keig4s2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_keig4s2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_keig4s2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_keig4s2",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "_keig4s2",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "_keig4s2",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "_keig4s2",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "yvQzzOiH",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "yvQzzOiH",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "yvQzzOiH",
        "http://bibfra.me/vocab/lite/instantiates",
        "_keig4s2",
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
        "NdvSfYil",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/lite/title",
        "Ishinp\u014d /",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/lite/title",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "programmed texts",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Tanba no Sukune Yasuyori sen.",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/marc/titleStatement",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/marcext/tag-008",
        "020613s1860 ja a 000 0 jpn",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/marcext/tag-880-10-6",
        "245-02/$1",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/marcext/tag-880-10-a",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "NdvSfYil",
        "http://bibfra.me/vocab/marcext/tag-880-10-c",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ],
    [
        "wOSEKrl4",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "wOSEKrl4",
        "http://bibfra.me/vocab/lite/instantiates",
        "NdvSfYil",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "wOSEKrl4",
        "http://bibfra.me/vocab/lite/title",
        "Ishinp\u014d /",
        {}
    ],
    [
        "wOSEKrl4",
        "http://bibfra.me/vocab/lite/title",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "wOSEKrl4",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Tanba no Sukune Yasuyori sen.",
        {}
    ],
    [
        "wOSEKrl4",
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
        "DoVM1hvc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DoVM1hvc",
        "http://bibfra.me/vocab/lite/date",
        "1878-1967.",
        {}
    ],
    [
        "DoVM1hvc",
        "http://bibfra.me/vocab/lite/name",
        "Sandburg, Carl,",
        {}
    ],
    [
        "DoVM1hvc",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Sandburg, Carl,",
        {}
    ],
    [
        "DoVM1hvc",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1878-1967.",
        {}
    ],
    [
        "O8rkHG6A",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "O8rkHG6A",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "O8rkHG6A",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "O8rkHG6A",
        "http://bibfra.me/vocab/lite/creator",
        "DoVM1hvc",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "O8rkHG6A",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "O8rkHG6A",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "O8rkHG6A",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "O8rkHG6A",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "v3SayFrF",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "v3SayFrF",
        "http://bibfra.me/vocab/lite/instantiates",
        "O8rkHG6A",
        {
            "@target-type": "@iri-ref"
        }
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
        "MqzpTVEt",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "MqzpTVEt",
        "http://bibfra.me/vocab/lite/instantiates",
        "NLx-hKGy",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/vocab/marc/characteristic",
        "periodical",
        {}
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/vocab/marc/frequency",
        "bimonthly",
        {}
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/vocab/marc/originalAlphabetOrScriptOfTitle",
        "basic roman",
        {}
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/vocab/marc/regularity",
        "regular",
        {}
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/vocab/marcext/tag-008",
        "010806c20019999ru br p       0   a0eng d",
        {}
    ],
    [
        "NLx-hKGy",
        "http://bibfra.me/vocab/relation/unionOf",
        "v7KconuS",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "v7KconuS",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://lccn.loc.gov/96646621",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://www.ncbi.nlm.nih.gov/nlmcatalog?term=7505458",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://www.worldcat.org/oclc/1478787",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/lite/title",
        "Doklady biochemistry",
        {}
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/marc/issn",
        "0012-4958",
        {}
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/marcext/sf-t",
        "Doklady biochemistry",
        {}
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(DLC)   96646621",
        {}
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(DNLM)7505458",
        {}
    ],
    [
        "v7KconuS",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(OCoLC)1478787",
        {}
    ],
    [
        "v7KconuS",
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
        "8jkfYTiE",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "8jkfYTiE",
        "http://bibfra.me/vocab/lite/instantiates",
        "cwmyy44V",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "8jkfYTiE",
        "http://bibfra.me/vocab/marc/publication",
        "fSuzQL_M",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "M7O9Q9np",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Place",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "M7O9Q9np",
        "http://bibfra.me/vocab/lite/name",
        "Tokyo.",
        {}
    ],
    [
        "M7O9Q9np",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Tokyo.",
        {}
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/vocab/lite/language",
        "jpn",
        {}
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/vocab/marc/characteristic",
        "periodical",
        {}
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/vocab/marc/frequency",
        "unknown",
        {}
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/vocab/marc/regularity",
        "unknown",
        {}
    ],
    [
        "cwmyy44V",
        "http://bibfra.me/vocab/marcext/tag-008",
        "821218d18821919ja uu p       0||||0jpn b",
        {}
    ],
    [
        "fSuzQL_M",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/ProviderEvent",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "fSuzQL_M",
        "http://bibfra.me/vocab/lite/providerPlace",
        "M7O9Q9np",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "fSuzQL_M",
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
        "REBetltW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "REBetltW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "REBetltW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "REBetltW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marc/frequency",
        "biennial",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marc/governmentPublication",
        "federal national government publication",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "dictionaries",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "directories",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marc/originalAlphabetOrScriptOfTitle",
        "basic roman",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marc/regularity",
        "regular",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marcext/tag-003",
        "OCoLC",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marcext/tag-005",
        "20141208144405.0",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marcext/tag-006",
        "m     o  d f      ",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marcext/tag-007",
        "cr gn|||||||||",
        {}
    ],
    [
        "REBetltW",
        "http://bibfra.me/vocab/marcext/tag-008",
        "970709c19679999dcugr   o hr f0   a0eng  ",
        {}
    ],
    [
        "eNfogYjb",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "eNfogYjb",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ElectronicResource",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "eNfogYjb",
        "http://bibfra.me/vocab/lite/controlCode",
        "37263290",
        {}
    ],
    [
        "eNfogYjb",
        "http://bibfra.me/vocab/lite/instantiates",
        "REBetltW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "eNfogYjb",
        "http://bibfra.me/vocab/marc/dimensions",
        "unknown",
        {}
    ],
    [
        "eNfogYjb",
        "http://bibfra.me/vocab/marc/formOfItem",
        "online",
        {}
    ],
    [
        "eNfogYjb",
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
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "881466",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MovingImage",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
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
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "881466",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ]
]'''

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
        "7fhOVaVy",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marc/illustrations",
        "illustrations",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marc/index",
        "index present",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marc/literaryForm",
        "non fiction",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "bibliography",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marcext/tag-008",
        "050506s2005    gw a     b    001 0 eng  ",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "1588902153 (TNY)",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "3136128044 (GTV)",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "9781588902153 (TNY)",
        {}
    ],
    [
        "7fhOVaVy",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "9783136128046 (GTV)",
        {}
    ],
    [
        "DVlNHJcG",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DVlNHJcG",
        "http://bibfra.me/vocab/lite/controlCode",
        "1247500",
        {}
    ],
    [
        "DVlNHJcG",
        "http://bibfra.me/vocab/lite/instantiates",
        "7fhOVaVy",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DVlNHJcG",
        "http://bibfra.me/vocab/marc/isbn",
        "9781588902153",
        {}
    ],
    [
        "DVlNHJcG",
        "http://bibfra.me/vocab/marc/isbnType",
        "(TNY)",
        {}
    ],
    [
        "XM7HBzEu",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "XM7HBzEu",
        "http://bibfra.me/vocab/lite/controlCode",
        "1247500",
        {}
    ],
    [
        "XM7HBzEu",
        "http://bibfra.me/vocab/lite/instantiates",
        "7fhOVaVy",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "XM7HBzEu",
        "http://bibfra.me/vocab/marc/isbn",
        "9783136128046",
        {}
    ],
    [
        "XM7HBzEu",
        "http://bibfra.me/vocab/marc/isbnType",
        "(GTV)",
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
        "Lw5Txi2I",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Lw5Txi2I",
        "http://bibfra.me/vocab/lite/instantiates",
        "Ph1VSk-f",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Ph1VSk-f",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Ph1VSk-f",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Ph1VSk-f",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Ph1VSk-f",
        "http://bibfra.me/vocab/lite/creator",
        "R-ReGIB2",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/%28ZZZ%29%20%20Ishinp%C5%8D%20%2F",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/%28ZZZ%29%20%20x9898989898",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/(ZZZ)x9898989898",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/n79032879",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://viaf.org/viaf/102333412",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)  Ishinp\u014d /",
        {}
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)  x9898989898",
        {}
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)x9898989898",
        {}
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "R-ReGIB2",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
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
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MotionPicture",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1992",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1993",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1994-02",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-007",
        "m                1992",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-007",
        "m                1993--",
        {}
    ],
    [
        "kP2G4QhW",
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
        "IC4V39Hk",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MovingImage",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/VisualMaterials",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/multiple",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/not-applicable",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/unknown",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marc/runtime",
        1,
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marc/runtime",
        123,
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marc/runtime",
        2,
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c 02              ",
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c---              ",
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c001              ",
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c123              ",
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cXXX              ",
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cmmm              ",
        {}
    ],
    [
        "IC4V39Hk",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cnnn              ",
        {}
    ],
    [
        "LWrAcXTl",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LWrAcXTl",
        "http://bibfra.me/vocab/lite/instantiates",
        "IC4V39Hk",
        {
            "@target-type": "@iri-ref"
        }
    ]
]'''

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

EXPECTED_17 = '''[
    [
        "3wNBhsEh",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/sh2008104170",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/lite/focus",
        "aFaDTjs1",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/lite/name",
        "Friendship",
        {}
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/marc/formSubdivision",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "3wNBhsEh",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "AaAs516W",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "AaAs516W",
        "http://bibfra.me/vocab/lite/instantiates",
        "Bz2m7NIu",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/lite/genre",
        "O_GVdk0y",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/lite/genre",
        "hH8I69p9",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/lite/subject",
        "3wNBhsEh",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/lite/subject",
        "vulrb2Yz",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/marc/index",
        "no index present",
        {}
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/marc/literaryForm",
        "non fiction",
        {}
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/marcext/tag-005",
        "20140814163144.0",
        {}
    ],
    [
        "Bz2m7NIu",
        "http://bibfra.me/vocab/marcext/tag-008",
        "980828s1996    xxu           000 0 eng  ",
        {}
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Form",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/vocab/lite/name",
        "Quotations.",
        {}
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "O_GVdk0y",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations.",
        {}
    ],
    [
        "aFaDTjs1",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Topic",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "aFaDTjs1",
        "http://bibfra.me/vocab/lite/name",
        "Friendship",
        {}
    ],
    [
        "aFaDTjs1",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "aFaDTjs1",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "aFaDTjs1",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "aFaDTjs1",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "hH8I69p9",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Form",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "hH8I69p9",
        "http://bibfra.me/vocab/lite/name",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "hH8I69p9",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "hH8I69p9",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "hH8I69p9",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "hH8I69p9",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/lite/date",
        "1775-1817",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "oo8FKz2v",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations.",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/n79032879",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://viaf.org/viaf/102333412",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/lite/date",
        "1775-1817",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/lite/focus",
        "oo8FKz2v",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/marc/formSubdivision",
        "Quotations.",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "vulrb2Yz",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "vulrb2Yz",
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
        "5ygS5Gv9",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5ygS5Gv9",
        "http://bibfra.me/vocab/lite/instantiates",
        "a3mOgbep",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Topic",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/vocab/lite/name",
        "Name goes here",
        {}
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/vocab/marc/additionalName",
        "Alt name not used in label",
        {}
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Name goes here",
        {}
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/vocab/marcext/sf-b",
        "Alt name not used in label",
        {}
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub1",
        {}
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub2",
        {}
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 1",
        {}
    ],
    [
        "_nmQYQ2f",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 2",
        {}
    ],
    [
        "_nmQYQ2f",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "Name goes here",
        {}
    ],
    [
        "a3mOgbep",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "a3mOgbep",
        "http://bibfra.me/vocab/lite/subject",
        "u0IU3M1U",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/lite/focus",
        "_nmQYQ2f",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/lite/name",
        "Name goes here",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marc/generalSubdivision",
        "General Sub1",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marc/generalSubdivision",
        "General Sub2",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marc/geographicSubdivision",
        "Region 1",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marc/geographicSubdivision",
        "Region 2",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Name goes here",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marcext/sf-b",
        "Alt name not used in label",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub1",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub2",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 1",
        {}
    ],
    [
        "u0IU3M1U",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 2",
        {}
    ],
    [
        "u0IU3M1U",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "Name goes here > Region 1 > General Sub1 | General Sub2 > Region 2",
        {}
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
    bfconvert([infile.name], model=m, out=outstream, config=config, canonical=canonical, loop=loop)
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
