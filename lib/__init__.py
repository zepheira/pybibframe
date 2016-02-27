# bibframe

from versa import I

# use BFZ namespace to scope MARC tags that don't match transformation recipes
BFZ = I('http://bibfra.me/vocab/marcext/')
BFLC = I('http://bibframe.org/vocab/')

#A way to register services to specialize bibframe.py processing
#Maps URL to callable
g_services = {}

BF_INIT_TASK = 'http://bibfra.me/tool/pybibframe#task.init'
BF_INPUT_TASK = 'http://bibfra.me/tool/pybibframe#task.input-model'
BF_INPUT_XREF_TASK = 'http://bibfra.me/tool/pybibframe#task.input-xref-model'
BF_MARCREC_TASK = 'http://bibfra.me/tool/pybibframe#task.marcrec'
BF_MATRES_TASK = 'http://bibfra.me/tool/pybibframe#task.materialize-resource'
BF_FINAL_TASK = 'http://bibfra.me/tool/pybibframe#task.final'

BL = I('http://bibfra.me/vocab/lite/')
BA = I('http://bibfra.me/vocab/annotation/')
REL = I('http://bibfra.me/vocab/relation/')
MARC = I('http://bibfra.me/vocab/marc/')
RBMS = I('http://bibfra.me/vocab/rbms/')
AV = I('http://bibfra.me/vocab/audiovisual/')
ARCHIVE = I('http://bibfra.me/vocab/archive/')
MARCEXT = I('http://bibfra.me/vocab/marcext/')

POSTPROCESS_AS_INSTANCE = 'http://bibfra.me/tool/pybibframe#marc.postprocess.instance'

#def register_service(coro, iri=None):
#    iri = iri or coro.iri
#    g_services[iri] = coro
#    return

def register_service(sinfo):
    g_services.update(sinfo)
    return
