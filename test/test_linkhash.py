import struct
import base64

import pytest
import mmh3

from bibframe.contrib.datachefids import simple_hashstring


RESOURCE_ID_CASES = [
('[["http://bibfra.me/purl/versa/type","http://schema.org/Person"],["http://schema.org/name","Jonathan Bruce Postel"],["http://schema.org/birthDate","1943-08-06"],["http://schema.org/deathDate","1998-10-16"]]', b'65IMbTlnlOQ'),
('[["http://bibfra.me/purl/versa/type","http://schema.org/Person"],["http://schema.org/name","Alan Mathison Turing"],["http://schema.org/birthDate","1912-06-23"],["http://schema.org/deathDate","1954-06-07"]]', b'1fFiNHqOLbk'),
('[["http://bibfra.me/purl/versa/type","http://schema.org/Person"],["http://schema.org/name","Brian Wilson Kernighan"],["http://schema.org/birthDate","1942-01-01"]]', b'iEmPxG1rYr4'),
('[["http://bibfra.me/purl/versa/type","http://schema.org/Person"],["http://schema.org/name","Dennis MacAlistair Ritchie"],["http://schema.org/birthDate","1941-09-09"],["http://schema.org/deathDate","2011-10-12"]]', b'boPojRRwekE'),
('[["http://bibfra.me/purl/versa/type","http://schema.org/Person"],["http://schema.org/name","Augusta Ada King"],["http://schema.org/birthDate","1815-12-10"],["http://schema.org/deathDate","1852-11-27"]]', b'1iIRmLeN1TY'),
('[["http://bibfra.me/purl/versa/type","http://schema.org/Person"],["http://schema.org/name","Augusta Ada King"]]', b'xjgOrUFiw_o'),
]


@pytest.mark.parametrize('inputdata,expected', RESOURCE_ID_CASES)
def test_compute_librarylink_hash(inputdata, expected):
    bits128 = mmh3.hash64(inputdata)
    bits64 = bits128[0]
    hexbits64 = hex(bits64)
    hexbits128 = [ hex(x) for x in bits128 ]
    octets = struct.pack('!q', bits64)
    octets_raw = [ hex(c) for c in octets ]
    octets_rawer = [ hex(c)[2:].zfill(2) for c in octets ]
    encoded = base64.urlsafe_b64encode(octets).rstrip(b"=")
    encoded_unsafe = base64.b64encode(octets).rstrip(b"=")
    assert encoded == expected, (encoded, expected)
    encoded = simple_hashstring(inputdata).encode('ascii')
    assert encoded == expected, (encoded, expected)
    #print('\n'.join([str(x) for x in [bits128, bits64, hexbits64, hexbits128, octets, octets_raw, octets_rawer, encoded, encoded_unsafe]]))


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
