'''
For processing MARC/XML
Uses SAX for streaming process
Notice however, possible security vulnerabilities:
https://docs.python.org/3/library/xml.html#xml-vulnerabilities
'''

from collections import defaultdict, OrderedDict
import unicodedata
import warnings

import xml.parsers.expat

from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES
from versa import util
from versa.driver import memory

from bibframe.reader import marc

MARCXML_NS = marc.MARCXML_NS

# valid subfield codes
VALID_SUBFIELDS = set(range(ord('a'), ord('z')+1))
VALID_SUBFIELDS.update(range(ord('A'), ord('Z')+1))
VALID_SUBFIELDS.update(range(ord('0'), ord('9')+1))
VALID_SUBFIELDS.add(ord('-'))

# validates tags in URL form
IS_VALID_TAG = lambda t: len(t.rsplit('/',1)[-1]) == 3

NSSEP = ' '

class expat_callbacks(object):
    def __init__(self, sink, parser, attr_cls=dict, attr_list_cls=list, lax=False):
        self._sink = sink
        self._getcontent = False
        self.no_records = True
        self._attr_cls = attr_cls # dict-like class to use for holding Versa attributes
        self._attr_list_cls = attr_list_cls # list-like class to use for holding Versa attribute values
        self._lax = lax
        self._parser = parser
        self._record_model = None
        return

    def start_element(self, name, attributes):
        if self._lax:
            (head, sep, tail) = name.partition(':')
            local = tail or head
            ns = MARCXML_NS #Just assume all elements are MARC/XML
        else:
            ns, local = name.split(NSSEP) if NSSEP in name else (None, name)
        if ns == MARCXML_NS:
            #Ignore the 'collection' element
            #What to do with the record/@type
            if local == 'record':
                self.no_records = False
                #XXX: Entity base IRI needed?
                self._record_id = 'record-{0}:{1}'.format(self._parser.CurrentLineNumber, self._parser.CurrentColumnNumber)
                #Versa model with a representation of the record
                #For input model plugins, important that natural ordering be preserved
                self._record_model = memory.connection(attr_cls=self._attr_cls)#logger=logger)
            elif local == 'leader':
                self._chardata_dest = ''
                self._link_iri = MARCXML_NS + '/leader'
                self._marc_attributes = self._attr_cls()
                self._getcontent = True
            elif local == 'controlfield':
                self._chardata_dest = ''
                self._link_iri = MARCXML_NS + '/control/' + attributes['tag'].strip()
                #Control tags have neither indicators nor subfields
                self._marc_attributes = self._attr_cls({'tag': attributes['tag'].strip()})
                self._getcontent = True
            elif local == 'datafield':
                self._link_iri = MARCXML_NS + '/data/' + attributes['tag'].strip()
                self._marc_attributes = self._attr_cls(([k, v.strip()] for (k, v) in attributes.items() if ' ' not in k))
            elif local == 'subfield':
                self._chardata_dest = ''
                self._subfield = attributes['code'].strip()
                if not self._subfield or ord(self._subfield) not in VALID_SUBFIELDS:
                    self._subfield = '_'
                self._getcontent = True
        return

    def end_element(self, name):
        if self._lax:
            (head, sep, tail) = name.partition(':')
            local = tail or head
            ns = MARCXML_NS #Just assume all elements are MARC/XML
        else:
            ns, local = name.split(NSSEP) if NSSEP in name else (None, name)
        if ns == MARCXML_NS:
            if local == 'record':
                try:
                    self._sink.send(self._record_model)
                except StopIteration:
                    #Handler coroutine has declined to process more records. Perhaps it's hit a limit
                    #FIXME would be nice to throw some sort of signal to stop parse. Or...we can wait until we've evolved beyond SAX to enhance the event architecture
                    pass
            elif local == 'datafield':
                #Convert list of pairs of subfield codes/values to dict of lists (since there can be multiple of each subfields)
                #sfdict = defaultdict(list)
                #[ sfdict[sf[0]].append(sf[1]) for sf in self._record[-1][3] ]
                #self._record[-1][3] = sfdict
                if self._record_model and IS_VALID_TAG(self._link_iri):
                    self._record_model.add(self._record_id, self._link_iri, '', self._marc_attributes)
                self._getcontent = False
            elif local == 'subfield':
                self._marc_attributes.setdefault(self._subfield, self._attr_list_cls()).append(self._chardata_dest)
            elif local == 'leader':
                if self._record_model: self._record_model.add(self._record_id, self._link_iri, self._chardata_dest, self._marc_attributes)
                self._getcontent = False
            elif local == 'controlfield':
                if self._record_model and IS_VALID_TAG(self._link_iri):
                    self._record_model.add(self._record_id, self._link_iri, self._chardata_dest, self._marc_attributes)
                self._getcontent = False

    def char_data(self, data):
        if self._getcontent:
            #NFKC normalization precombines composed characters and substitutes compatibility codepoints
            #We want to make sure we're dealing with comparable & consistently hashable strings throughout the toolchain
            self._chardata_dest += unicodedata.normalize('NFKC', data)


#PYTHONASYNCIODEBUG = 1


def handle_marcxml_source(infname, sink, args, attr_cls, attr_list_cls):
    #Cannot reuse a pyexpat parser, so must create a new one for each input file
    next(sink) #Start the coroutine running
    with open(infname, 'rb') as inf:
        lax = args['lax']
        if lax:
            parser = xml.parsers.expat.ParserCreate()
        else:
            parser = xml.parsers.expat.ParserCreate(namespace_separator=NSSEP)

        handler = expat_callbacks(sink, parser, attr_cls, attr_list_cls, lax)

        parser.StartElementHandler = handler.start_element
        parser.EndElementHandler = handler.end_element
        parser.CharacterDataHandler = handler.char_data
        parser.buffer_text = True

        parser.ParseFile(inf)
        if handler.no_records:
            warnings.warn("No records found in this file. Possibly an XML namespace problem (try using the 'lax' flag).", RuntimeWarning)
    return

