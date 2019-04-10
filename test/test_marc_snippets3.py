# -*- coding: utf-8 -*-
'''
Test some small, simple MARC snippets.

Requires http://pytest.org/ e.g.:

pip install pytest

Each test case is a triple of e.g. [SNIPPET_1, CONFIG_1, EXPECTED_1]

You must have matched series each with all 3 components matched up, otherwise the entire test suite will fall over like a stack of dominoes

----

Recipe for regenerating the test case expected outputs:

python -i test/test_marc_snippets3.py #Ignore the SystemExit

Then:

all_snippets = sorted([ sym for sym in globals() if sym.startswith('SNIPPET') ])
all_config = sorted([ sym for sym in globals() if sym.startswith('CONFIG') ])
all_expected = sorted([ sym for sym in globals() if sym.startswith('EXPECTED') ])

for s, c, e in zip(all_snippets, all_config, all_expected):
    sobj, cobj, eobj = globals()[s], globals()[c], globals()[e]
    m = memory.connection()
    instream = BytesIO(sobj.encode('utf-8'))
    outstream = StringIO()
    bfconvert(instream, model=m, out=outstream, config=cobj, canonical=True)
    print('EXPECTED from {0}:'.format(s))
    print(outstream.getvalue()) #This output becomes the EXPECTED stanza

'''

import sys
import logging
import difflib
from io import StringIO, BytesIO
import tempfile

from amara3.inputsource import factory

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader import bfconvert
import bibframe.plugin
from bibframe.util import hash_neutral_model
from bibframe.reader.util import *
from bibframe import *


import pytest

#Bits from http://www.loc.gov/standards/marcxml/Sandburg/sandburg.xml

#XXX Add test for 8a subfield code warning
SNIPPET_21 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>02143nam a22004218a 4500</leader>
  <!-- Note the following 2 ISBNs, once normalized, are the same -->
  <datafield ind2=" " ind1=" " tag="020"><subfield code="a">9781615302550</subfield></datafield>
  <datafield ind2=" " ind1=" " tag="020"><subfield code="a">1615302557</subfield></datafield>
  <datafield ind2="4" ind1="0" tag="245">
    <!-- Note: should issue somethig like: WARNING:root:Invalid subfield code "8a" in record "record-2:0", tag "245" -->
    <subfield code="8a">The eye</subfield>
    <subfield code="h">[downloadable ebook] :</subfield>
    <subfield code="b">the physiology of human perception /</subfield>
    <subfield code="c">edited by Kara Rogers</subfield>
  </datafield>
  <datafield ind2=" " ind1="0" tag="776">
    <subfield code="c">Original</subfield>
    <subfield code="z">9781615301164</subfield>
    <subfield code="w">sky235195071</subfield>
  </datafield>
</record>
</collection>
'''

CONFIG_21 = None

EXPECTED_21 = '''
[
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/lite/authorityLink",
        "sky235195071",
        {}
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/lite/instantiates",
        "tVaxKHAonKQ",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/lite/medium",
        "[downloadable ebook] :",
        {}
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/lite/note",
        "Original",
        {}
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/marc/isbn",
        "9781615301164",
        {}
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/marc/titleRemainder",
        "the physiology of human perception /",
        {}
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/marc/titleStatement",
        "edited by Kara Rogers",
        {}
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/marcext/sf-c",
        "Original",
        {}
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/marcext/sf-w",
        "sky235195071",
        {}
    ],
    [
        "C_YMLbNuSDs",
        "http://bibfra.me/vocab/marcext/sf-z",
        "9781615301164",
        {}
    ],
    [
        "LRxdpzyk-Yk",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LRxdpzyk-Yk",
        "http://bibfra.me/vocab/lite/instantiates",
        "tVaxKHAonKQ",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LRxdpzyk-Yk",
        "http://bibfra.me/vocab/lite/medium",
        "[downloadable ebook] :",
        {}
    ],
    [
        "LRxdpzyk-Yk",
        "http://bibfra.me/vocab/marc/isbn",
        "9781615302550",
        {}
    ],
    [
        "LRxdpzyk-Yk",
        "http://bibfra.me/vocab/marc/titleRemainder",
        "the physiology of human perception /",
        {}
    ],
    [
        "LRxdpzyk-Yk",
        "http://bibfra.me/vocab/marc/titleStatement",
        "edited by Kara Rogers",
        {}
    ],
    [
        "LRxdpzyk-Yk",
        "http://bibfra.me/vocab/relation/hasOtherPhysicalFormat",
        "C_YMLbNuSDs",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "tVaxKHAonKQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "tVaxKHAonKQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "tVaxKHAonKQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "tVaxKHAonKQ",
        "http://bibfra.me/vocab/marc/titleRemainder",
        "the physiology of human perception /",
        {}
    ],
    [
        "tVaxKHAonKQ",
        "http://bibfra.me/vocab/marc/titleStatement",
        "edited by Kara Rogers",
        {}
    ],
    [
        "tVaxKHAonKQ",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "1615302557",
        {}
    ],
    [
        "tVaxKHAonKQ",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "9781615302550",
        {}
    ]
]
'''

SNIPPET_22 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <datafield ind2="4" ind1="0" tag="245">
    <subfield code="a">The eye</subfield>
    <subfield code="h">downloadable ebook</subfield>
    <subfield code="b">the physiology of human perception</subfield>
    <subfield code="c">edited by Kara Rogers</subfield>
  </datafield>
</record>
</collection>
'''

