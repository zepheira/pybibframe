'''
For processing MARC/XML
Uses SAX for streaming process
Notice however, possible security vulnerabilities:
https://docs.python.org/3/library/xml.html#xml-vulnerabilities
'''

import asyncio
import collections
import logging
from collections import defaultdict
import warnings

from xml import sax
#from xml.sax.handler import ContentHandler
#from xml.sax.saxutils import XMLGenerator

from bibframe import g_services
from bibframe import BF_INIT_TASK, BF_MARCREC_TASK, BF_FINAL_TASK
from bibframe.reader.marcextra import transforms as extra_transforms

import rdflib

from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES
from versa import util
from versa.driver import memory

from bibframe import BFZ, BFLC, register_service
from bibframe.reader import marc
from bibframe.writer import rdf
from bibframe.reader.marcpatterns import TRANSFORMS
from bibframe.reader.util import AVAILABLE_TRANSFORMS

BFNS = rdflib.Namespace(BFZ)
BFCNS = rdflib.Namespace(BFZ + 'cftag/')
BFDNS = rdflib.Namespace(BFZ + 'dftag/')
VNS = rdflib.Namespace(VERSA_BASEIRI)

MARCXML_NS = marc.MARCXML_NS

#Subclass from ContentHandler in order to gain default behaviors
class marcxmlhandler(sax.ContentHandler):
    def __init__(self, sink, *args, **kwargs):
        self._sink = sink
        next(self._sink) #Start the coroutine running
        self._getcontent = False
        self._empty = True
        sax.ContentHandler.__init__(self, *args, **kwargs)
        return

    def startElementNS(self, name, qname, attributes):
        (ns, local) = name
        if ns == MARCXML_NS:
            #Ignore the 'collection' element
            #What to do with the record/@type
            if local == 'record':
                self._empty = False
                #XXX: Entity base IRI needed?
                self._record_id = 'record-{0}:{1}'.format(self._locator.getLineNumber(), self._locator.getColumnNumber())
                #Versa model with a representation of the record
                self._record_model = memory.connection()#logger=logger)
            elif local == 'leader':
                self._chardata_dest = ''
                self._link_iri = MARCXML_NS + '/leader'
                self._marc_attributes = {}
                self._getcontent = True
            elif local == 'controlfield':
                self._chardata_dest = ''
                self._link_iri = MARCXML_NS + '/control/' + attributes[None, 'tag'].strip()
                #Control tags have neither indicators nor subfields
                self._marc_attributes = {'tag': attributes[None, 'tag'].strip()}
                self._getcontent = True
            elif local == 'datafield':
                self._link_iri = MARCXML_NS + '/data/' + attributes[None, 'tag'].strip()
                self._marc_attributes = {k[1]: v.strip() for (k, v) in attributes.items()}
            elif local == 'subfield':
                self._chardata_dest = ''
                self._subfield = attributes[None, 'code'].strip()
                self._getcontent = True
        return

    def characters(self, data):
        if self._getcontent:
            self._chardata_dest += data

    def endElementNS(self, name, qname):
        (ns, local) = name
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
                self._record_model.add(self._record_id, self._link_iri, '', self._marc_attributes)
                self._getcontent = False
            elif local == 'subfield':
                self._marc_attributes.setdefault(self._subfield, []).append(self._chardata_dest)
            elif local in ('leader', 'controlfield'):
                self._record_model.add(self._record_id, self._link_iri, self._chardata_dest, self._marc_attributes)
                self._getcontent = False
        return

    def endDocument(self):
        if self._empty:
            warnings.warn("No records found. Possibly an XML namespace problem.", RuntimeWarning)
        self._sink.close()

#PYTHONASYNCIODEBUG = 1

