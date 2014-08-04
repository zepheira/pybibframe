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


#http://stackoverflow.com/questions/5574042/string-slugification-in-python
## {{{ http://code.activestate.com/recipes/577257/ (r2)
_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    
    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)
## end of http://code.activestate.com/recipes/577257/ }}}