# A perfectly useless configuration just meant to exercise the labelizer
CONFIG_22 = {
    "plugins": [ {
        "id": "http://bibfra.me/tool/pybibframe#labelizer",
        "lookup": {
            "http://bibfra.me/vocab/lite/Instance": [ {
                "properties": [ "http://bibfra.me/vocab/lite/titleStatement" ]
            },
            {
                "separator": lambda ctx: '=' if ctx['currentProperty']=='http://bibfra.me/vocab/lite/title' else '-',
                "wrapper": lambda ctx: '[]' if ctx['currentProperty']=='http://bibfra.me/vocab/lite/medium' else None,
                "marcOrder": True,
                "properties": [ "http://bibfra.me/vocab/lite/title",
                                "http://bibfra.me/vocab/marc/titleRemainder",
                                "http://bibfra.me/vocab/lite/medium",
                                "http://bibfra.me/vocab/marc/titleStatement" ]
            } ]
        },
        "default-label": "!UNKNOWN LABEL"
    } ]
}

EXPECTED_22 = '''
[
    [
        "NKUx9o0hy4w",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NKUx9o0hy4w",
        "http://bibfra.me/vocab/lite/instantiates",
        "wBUG8tKcyqU",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NKUx9o0hy4w",
        "http://bibfra.me/vocab/lite/medium",
        "downloadable ebook",
        {}
    ],
    [
        "NKUx9o0hy4w",
        "http://bibfra.me/vocab/lite/title",
        "The eye",
        {}
    ],
    [
        "NKUx9o0hy4w",
        "http://bibfra.me/vocab/marc/titleRemainder",
        "the physiology of human perception",
        {}
    ],
    [
        "NKUx9o0hy4w",
        "http://bibfra.me/vocab/marc/titleStatement",
        "edited by Kara Rogers",
        {}
    ],
    [
        "NKUx9o0hy4w",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "The eye=[downloadable ebook]-the physiology of human perception-edited by Kara Rogers",
        {}
    ],
    [
        "wBUG8tKcyqU",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "wBUG8tKcyqU",
        "http://bibfra.me/vocab/lite/title",
        "The eye",
        {}
    ],
    [
        "wBUG8tKcyqU",
        "http://bibfra.me/vocab/marc/titleRemainder",
        "the physiology of human perception",
        {}
    ],
    [
        "wBUG8tKcyqU",
        "http://bibfra.me/vocab/marc/titleStatement",
        "edited by Kara Rogers",
        {}
    ]
]
'''


TEST_ABORT_PATTERNS = {
    '852$b': abort_on('eggs'),
}

#Register these transform sets so they can be invoked by URL in config
register_transforms("http://example.org/vocab/test-abort#transforms", TEST_ABORT_PATTERNS)

SNIPPET_23 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="001">92005291</controlfield>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Arithmetic</subfield>
  </datafield>
  <datafield ind1="8" ind2=" " tag="852">
    <subfield code="b">spam</subfield>
  </datafield>
</record>
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="001">92005292</controlfield>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Geometry</subfield>
  </datafield>
  <datafield ind1="8" ind2=" " tag="852">
    <subfield code="b">eggs</subfield>
  </datafield>
