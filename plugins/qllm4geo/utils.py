from qgis.PyQt.QtGui import QColor

from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsVectorLayer, QgsGraduatedSymbolRenderer, \
    QgsCategorizedSymbolRenderer, QgsRuleBasedRenderer, QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.utils import iface

from typing import Literal

log_tag = "LLM4GEO"


def add_layer(layer):
    if not layer.isValid():
        QgsMessageLog.logMessage("Layer failed to load!", log_tag, level=Qgis.Info)
    else:
        QgsProject.instance().addMapLayer(layer)
        QgsMessageLog.logMessage("Layer added successfully!", log_tag, level=Qgis.Info)


def get_layer(layer_name: str) -> QgsVectorLayer:
    return QgsProject.instance().mapLayersByName(layer_name)[0]


def get_category_by_label(renderer: QgsCategorizedSymbolRenderer, cat_label: str):
    for idx, cat in enumerate(renderer.categories()):
        if cat.label() == cat_label:
            return idx, cat


def get_rule_by_label(renderer: QgsRuleBasedRenderer, rule_label: str):
    for idx, rule in enumerate(renderer.rootRule().children()):
        if rule.label() == rule_label:
            return idx, rule


def get_range_by_label(renderer: QgsGraduatedSymbolRenderer, range_label: str):
    for idx, range_obj in enumerate(renderer.ranges()):
        if range_obj.label() == range_label:
            return idx, range_obj


def color_object(layer_name: str, renderer_name: str, color: [int, int, int],
                 object_type: Literal['rule', 'category', 'range']):
    layer = get_layer(layer_name)
    renderer = layer.renderer()
    mapped_method = {'rule': get_rule_by_label, 'category': get_category_by_label, 'range': get_range_by_label}
    idx, render_obj = mapped_method[object_type](renderer, renderer_name)
    symbol = render_obj.symbol()
    symbol.setColor(QColor(*color))

    def get_updater():
        if object_type == 'category':
            return renderer.updateCategorySymbol
        if object_type == 'range':
            return renderer.updateRangeSymbol
        if object_type == 'rule':
            return renderer.updateRuleSymbol

    get_updater()(idx, symbol)
    # layer.triggerRepaint()
    # iface.layerTreeView().refreshLayerSymbology(layer.id())

def convert_coordinate(lon: float, lat: float) -> QgsPointXY:
    canvas = iface.mapCanvas()
    canvas_crs = canvas.mapSettings().destinationCrs()
    wgs84_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    transform = QgsCoordinateTransform(wgs84_crs, canvas_crs, QgsProject.instance())
    point = QgsPointXY(lon, lat)
    return transform.transform(point)