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
    isbn_tags = {}
    for isbn in isbns:
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
    for c14nisbn, variants in invert_dict(c14ned).items():
        yield c14nisbn, isbn_tags[variants[0]]
        #We'll use the heuristic that the longest ISBN number is the best
        #variants.sort(key=len, reverse=True) # sort by descending length
        #yield variants[0], isbn_tags[variants[0]]
    return

