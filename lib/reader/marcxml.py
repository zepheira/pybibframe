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
                self._chardata_dest = [CONTROLFIELD, attributes[None, u'tag'], u'']
                self._record.append(self._chardata_dest)
                self._getcontent = True
            elif local == u'datafield':
                self._record.append([DATAFIELD, attributes[None, u'tag'], attributes.copy(), []])
            elif local == u'subfield':
                self._chardata_dest = [attributes[None, u'code'], u'']
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
                    #FIXME would be nice to throw some sort of signal to setp parse. Or...we should maybe rearchitect the event architecture (easier when we've evolved beyond SAX) :)
                    pass
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

    def postprocess(rec):
        #No need to bother with Versa -> RDF translation if we were not asked to generate Turtle
        if rdfttl is not None: rdf.process(m, g, logger=logger)
        m.create_space()

    #Set up event loop
    loop = asyncio.get_event_loop()

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
        sink = marc.record_handler(loop, m, idbase=base, limiting=limiting, plugins=plugins, ids=ids, postprocess=postprocess, out=out, logger=logger)
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

    if rdfttl is not None: rdfttl.write(g.serialize(format="turtle"))
    return

