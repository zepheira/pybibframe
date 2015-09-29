'''
'''

import re
import logging

NON_ISBN_CHARS = re.compile(u'\D')

def invert_dict(d):
     #http://code.activestate.com/recipes/252143-invert-a-dictionary-one-liner/#c3
    #See also: http://pypi.python.org/pypi/bidict
    #Though note: http://code.activestate.com/recipes/576968/#c2
    inv = {}
    for k, v in d.items():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv


#TODO: Also split on multiple 260 fields

def canonicalize_isbns(isbns, logger=logging):
    #http://www.hahnlibrary.net/libraries/isbncalc.html
    canonicalized = {}
    for isbn in isbns:
        if len(isbn) == 9: #ISBN-10 without check digit
            c14ned = u'978' + isbn
        elif len(isbn) == 10: #ISBN-10 with check digit
            c14ned = u'978' + isbn[:-1]
        elif len(isbn) == 12: #ISBN-13 without check digit
            c14ned = isbn
        elif len(isbn) == 13: #ISBN-13 with check digit
            c14ned = isbn[:-1]
        else:
            logger.debug('BAD ISBN: {0}'.format(isbn))
            isbn = None
        if isbn:
            canonicalized[isbn] = c14ned
    return canonicalized


def isbn_list(isbns, logger=logging):
    '''
    Take a list of ISBN descriptions, in the form of an ISBN and an optional annotation
    Return a list of normalized ISBNs in 12-digit form (i.e. ISBN-13 *without checkbit*), and matching annotations

    >>> from bibframe.isbnplus import isbn_list
    >>> isbns = ['9783136128046 (GTV)', '1588902153 (TNY)', '9781588902153 (TNY)', '3136128044 (GTV)']
    >>> list(isbn_list(isbns))
    [('978158890215', '(TNY)'), ('978313612804', '(GTV)')]
    '''
    isbn_tags = {}
    for isbn in isbns:
        assert isinstance(isbn, str), "non-string passed to isbn_list: {0}".format(repr(isbn))
        parts = isbn.split(None, 1)
        if not parts:
            logger.debug('Blank ISBN')
            continue
        #Remove any cruft from ISBNs. Leave just the digits
        cleaned_isbn = NON_ISBN_CHARS.subn(u'', parts[0])[0]
        if len(parts) == 1:
            #FIXME: More generally strip non-digit chars from ISBNs
            isbn_tags[cleaned_isbn] = None
        else:
            isbn_tags[cleaned_isbn] = parts[1]
    c14ned = canonicalize_isbns(isbn_tags.keys(), logger=logger)
    for c14nisbn, variants in sorted(invert_dict(c14ned).items()):
        yield c14nisbn, isbn_tags[variants[0]]
        #We'll use the heuristic that the longest ISBN number is the best
        #variants.sort(key=len, reverse=True) # sort by descending length
        #yield variants[0], isbn_tags[variants[0]]
    return


def compute_ean13_check(ean):
    '''
    Compute the EAN-13 check digit. Note: ISBN-13 is the same scheme as EAN-13

    Algorithm: http://en.wikipedia.org/wiki/International_Article_Number_(EAN)#Calculation_of_checksum_digit

    >>> from bibframe.isbnplus import compute_ean13_check
    >>> compute_ean13_check('4006381333931')
    '4006381333931'
    >>> compute_ean13_check('400638133393')
    '4006381333931'
    >>> compute_ean13_check('9780615886084') #Ndewo, Colorado :)
    '9780615886084'
    >>> compute_ean13_check('978061588608')
    '9780615886084'
    >>> compute_ean13_check('978068807546')
    '9780688075460'
    '''
    assert len(ean) in (12, 13)
    def weight_gen():
        '''
        Generator of alternating 1 and 3 weights
        '''
        while True:
            yield 1
            yield 3

    wg = weight_gen()
    ean = ean[:12]
    s = sum([ int(d) * next(wg) for d in ean ])

    #print(str(10 - s % 10)[-1])
    ean_checked = ean + str(10 - s % 10)[-1]
    assert len(ean_checked) == 13
    return ean_checked
