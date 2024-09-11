from time import sleep

from qgis.PyQt.QtGui import QColor

from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsVectorLayer, QgsGraduatedSymbolRenderer, \
    QgsCategorizedSymbolRenderer, QgsRuleBasedRenderer, QgsPointXY, QgsCoordinateReferenceSystem, \
    QgsCoordinateTransform, \
    QgsApplication

from qgis.utils import iface

from typing import Literal

log_tag = "LLM4GEO"


def add_layer(layer):
    if not layer.isValid():
        QgsMessageLog.logMessage("Layer failed to load!", log_tag, level=Qgis.Info)
        raise Exception(f"Failed to load layer.")
    else:
        QgsProject.instance().addMapLayer(layer)
        QgsMessageLog.logMessage("Layer added successfully!", log_tag, level=Qgis.Info)


def get_layer(layer_name: str) -> QgsVectorLayer:
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if layers:
        return layers[0]
    raise Exception(f"Layer {layer_name} was not found.")


def get_category_by_label(renderer: QgsCategorizedSymbolRenderer, cat_label: str):
    for idx, cat in enumerate(renderer.categories()):
        if cat.label() == cat_label:
            return idx, cat
    raise Exception(f"Category renderer {cat_label} was not found.")


def get_rule_by_label(renderer: QgsRuleBasedRenderer, rule_label: str):
    for idx, rule in enumerate(renderer.rootRule().children()):
        if rule.label() == rule_label:
            return idx, rule
    raise Exception(f"Category renderer {rule_label} was not found.")


def get_range_by_label(renderer: QgsGraduatedSymbolRenderer, range_label: str):
    for idx, range_obj in enumerate(renderer.ranges()):
        if range_obj.label() == range_label:
            return idx, range_obj
    raise Exception(f"Category renderer {range_label} was not found.")


def get_renderer_updater(object_type, renderer):
    if object_type == 'category':
        return renderer.updateCategorySymbol
    if object_type == 'range':
        return renderer.updateRangeSymbol
    if object_type == 'rule':
        return renderer.updateRuleSymbol


def color_object(layer_name: str, renderer_name: str, color: [int, int, int],
                 object_type: Literal['rule', 'category', 'range']):
    layer = get_layer(layer_name)
    renderer = layer.renderer()

    mapped_method = {'rule': get_rule_by_label, 'category': get_category_by_label, 'range': get_range_by_label}
    idx, render_obj = mapped_method[object_type](renderer, renderer_name)

    symbol = render_obj.symbol().clone()
    symbol.setColor(QColor(*color))
    get_renderer_updater(object_type, renderer)(idx, symbol)
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
    iface.mapCanvas().refresh()


def convert_coordinate(lon: float, lat: float) -> QgsPointXY:
    canvas = iface.mapCanvas()
    canvas_crs = canvas.mapSettings().destinationCrs()
    wgs84_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    transform = QgsCoordinateTransform(wgs84_crs, canvas_crs, QgsProject.instance())
    point = QgsPointXY(lon, lat)
    return transform.transform(point)
