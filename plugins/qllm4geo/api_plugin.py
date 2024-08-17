from qgis.PyQt.QtCore import Qt, QSettings, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QMenu
from qgis.gui import QgisInterface
import os
from .api_input_dialog import ApiInputDialog

class ApiPlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr("&API Plugin")

    def tr(self, message):
        return QCoreApplication.translate('ApiPlugin', message)

    def initGui(self):
        icon_path = ':/plugins/api_plugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr("Open API Input Window"),
            callback=self.run,
            parent=self.iface.mainWindow())

    def add_action(
            self,
            icon_path,
            text,
            callback,
            parent=None):
        action = QAction(QIcon(icon_path), text, parent)
        action.triggered.connect(callback)
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&API Plugin"), action)

    def run(self):
        dialog = ApiInputDialog()
        dialog.exec_()