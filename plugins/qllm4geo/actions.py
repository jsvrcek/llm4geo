from typing import TypedDict

from qgis.core import Qgis, QgsMessageLog, QgsRasterLayer, QgsProject
from typing import Literal

log_tag = "LLM4GEO"

def add_map_layer(layer_params):
    wms_layer = QgsRasterLayer(*layer_params)

    if not wms_layer.isValid():
        QgsMessageLog.logMessage("Layer failed to load!", log_tag, level=Qgis.Info)
    else:
        QgsProject.instance().addMapLayer(wms_layer)
        QgsMessageLog.logMessage("Layer added successfully!", log_tag, level=Qgis.Info)

def remove_all_map_layers():
    QgsProject.instance().removeAllMapLayers()

function_map = {"add_map_layer": add_map_layer, "remove_all_map_layers": remove_all_map_layers}

class MappedFuction(TypedDict):
    function_name: Literal["addMapLayer", "removeAllMapLayers"]
    parameters: dict

class ChatResponse(TypedDict):
    chat: str
    mapped_function: MappedFuction


