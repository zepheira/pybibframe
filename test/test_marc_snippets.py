'''

Requires http://pytest.org/ e.g.:

pip install pytest

----
'''

import sys
import logging
import asyncio
import unittest
import difflib
from io import StringIO

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader.marcxml import bfconvert

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

EXPECTED_1 = '''[
[
"Lw_-mBOy",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/marc/Instance",
{}
],
[
"Lw_-mBOy",
"http://bibfra.me/vocab/lite/controlCode",
"92005291",
{}
],
[
"Lw_-mBOy",
"http://bibfra.me/vocab/marc/instantiates",
"m3WVtlnz",
{}
],
[
"m3WVtlnz",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/LanguageMaterial",
{}
],
[
"m3WVtlnz",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/encyclopedias",
{}
],
[
"m3WVtlnz",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/legal-articles",
{}
],
[
"m3WVtlnz",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/surveys-of-literature",
{}
],
[
"m3WVtlnz",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/marc/Work",
{}
],
[
"m3WVtlnz",
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

EXPECTED_2 = '''[
[
"Qx6eLZ2J",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/marc/Instance",
{}
],
[
"Qx6eLZ2J",
"http://bibfra.me/vocab/lite/title",
"Arithmetic /",
{}
],
[
"Qx6eLZ2J",
"http://bibfra.me/vocab/marc/instantiates",
"_EPsFtnX",
{}
],
[
"Qx6eLZ2J",
"http://bibfra.me/vocab/rda/titleStatement",
"Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/LanguageMaterial",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/encyclopedias",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/legal-articles",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/surveys-of-literature",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/marc/Work",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/vocab/lite/title",
"Arithmetic /",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/vocab/marc/tag-008",
"920219s1993 caua j 000 0 eng",
{}
],
[
"_EPsFtnX",
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

EXPECTED_3 = '''
[
[
"Qx6eLZ2J",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/marc/Instance",
{}
],
[
"Qx6eLZ2J",
"http://bibfra.me/vocab/lite/controlCode",
"92005291",
{}
],
[
"Qx6eLZ2J",
"http://bibfra.me/vocab/lite/title",
"Arithmetic /",
{}
],
[
"Qx6eLZ2J",
"http://bibfra.me/vocab/marc/instantiates",
"_EPsFtnX",
{}
],
[
"Qx6eLZ2J",
"http://bibfra.me/vocab/rda/titleStatement",
"Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/LanguageMaterial",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/encyclopedias",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/legal-articles",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/lite/surveys-of-literature",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/purl/versa/type",
"http://bibfra.me/vocab/marc/Work",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/vocab/lite/title",
"Arithmetic /",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/vocab/marc/tag-008",
"920219s1993 caua j 000 0 eng",
{}
],
[
"_EPsFtnX",
"http://bibfra.me/vocab/rda/titleStatement",
"Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
{}
     ]
]
'''

all_snippets = sorted([ obj for (sym, obj) in locals().items() if sym.startswith('SNIPPET') ])
all_expected = sorted([ obj for (sym, obj) in locals().items() if sym.startswith('EXPECTED') ])


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


@pytest.mark.parametrize('snippet, expected', zip(all_snippets, all_expected))
def test_snippets(snippet, expected):
    #Use a new event loop per test instance, and so one call of bfconvert per test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    run_one(snippet, expected, loop=loop)


if __name__ == '__main__':
    raise SystemExit("use py.test")