</record>
</collection>
'''

CONFIG_23 = {
    "transforms": [
        "http://bibfra.me/tool/pybibframe/transforms#marc",
        "http://bibfra.me/tool/pybibframe/transforms#bflite",
        "http://example.org/vocab/test-abort#transforms"
    ]
}

EXPECTED_23 = '''
[
    [
        "VsIPn7Vve5E",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VsIPn7Vve5E",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VsIPn7Vve5E",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VsIPn7Vve5E",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic",
        {}
    ],
    [
        "VsIPn7Vve5E",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "VsIPn7Vve5E",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "VsIPn7Vve5E",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "VsIPn7Vve5E",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "u6cLqQV23I8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "u6cLqQV23I8",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "u6cLqQV23I8",
        "http://bibfra.me/vocab/lite/instantiates",
        "VsIPn7Vve5E",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "u6cLqQV23I8",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic",
        {}
    ]
]
'''


HELD_AT = 'http://example.org/vocab/held-at'

TEST_INLINE_LOOKUP_PATTERNS = {
    '852$b': oninstance.link(rel=HELD_AT, value=lookup_inline({'ein': 'one', 'uno': 'one', 'zwei': 'two'})),
}

#Register these transform sets so they can be invoked by URL in config
register_transforms("http://example.org/vocab/lookup-inline#transforms", TEST_INLINE_LOOKUP_PATTERNS)

SNIPPET_24 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Arithmetic</subfield>
  </datafield>
  <datafield ind1="8" ind2=" " tag="852">
    <subfield code="b">ein</subfield>
  </datafield>
</record>
</collection>
'''

CONFIG_24 = {
    "transforms": [
        "http://bibfra.me/tool/pybibframe/transforms#marc",
        "http://bibfra.me/tool/pybibframe/transforms#bflite",
        "http://example.org/vocab/lookup-inline#transforms"
    ]
}

EXPECTED_24 = '''
[
    [
        "VpDb1Wlkt_A",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VpDb1Wlkt_A",
        "http://bibfra.me/vocab/lite/instantiates",
        "VuXv7krAijw",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VpDb1Wlkt_A",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic",
        {}
    ],
    [
        "VpDb1Wlkt_A",
        "http://example.org/vocab/held-at",
        "one",
        {}
    ],
    [
        "VuXv7krAijw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "VuXv7krAijw",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic",
        {}
    ]
]
'''


HELD_AT = 'http://example.org/vocab/held-at'

TEST_HOLDINGS_FALLBACK_PATTERNS = {
    '949': oninstance.link('http://library.link/vocab/branchCode', value=ifexists(subfield('a'), subfield('a'), alt='ALL_BRANCHES'))
}

#Register these transform sets so they can be invoked by URL in config
register_transforms("http://example.org/vocab/holdings-fallback#transforms", TEST_HOLDINGS_FALLBACK_PATTERNS)

SNIPPET_25 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Holdings test</subfield>
  </datafield>
  <datafield ind2=" " ind1=" " tag="949">
      <subfield code="a">dt</subfield>
      <subfield code="b">i</subfield>
      <subfield code="c">prta</subfield>
      <subfield code="d">DOWNING</subfield>
      <subfield code="e">fica</subfield>
      <subfield code="f">37413316147406</subfield>
      <subfield code="3">0</subfield>
      <subfield code="i">DOWNING</subfield>
      <subfield code="0">1368556</subfield>
  </datafield>
  <datafield ind2=" " ind1=" " tag="949">
      <subfield code="a">so</subfield>
      <subfield code="a">xx</subfield>
      <subfield code="b">i</subfield>
      <subfield code="c">prta</subfield>
      <subfield code="d">DOWNING</subfield>
      <subfield code="e">fica</subfield>
      <subfield code="f">37413316147398</subfield>
      <subfield code="3">0</subfield>
      <subfield code="i">DOWNING</subfield>
      <subfield code="0">1368555</subfield>
  </datafield>
  <datafield ind2=" " ind1=" " tag="949">
      <subfield code="b">i</subfield>
  </datafield>
</record>
</collection>
'''

CONFIG_25 = {
    "transforms": [
        "http://bibfra.me/tool/pybibframe/transforms#marc",
        "http://bibfra.me/tool/pybibframe/transforms#bflite",
        "http://example.org/vocab/holdings-fallback#transforms"
    ]
}

EXPECTED_25 = '''
[
    [
        "AkhksJtiCK4",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "AkhksJtiCK4",
        "http://bibfra.me/vocab/lite/instantiates",
        "YrII1AheVtE",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "AkhksJtiCK4",
        "http://bibfra.me/vocab/lite/title",
        "Holdings test",
        {}
    ],
    [
        "AkhksJtiCK4",
        "http://library.link/vocab/branchCode",
        "ALL_BRANCHES",
        {}
    ],
    [
        "AkhksJtiCK4",
        "http://library.link/vocab/branchCode",
        "dt",
        {}
    ],
    [
        "AkhksJtiCK4",
        "http://library.link/vocab/branchCode",
        "so",
        {}
    ],
    [
        "AkhksJtiCK4",
        "http://library.link/vocab/branchCode",
        "xx",
        {}
    ],
    [
        "YrII1AheVtE",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "YrII1AheVtE",
        "http://bibfra.me/vocab/lite/title",
        "Holdings test",
        {}
    ]
]
'''


SNIPPET_26 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <leader>02467cam a2200505 a 4500</leader>
        <datafield tag="100" ind1="3" ind2="">
            <subfield code="a">Brown family</subfield>
        </datafield>
  </record>
</collection>
'''

