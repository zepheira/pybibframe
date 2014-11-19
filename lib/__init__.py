# bibframe

from versa import I

BFZ = I('http://bibfra.me/vocab/')
BFLC = I('http://bibframe.org/vocab/')

#A way to register services to specialize bibframe.py processing
#Maps URL to callable
g_services = {}

BF_INIT_TASK = 'http://bibfra.me/tool/pybibframe#task.init'
BF_MARCREC_TASK = 'http://bibfra.me/tool/pybibframe#task.marcrec'
BF_MATRES_TASK = 'http://bibfra.me/tool/pybibframe#task.materialize-resource'
BF_FINAL_TASK = 'http://bibfra.me/tool/pybibframe#task.final'

#def register_service(coro, iri=None):
#    iri = iri or coro.iri
#    g_services[iri] = coro
#    return

def register_service(sinfo):
    g_services.update(sinfo)
    return

