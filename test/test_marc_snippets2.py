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

from amara3.inputsource import factory

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader import bfconvert
import bibframe.plugin
from bibframe.util import hash_neutral_model

import pytest

#Bits from http://www.loc.gov/standards/marcxml/Sandburg/sandburg.xml

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
        "qbX1fsNldrs",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "qbX1fsNldrs",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ElectronicResource",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "qbX1fsNldrs",
        "http://bibfra.me/vocab/lite/controlCode",
        "37263290",
        {}
    ],
    [
        "qbX1fsNldrs",
        "http://bibfra.me/vocab/lite/instantiates",
        "ucZjoxY-Isc",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "qbX1fsNldrs",
        "http://bibfra.me/vocab/marc/dimensions",
        "unknown",
        {}
    ],
    [
        "qbX1fsNldrs",
        "http://bibfra.me/vocab/marc/formOfItem",
        "online",
        {}
    ],
    [
        "qbX1fsNldrs",
        "http://bibfra.me/vocab/marc/specificMaterialDesignation",
        "remote",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marc/frequency",
        "biennial",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marc/governmentPublication",
        "federal national government publication",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "dictionaries",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "directories",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marc/originalAlphabetOrScriptOfTitle",
        "basic roman",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marc/regularity",
        "regular",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marcext/tag-003",
        "OCoLC",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marcext/tag-005",
        "20141208144405.0",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marcext/tag-006",
        "m     o  d f      ",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marcext/tag-007",
        "cr gn|||||||||",
        {}
    ],
    [
        "ucZjoxY-Isc",
        "http://bibfra.me/vocab/marcext/tag-008",
        "970709c19679999dcugr   o hr f0   a0eng  ",
        {}
    ]
]
'''

# a couple of degenerate cases
SNIPPET_11 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
<record xmlns="http://www.loc.gov/MARC21/slim"><leader>00000ngm a2200000Ka 4500</leader><controlfield tag="001">881466</controlfield></record>
</collection>
'''

CONFIG_11 = {}

