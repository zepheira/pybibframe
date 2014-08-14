'''
For processing MARC/XML
Uses SAX for streaming process
Notice however, possible security vulnerabilities:
https://docs.python.org/3/library/xml.html#xml-vulnerabilities
'''

import asyncio
import collections
import logging

from xml import sax
#from xml.sax.handler import ContentHandler
#from xml.sax.saxutils import XMLGenerator

#from bibframe.contrib.xmlutil import normalize_text_filter
from bibframe.reader.marc import LEADER, CONTROLFIELD, DATAFIELD
from bibframe import g_services
from bibframe import BF_INIT_TASK, BF_MARCREC_TASK, BF_FINAL_TASK

import rdflib

from versa import I, VERSA_BASEIRI
from versa import util
from versa.driver import memory

from bibframe import BFZ, BFLC, register_service
from bibframe.reader import marc
from bibframe.writer import rdf

BFNS = rdflib.Namespace(BFZ)
BFCNS = rdflib.Namespace(BFZ + 'cftag/')
BFDNS = rdflib.Namespace(BFZ + 'dftag/')
VNS = rdflib.Namespace(VERSA_BASEIRI)


MARCXML_NS = "http://www.loc.gov/MARC21/slim"

#Subclass from ContentHandler in order to gain default behaviors
class marcxmlhandler(sax.ContentHandler):
    def __init__(self, sink, *args, **kwargs):
        self._sink = sink
        next(self._sink) #Start the coroutine running
        self._getcontent = False
        sax.ContentHandler.__init__(self, *args, **kwargs)

    def startElementNS(self, name, qname, attributes):
        (ns, local) = name
        if ns == MARCXML_NS:
            #if local == u'collection':
            #    return
            if local == u'record':
                self._record = []
            elif local == u'leader':
                self._chardata_dest = [LEADER, u'']
                self._record.append(self._chardata_dest)
                self._getcontent = True
            elif local == u'controlfield':
                self._chardata_dest = [CONTROLFIELD, attributes[None, u'tag'].strip(), u'']
                self._record.append(self._chardata_dest)
                self._getcontent = True
            elif local == u'datafield':
                self._record.append([DATAFIELD, attributes[None, u'tag'].strip(), dict((k, v.strip()) for (k, v) in attributes.items()), []])
            elif local == u'subfield':
                self._chardata_dest = [attributes[None, u'code'].strip(), u'']
                self._record[-1][3].append(self._chardata_dest)
                self._getcontent = True
        return

    def characters(self, data):
        if self._getcontent:
            self._chardata_dest[-1] += data

    def endElementNS(self, name, qname):
        (ns, local) = name
        if ns == MARCXML_NS:
            if local == u'record':
                try:
                    self._sink.send(self._record)
                except StopIteration:
                    #Handler coroutine has declined to process more records. Perhaps it's hit a limit
                    #FIXME would be nice to throw some sort of signal to stop parse. Or...we can wait until we've evolved beyond SAX to enhance the event architecture
                    pass
            elif local == u'datafield':
                #Convert list of pairs to disct
                self._record[-1][3] = dict(( (sf[0], sf[1]) for sf in self._record[-1][3] ))
                self._getcontent = False
            elif local in (u'leader', u'controlfield', u'subfield'):
                self._getcontent = False
        return

    def endDocument(self):
        self._sink.close()

#PYTHONASYNCIODEBUG = 1

def bfconvert(inputs, base=None, out=None, limit=None, rdfttl=None, config=None, verbose=False, logger=logging):
    '''
    inputs - List of MARC/XML files to be parsed and converted to BIBFRAME RDF (Note: want to allow singular input strings)
    out - file where raw Versa JSON dump output should be written (default: write to stdout)
    rdfttl - stream to where RDF Turtle output should be written
    config - configuration information
    limit - Limit the number of records processed to this number. If omitted, all records will be processed.
    base - Base IRI to be used for creating resources.
    verbose - If true show additional messages and information (default: False)
    logger - logging object for messages
    '''
    #if stats:
    #    register_service(statsgen.statshandler)

    config = config or {}
    if hasattr(inputs, 'read') and hasattr(inputs, 'close'):
        #It's a file type?
        inputs = [inputs]
    if limit is not None:
        try:
            limit = int(limit)
        except ValueError:
            logger.debug('Limit must be a number, not "{0}". Ignoring.'.format(limit))

    ids = marc.idgen(base)
    m = memory.connection()
    g = rdflib.Graph()
    g.bind('bf', BFNS)
    g.bind('bfc', BFCNS)
    g.bind('bfd', BFDNS)
    g.bind('v', VNS)
    if base:
        g.bind('ent', base)

    extant_resources = None
    #extant_resources = set()
    def postprocess(rec):
        #No need to bother with Versa -> RDF translation if we were not asked to generate Turtle
        if rdfttl is not None: rdf.process(m, g, to_ignore=extant_resources, logger=logger)
        m.create_space()

    #Set up event loop
    loop = asyncio.get_event_loop()

    #Allow configuration of a separate base URI for vocab items (classes & properties)
    #XXX: Is this the best way to do this, or rather via a post-processing plug-in
    vb = config.get(u'vocab-base-uri', BFZ)

    #Initialize auxiliary services (i.e. plugins)
    plugins = []
    for pc in config.get(u'plugins', []):
        try:
            pinfo = g_services[pc[u'id']]
            plugins.append(pinfo)
            pinfo[BF_INIT_TASK](pinfo, config=pc)
        except KeyError:
            raise Exception(u'Unknown plugin {0}'.format(pc[u'id']))

    limiting = [0, limit]
    #logger=logger,
    
    for inf in inputs:
        sink = marc.record_handler(loop, m, entbase=base, vocabbase=vb, limiting=limiting, plugins=plugins, ids=ids, postprocess=postprocess, out=out, logger=logger)
        parser = sax.make_parser()
        #parser.setContentHandler(marcxmlhandler(receive_recs()))
        parser.setContentHandler(marcxmlhandler(sink))
        parser.setFeature(sax.handler.feature_namespaces, 1)
        @asyncio.coroutine
        #Wrap the parse operation to make it a task in the event loop
        def wrap_task():
            parser.parse(inf)
            yield
        asyncio.Task(wrap_task())
        #parse_marcxml(inf, sink)
        loop.run_forever()

    if rdfttl is not None:
        logger.debug('Converting to RDF.')
        rdfttl.write(g.serialize(format="turtle"))
    return