def bfconvert(inputs, entbase=None, model=None, out=None, limit=None, rdfttl=None, rdfxml=None, config=None, verbose=False, logger=logging, loop=None, canonical=False):
    '''
    inputs - List of MARC/XML files to be parsed and converted to BIBFRAME RDF (Note: want to allow singular input strings)
    entbase - Base IRI to be used for creating resources.
    model - model instance for internal use
    out - file where raw Versa JSON dump output should be written (default: write to stdout)
    limit - Limit the number of records processed to this number. If omitted, all records will be processed.
    rdfttl - stream to where RDF Turtle output should be written
    rdfxml - stream to where RDF/XML output should be written
    config - configuration information
    verbose - If true show additional messages and information (default: False)
    logger - logging object for messages
    loop - optional asyncio event loop to use
    canonical - output Versa's canonical form?
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

    ids = marc.idgen(entbase)
    if model is None: model = memory.connection(logger=logger)
    g = rdflib.Graph()
    if canonical: global_model = memory.connection()

    extant_resources = None
    #extant_resources = set()
    def postprocess():
        #No need to bother with Versa -> RDF translation if we were not asked to generate Turtle
        if any((rdfttl, rdfxml)): rdf.process(model, g, to_ignore=extant_resources, logger=logger)
        if canonical: global_model.add_many([(o,r,t,a) for (rid,(o,r,t,a)) in model])

        model.create_space()

    #Set up event loop if not provided
    if not loop:
        loop = asyncio.get_event_loop()

    #Allow configuration of a separate base URI for vocab items (classes & properties)
    #XXX: Is this the best way to do this, or rather via a post-processing plug-in
    vb = config.get('vocab-base-uri', BFZ)

    transform_iris = config.get('transforms', {})
    if transform_iris:
        transforms = {}
        for tiri in transform_iris:
            try:
                transforms.update(AVAILABLE_TRANSFORMS[tiri])
            except KeyError:
                raise Exception('Unknown transforms set {0}'.format(tiri))
    else:
        transforms = TRANSFORMS

    marcextras_vocab = config.get('marcextras-vocab')

    #Initialize auxiliary services (i.e. plugins)
    plugins = []
    for pc in config.get('plugins', []):
        try:
            pinfo = g_services[pc['id']]
            plugins.append(pinfo)
            pinfo[BF_INIT_TASK](pinfo, config=pc)
        except KeyError:
            raise Exception('Unknown plugin {0}'.format(pc['id']))

    limiting = [0, limit]
    #logger=logger,
    
    for inf in inputs:
        sink = marc.record_handler( loop,
                                    model,
                                    entbase=entbase,
                                    vocabbase=vb,
                                    limiting=limiting,
                                    plugins=plugins,
                                    ids=ids,
                                    postprocess=postprocess,
                                    out=out,
                                    logger=logger,
                                    transforms=transforms,
                                    extra_transforms=extra_transforms(marcextras_vocab),
                                    canonical=canonical)
        parser = sax.make_parser()
        #parser.setContentHandler(marcxmlhandler(receive_recs()))
        parser.setContentHandler(marcxmlhandler(sink))
        parser.setFeature(sax.handler.feature_namespaces, 1)
        @asyncio.coroutine
        #Wrap the parse operation to make it a task in the event loop
        def wrap_task():
            parser.parse(inf)
            yield
        task = asyncio.async(wrap_task(), loop=loop)
        #parse_marcxml(inf, sink)
        try:
            loop.run_until_complete(task)
        except Exception as ex:
            raise ex
        finally:
            loop.close()

    if canonical:
        out.write(repr(global_model))

    if vb == BFZ:
        g.bind('bf', BFNS)
        g.bind('bfc', BFCNS)
        g.bind('bfd', BFDNS)
    else:
        g.bind('vb', rdflib.Namespace(vb))
    if entbase:
        g.bind('ent', entbase)

    if rdfttl is not None:
        logger.debug('Converting to RDF.')
        rdfttl.write(g.serialize(format="turtle"))

    if rdfxml is not None:
        logger.debug('Converting to RDF.')
        rdfxml.write(g.serialize(format="pretty-xml"))
    return

