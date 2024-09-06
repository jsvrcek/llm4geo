from qgis.gui import QgisInterface
from .api_plugin import ApiPlugin

def classFactory(iface: QgisInterface):
    return ApiPlugin(iface)
