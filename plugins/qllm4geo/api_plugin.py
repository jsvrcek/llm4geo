from qgis.PyQt.QtCore import Qt, QSettings, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.gui import QgisInterface
import os
from .api_input_widget import LLMWidget


class ApiPlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr("&LLM4Geo")

    def tr(self, message):
        return QCoreApplication.translate("ApiPlugin", message)

    def initGui(self):
        self.dock_widget = LLMWidget(self.iface)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        self.dock_widget.show()

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&LLM4Geo"), action)
