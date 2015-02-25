# bibframe

from versa import I

# use BFZ namespace to scope MARC tags that don't match transformation recipes 
BFZ = I('http://bibfra.me/vocab/marcext/')
BFLC = I('http://bibframe.org/vocab/')

#A way to register services to specialize bibframe.py processing
#Maps URL to callable
g_services = {}

BF_INIT_TASK = 'http://bibfra.me/tool/pybibframe#task.init'
BF_MARCREC_TASK = 'http://bibfra.me/tool/pybibframe#task.marcrec'
BF_MATRES_TASK = 'http://bibfra.me/tool/pybibframe#task.materialize-resource'
BF_FINAL_TASK = 'http://bibfra.me/tool/pybibframe#task.final'

BL = 'http://bibfra.me/vocab/lite/'
BA = 'http://bibfra.me/vocab/annotation/'
REL = 'http://bibfra.me/vocab/relation/'
MARC = 'http://bibfra.me/vocab/marc/'
RBMS = 'http://bibfra.me/vocab/rbms/'
AV = 'http://bibfra.me/vocab/audiovisual/'



#def register_service(coro, iri=None):
#    iri = iri or coro.iri
#    g_services[iri] = coro
#    return

def register_service(sinfo):
    g_services.update(sinfo)
    return

