# bibframe.plugin

from bibframe.plugin import linkreport, labelizer
from bibframe import register_service

register_service(linkreport.PLUGIN_INFO)
register_service(labelizer.PLUGIN_INFO)