EXPECTED_11 = '''
[
    [
        "5oTRm8YuoLg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5oTRm8YuoLg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MovingImage",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "5oTRm8YuoLg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/VisualMaterials",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ujFWXv8S6l0",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ujFWXv8S6l0",
        "http://bibfra.me/vocab/lite/controlCode",
        "881466",
        {}
    ],
    [
        "ujFWXv8S6l0",
        "http://bibfra.me/vocab/lite/instantiates",
        "5oTRm8YuoLg",
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
        "APki02GVOdw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "APki02GVOdw",
        "http://bibfra.me/vocab/lite/controlCode",
        "881466",
        {}
    ],
    [
        "APki02GVOdw",
        "http://bibfra.me/vocab/lite/instantiates",
        "yF1Aoyu4VSc",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "yF1Aoyu4VSc",
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
        "7oNnsir8B7s",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "7oNnsir8B7s",
        "http://bibfra.me/vocab/lite/controlCode",
        "1247500",
        {}
    ],
    [
        "7oNnsir8B7s",
        "http://bibfra.me/vocab/lite/instantiates",
        "TOFSAqBk_4E",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "7oNnsir8B7s",
        "http://bibfra.me/vocab/marc/isbn",
        "9781588902153",
        {}
    ],
    [
        "7oNnsir8B7s",
        "http://bibfra.me/vocab/marc/isbnType",
        "(TNY)",
        {}
    ],
    [
        "7xf1LdAXzMM",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "7xf1LdAXzMM",
        "http://bibfra.me/vocab/lite/controlCode",
        "1247500",
        {}
    ],
    [
        "7xf1LdAXzMM",
        "http://bibfra.me/vocab/lite/instantiates",
        "TOFSAqBk_4E",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "7xf1LdAXzMM",
        "http://bibfra.me/vocab/marc/isbn",
        "9783136128046",
        {}
    ],
    [
        "7xf1LdAXzMM",
        "http://bibfra.me/vocab/marc/isbnType",
        "(GTV)",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/marc/illustrations",
        "illustrations",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/marc/index",
        "index present",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/marc/literaryForm",
        "non fiction",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "bibliography",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/marcext/tag-008",
        "050506s2005    gw a     b    001 0 eng  ",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "1588902153 (TNY)",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "3136128044 (GTV)",
        {}
    ],
    [
        "TOFSAqBk_4E",
        "http://bibfra.me/vocab/marcext/tag-020-XX-a",
        "9781588902153 (TNY)",
        {}
    ],
    [
        "TOFSAqBk_4E",
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
        "DI_aPYZ7v0U",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/%28ZZZ%29%20%20Ishinp%C5%8D%20%2F",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/%28ZZZ%29%20%20x9898989898",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://bibfra.me/vocab/marcext/authrec/(ZZZ)x9898989898",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/n79032879",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://viaf.org/viaf/102333412",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)  Ishinp\u014d /",
        {}
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)  x9898989898",
        {}
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(ZZZ)x9898989898",
        {}
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "DI_aPYZ7v0U",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "XVQwuBl6LMc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "XVQwuBl6LMc",
        "http://bibfra.me/vocab/lite/instantiates",
        "_LFRIQI-KkA",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_LFRIQI-KkA",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_LFRIQI-KkA",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_LFRIQI-KkA",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_LFRIQI-KkA",
        "http://bibfra.me/vocab/lite/creator",
        "DI_aPYZ7v0U",
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
        "APki02GVOdw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "APki02GVOdw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MotionPicture",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "APki02GVOdw",
        "http://bibfra.me/vocab/lite/instantiates",
        "yF1Aoyu4VSc",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "APki02GVOdw",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1992",
        {}
    ],
    [
        "APki02GVOdw",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1993",
        {}
    ],
    [
        "APki02GVOdw",
        "http://bibfra.me/vocab/marc/filmInspectionDate",
        "1994-02",
        {}
    ],
    [
        "yF1Aoyu4VSc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "yF1Aoyu4VSc",
        "http://bibfra.me/vocab/marcext/tag-007",
        "m                1992",
        {}
    ],
    [
        "yF1Aoyu4VSc",
        "http://bibfra.me/vocab/marcext/tag-007",
        "m                1993--",
        {}
    ],
    [
        "yF1Aoyu4VSc",
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
        "LjNUMfg2jQY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MovingImage",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/VisualMaterials",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/multiple",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/not-applicable",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marc/runtime",
        "http://bibfra.me/vocab/marc/unknown",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marc/runtime",
        1,
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marc/runtime",
        123,
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marc/runtime",
        2,
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c 02              ",
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c---              ",
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c001              ",
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marcext/tag-006",
        "c123              ",
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cXXX              ",
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cmmm              ",
        {}
    ],
    [
        "LjNUMfg2jQY",
        "http://bibfra.me/vocab/marcext/tag-006",
        "cnnn              ",
        {}
    ],
    [
        "kQdr2uFrxXs",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kQdr2uFrxXs",
        "http://bibfra.me/vocab/lite/instantiates",
        "LjNUMfg2jQY",
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
        "GgewcgNRUCs",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Topic",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "GgewcgNRUCs",
        "http://bibfra.me/vocab/lite/name",
        "Friendship",
        {}
    ],
    [
        "GgewcgNRUCs",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "GgewcgNRUCs",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "GgewcgNRUCs",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "GgewcgNRUCs",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/lite/genre",
        "WRYwes4yv4k",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/lite/genre",
        "x5Ig2vn3qiw",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/lite/language",
        "eng",
        {}
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/lite/subject",
        "apo1Ao7RunQ",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/lite/subject",
        "gz_aTEgktP4",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/marc/index",
        "no index present",
        {}
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/marc/literaryForm",
        "non fiction",
        {}
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/marcext/tag-005",
        "20140814163144.0",
        {}
    ],
    [
        "WQs46iFiYKg",
        "http://bibfra.me/vocab/marcext/tag-008",
        "980828s1996    xxu           000 0 eng  ",
        {}
    ],
    [
        "WRYwes4yv4k",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Form",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "WRYwes4yv4k",
        "http://bibfra.me/vocab/lite/name",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "WRYwes4yv4k",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "WRYwes4yv4k",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "WRYwes4yv4k",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "WRYwes4yv4k",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/lite/date",
        "1775-1817",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "Z7YEkZXapkA",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations.",
        {}
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/sh2008104170",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/lite/focus",
        "GgewcgNRUCs",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/lite/name",
        "Friendship",
        {}
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/marc/formSubdivision",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)sh2008104170",
        {}
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/subjects/sh2008104170",
        {}
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Friendship",
        {}
    ],
    [
        "apo1Ao7RunQ",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations, maxims, etc.",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://id.loc.gov/authorities/names/n79032879",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://viaf.org/viaf/102333412",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/lite/date",
        "1775-1817",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/lite/focus",
        "Z7YEkZXapkA",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/lite/name",
        "Austen, Jane,",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/marc/formSubdivision",
        "Quotations.",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "gz_aTEgktP4",
        "http://bibfra.me/vocab/marcext/sf-v",
        "Quotations.",
        {}
    ],
    [
        "lurWkoG0ZZc",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "lurWkoG0ZZc",
        "http://bibfra.me/vocab/lite/instantiates",
        "WQs46iFiYKg",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "x5Ig2vn3qiw",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Form",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "x5Ig2vn3qiw",
        "http://bibfra.me/vocab/lite/name",
        "Quotations.",
        {}
    ],
    [
        "x5Ig2vn3qiw",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(LoC)n79032879",
        {}
    ],
    [
        "x5Ig2vn3qiw",
        "http://bibfra.me/vocab/marcext/sf-0",
        "(viaf)102333412",
        {}
    ],
    [
        "x5Ig2vn3qiw",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://id.loc.gov/authorities/names/n79032879",
        {}
    ],
    [
        "x5Ig2vn3qiw",
        "http://bibfra.me/vocab/marcext/sf-0",
        "http://viaf.org/viaf/102333412",
        {}
    ],
    [
        "x5Ig2vn3qiw",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Austen, Jane,",
        {}
    ],
    [
        "x5Ig2vn3qiw",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1775-1817",
        {}
    ],
    [
        "x5Ig2vn3qiw",
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
        "Xcb9OOoMJNs",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Concept",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/lite/focus",
        "iA3PYMnNnis",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/lite/name",
        "Name goes here",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marc/generalSubdivision",
        "General Sub1",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marc/generalSubdivision",
        "General Sub2",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marc/geographicSubdivision",
        "Region 1",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marc/geographicSubdivision",
        "Region 2",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Name goes here",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marcext/sf-b",
        "Alt name not used in label",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub1",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub2",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 1",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 2",
        {}
    ],
    [
        "Xcb9OOoMJNs",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "Name goes here > Region 1 > General Sub1 | General Sub2 > Region 2",
        {}
    ],
    [
        "bSd-2v0jlqE",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "bSd-2v0jlqE",
        "http://bibfra.me/vocab/lite/instantiates",
        "jNbK8tuuT8M",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Topic",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/vocab/lite/name",
        "Name goes here",
        {}
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/vocab/marc/additionalName",
        "Alt name not used in label",
        {}
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Name goes here",
        {}
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/vocab/marcext/sf-b",
        "Alt name not used in label",
        {}
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub1",
        {}
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/vocab/marcext/sf-x",
        "General Sub2",
        {}
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 1",
        {}
    ],
    [
        "iA3PYMnNnis",
        "http://bibfra.me/vocab/marcext/sf-z",
        "Region 2",
        {}
    ],
    [
        "iA3PYMnNnis",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "Name goes here",
        {}
    ],
    [
        "jNbK8tuuT8M",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "jNbK8tuuT8M",
        "http://bibfra.me/vocab/lite/subject",
        "Xcb9OOoMJNs",
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
    bfconvert([infile], model=m, out=outstream, config=config, canonical=canonical, loop=loop)
    #bfconvert(factory(infile), model=m, out=outstream, config=config, canonical=canonical, loop=loop)
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