CONFIG_26 = {
    "transforms": [
        "http://example.org/vocab/test-indicator#transforms"
    ]
}
TEST_INDICATOR_SELECTION = {
    '100': ifexists(indicator('3?'),
                    onwork.materialize(BL + 'Family',
                                       values(
                                           BL + 'creator',
                                           relator_property(subfield('e'), prefix=REL),
                                           relator_property(subfield('4'), prefix=REL)
                                       ),
                                       unique=[
                                           (BL + 'name', subfield('a')),
                                           (MARC + 'numeration', subfield('b')),
                                           (MARC + 'titles', subfield('c')),
                                           (BL + 'date', subfield('d')),
                                           (BL + 'nameAlternative', subfield('q')),
                                       ],
                                       links={
                                           BL + 'name': subfield('a'),
                                           MARC + 'numeration': subfield('b'),
                                           MARC + 'titles': subfield('c'),
                                           BL + 'date': subfield('d'),
                                           BL + 'nameAlternative': subfield('q')
                                       }
                                       ),
                    onwork.materialize(BL + 'Person',
                                       values(
                                           BL + 'creator',
                                           relator_property(subfield('e'), prefix=REL),
                                           relator_property(subfield('4'), prefix=REL)
                                       ),
                                       unique=[
                                           (BL + 'name', subfield('a')),
                                           (MARC + 'numeration', subfield('b')),
                                           (MARC + 'titles', subfield('c')),
                                           (BL + 'date', subfield('d')),
                                           (BL + 'nameAlternative', subfield('q')),
                                       ],
                                       links={
                                           BL + 'name': subfield('a'),
                                           MARC + 'numeration': subfield('b'),
                                           MARC + 'titles': subfield('c'),
                                           BL + 'date': subfield('d'),
                                           BL + 'nameAlternative': subfield('q')
                                       }
                                       )
                    ),
}

register_transforms("http://example.org/vocab/test-indicator#transforms", TEST_INDICATOR_SELECTION)

EXPECTED_26 = '''
[
    [
        "O0kRT7RUxLY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "O0kRT7RUxLY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "O0kRT7RUxLY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "O0kRT7RUxLY",
        "http://bibfra.me/vocab/lite/creator",
        "nxaFsx7j5qk",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kG-tDyeLxz4",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kG-tDyeLxz4",
        "http://bibfra.me/vocab/lite/instantiates",
        "O0kRT7RUxLY",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "nxaFsx7j5qk",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Family",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "nxaFsx7j5qk",
        "http://bibfra.me/vocab/lite/name",
        "Brown family",
        {}
    ],
    [
        "nxaFsx7j5qk",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Brown family",
        {}
    ]
]
'''

SNIPPET_27 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <leader>02467cam a2200505 a 4500</leader>
        <datafield tag="100" ind1=" " ind2="">
            <subfield code="a">Not a family</subfield>
        </datafield>
  </record>
</collection>
'''

CONFIG_27 = CONFIG_26

EXPECTED_27='''
[
    [
        "NJ4ZGjmvWuU",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "NJ4ZGjmvWuU",
        "http://bibfra.me/vocab/lite/name",
        "Not a family",
        {}
    ],
    [
        "NJ4ZGjmvWuU",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Not a family",
        {}
    ],
    [
        "UmIxAwDwKuc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "UmIxAwDwKuc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "UmIxAwDwKuc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "UmIxAwDwKuc",
        "http://bibfra.me/vocab/lite/creator",
        "NJ4ZGjmvWuU",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "pESsoh9_INA",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "pESsoh9_INA",
        "http://bibfra.me/vocab/lite/instantiates",
        "UmIxAwDwKuc",
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
    bfconvert([infile], model=m, out=outstream, config=config, canonical=canonical)
    #bfconvert(factory(infile), model=m, out=outstream, config=config, canonical=canonical)
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
    run_one(snippet, expected, desc, config=config)


if __name__ == '__main__':
    raise SystemExit("use py.test")
