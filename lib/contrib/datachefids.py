#datachef.ids

'''
>>> from datachef.ids import simple_hashstring
>>> simple_hashstring("The quick brown fox jumps over the lazy dog")
B7x7vEvj
'''

import re
import base64
import struct

import mmh3

from amara3 import iri
from amara3.util import coroutine

SLUGCHARS = r'a-zA-Z0-9\-\_'
OMIT_FROM_SLUG_PAT = re.compile('[^%s]'%SLUGCHARS)
NORMALIZE_UNDERSCORES_PAT = re.compile('__+')
#slug_from_title = slug_from_title = lambda t: OMIT_FROM_SLUG_PAT.sub('_', t).lower().decode('utf-8')

MAX32LESS1 = 4294967295 #2**32-1

#For discussion of general purpose hashing as used in this code
#https://github.com/uogbuji/datachef/wiki/gp-hashing

def simple_hashstring(obj, bits=48):
    '''
    Creates a simple hash in brief string form from obj
    bits is an optional bit width, defaulting to 48, and should be in multiples of 8

    >>> from datachef.ids import simple_hashstring
    >>> simple_hashstring("The quick brown fox jumps over the lazy dog")
    B7x7vEvj
    '''
    #Useful discussion of techniques here: http://stackoverflow.com/questions/1303021/shortest-hash-in-python-to-name-cache-files

    #Abandoned idea of using MD5 and truncating
    #raw_hash = hashlib.md5(title).digest()
    #Abandoned Adler32 for MurmurHash3
    #raw_hash = struct.pack('i', zlib.adler32(title[:plain_len]))
    #Use MurmurHash3
    #Get a 64-bit integer, the first half of the 128-bit tuple from mmh and then bit shift it to get the desired bit length
    basis = mmh3.hash64(str(obj))[0] >> (64-bits)
    raw_hash = struct.pack('l', basis)[:-int((64-bits)/8)]
    hashstr = base64.urlsafe_b64encode(raw_hash).rstrip(b"=")
    return hashstr.decode('ascii')


def create_slug(title, plain_len=None):
    '''
    Tries to create a slug from a title, trading off collision risk with readability and minimized cruft

    title - a unicode object with a title to use as basis of the slug
    plain_len - the maximum character length preserved (from the beginning) of the title

    >>> from datachef.ids import create_slug
    >>> create_slug(u"The  quick brown fox jumps over the lazy dog")
    u'the_quick_brown_fox_jumps_over_the_lazy_dog'
    >>> create_slug(u"The  quick brown fox jumps over the lazy dog", 20)
    u'the_quick_brown_fox'
    '''
    if plain_len: title = title[:plain_len]
    pass1 = OMIT_FROM_SLUG_PAT.sub('_', title).lower()
    return NORMALIZE_UNDERSCORES_PAT.sub('_', pass1)


# Based loosely on http://stackoverflow.com/questions/5574042/string-slugification-in-python
# & http://code.activestate.com/recipes/577257/
_CHANGEME_RE = re.compile(r'[^\w\-_]')
#_SLUGIFY_HYPHENATE_RE = re.compile(r'[-\s]+')
def slugify(value, hyphenate=True, lower=True):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).strip()
    replacement = '-' if hyphenate else ''
    if lower: value = value.lower()
    return _CHANGEME_RE.sub(replacement, value)


#from datachef.ids import simple_hashstring
@coroutine
def idgen(idbase, tint=None):
    '''
    Generate an IRI as a hash of given information, or just make one up if None given
    idbase -- Base URI for generating links
    tint -- String that affects the sequence of IDs generated if sent None

    >>> from datachef.ids import idgen
    >>> g = idgen(None)
    >>> next(g) #Or g.send(None)
    'RtW-3skq'
    >>> next(g)
    'e4r-u_tx'
    >>> g.send('spam')
    'ThKLPHvp'
    >>> next(g)
    'YbGlkNf9'
    >>> g.send('spam')
    'ThKLPHvp'
    >>> g.send('eggs')
    'HeBrpNON'
    '''
    #Simple tumbler for now, possibly switch to random number, with some sort of sequence override for unit testing
    counter = -1
    to_hash = None
    while True:
        if to_hash is None:
            to_hash = str(counter)
            if tint: to_hash += tint
        to_hash = iri.absolutize(to_hash, idbase) if idbase else to_hash
        to_hash = yield simple_hashstring(to_hash)
        counter += 1

