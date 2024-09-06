from qgis.core import QgsRasterLayer, QgsProject, QgsVectorLayer, QgsRectangle, QgsMessageLog, Qgis
from qgis.utils import iface

from typing import Literal
from typing import TypedDict
from .utils import add_layer, color_object, convert_coordinate, log_tag


def add_map_layer(uri: str, layer_name: str, provider: str):
    layer = QgsRasterLayer(uri, layer_name, provider)
    add_layer(layer)


def add_feature_layer(uri: str, layer_name: str, provider: str):
    layer = QgsVectorLayer(uri, layer_name, provider)
    add_layer(layer)


def color_category(layer_name: str, renderer_name: str, color: [int, int, int]):
    color_object(layer_name, renderer_name, color, 'category')


def color_range(layer_name: str, renderer_name: str, color: [int, int, int]):
    color_object(layer_name, renderer_name, color, 'range')


def color_rule(layer_name: str, renderer_name: str, color: [int, int, int]):
    color_object(layer_name, renderer_name, color, 'rule')


def remove_all_map_layers():
    QgsProject.instance().removeAllMapLayers()


def go_to_location(west: float, south: float, east: float, north: float):
    QgsMessageLog.logMessage(f"Loading {west}{south}{east}{north}", log_tag, level=Qgis.MessageLevel.Info)
    ll = convert_coordinate(west, south)
    ur = convert_coordinate(east, north)
    QgsMessageLog.logMessage(f"converting {ll.x()}{ll.y()}{ur.x()}{ur.y()}", log_tag, level=Qgis.MessageLevel.Info)

    zoom_rect = QgsRectangle(ll.x(), ll.y(), ur.x(), ur.y())
    canvas = iface.mapCanvas()
    canvas.setExtent(zoom_rect)
    canvas.refresh()


function_map = {"add_map_layer": add_map_layer, "add_feature_layer": add_feature_layer,
                "color_category": color_category, "color_range": color_range, "color_rule": color_rule,
                "go_to_location": go_to_location,
                "remove_all_map_layers": remove_all_map_layers}


class MappedFunction(TypedDict):
    function_name: Literal["addMapLayer", "removeAllMapLayers"]
    parameters: dict


class ChatResponse(TypedDict):
    chat: str
    mapped_function: MappedFunction
