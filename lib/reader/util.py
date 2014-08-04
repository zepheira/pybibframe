

import re
# Based on http://stackoverflow.com/questions/5574042/string-slugification-in-python
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


def normalizeparse(text_in):
    return slugify(text_in, False)
    #return datachef.slugify(value)


from enum import Enum #https://docs.python.org/3.4/library/enum.html

class action(Enum):
    replace = 1



