from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QDockWidget,
    QWidget
)
from PyQt5.QtCore import Qt, QSettings
from qgis.core import QgsMessageLog, Qgis
from qgis.gui import QgsMapCanvas

import json
import requests
from .project import get_project_json
from .actions import function_map, ChatResponse
from .utils import log_tag


class LLMWidget(QDockWidget):

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.canvas = QgsMapCanvas()
        self.settings = QSettings("jsvrcek", "qllm4geo")
        self.setMinimumSize(200, 150)
        self.chat_response = None

        # Load the saved API URL if it exists
        saved_url = self.settings.value("api_host", "")

        self.setWindowTitle("LLM4GEO")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.main_widget = QWidget()
        self.setWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self)

        self.url_label = QLabel("LLM API URL:")
        self.layout.addWidget(self.url_label)
        self.url_field = QLineEdit(self)
        self.layout.addWidget(self.url_field)
        self.url_field.setText(saved_url)

        self.chat_label = QLabel("Chat:")
        self.layout.addWidget(self.chat_label)
        self.input_field = QTextEdit(self)
        self.layout.addWidget(self.input_field)

        self.url_label = QLabel("Response:")
        self.layout.addWidget(self.url_label)
        self.response_field = QTextEdit(self)
        self.response_field.setReadOnly(True)
        self.layout.addWidget(self.response_field)

        self.submit_button = QPushButton("Submit", self)
        self.layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(lambda: self.handle_submit(self.input_field.toPlainText()) and self.input_field.clear())

        self.apply_button = QPushButton("Apply", self)
        self.layout.addWidget(self.apply_button)
        self.apply_button.clicked.connect(self.handle_apply)
        self.apply_button.setEnabled(False)
        self.chat_history = []

    def closeEvent(self, event):
        super().closeEvent(event)

    def make_api_call(self):
        api_host = self.url_field.text().rstrip('/')
        self.settings.setValue("api_host", api_host)

        api_url = f"{api_host}/api/chat/qgis"
        input_text = self.input_field.text()
        request = {"text_input": input_text}
        try:
            response = requests.post(api_url, request)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "API Error", f"An error occurred: {e}")

    def get_api_url(self):
        api_host = self.url_field.text().rstrip('/')
        self.settings.setValue("api_host", api_host)
        return f"{api_host}/api/chat/qgis"

    def make_request(self, user_text, chat_history=None) -> ChatResponse:
        request = {"text_input": user_text, "project_description": get_project_json(), "chat_history": chat_history}

        try:
            response = requests.post(self.get_api_url(), json=request, timeout=30)
            response.raise_for_status()
            self.input_field.clear()
            return response.json()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "API Error", f"An error occurred: {e}")

    def handle_submit(self, input_text):
        if not input_text:
            return False
        self.response_field.append("\nUser:")
        self.chat_history.append(input_text)
        self.response_field.append(input_text)
        response = self.make_request(input_text, self.chat_history)

        if not response:
            QgsMessageLog.logMessage("Did not receive a response.", log_tag, level=Qgis.MessageLevel.Info)
            return False
        self.chat_response = response
        self.response_field.append("\nChatBot:")
        self.chat_history.append(response['chat'])

        # Trim chat history to avoid excessive amounts of context.
        # This could probably be parameterized and configurable by the user as an advanced setting.
        self.chat_history = self.chat_history[:8]

        self.response_field.append(response['chat'])
        self.apply_button.setEnabled(True)
        QgsMessageLog.logMessage(json.dumps(response), log_tag, level=Qgis.MessageLevel.Info)

        if "parameters" in response:
            self.response_field.append(f"\n I can do that using {response['function_name']}({response['parameters']})")
        else:
            self.response_field.append(f"I can do that now.")
        self.response_field.append(f"Click apply or submit a new chat.")
        return True

    def handle_apply(self):
        try:
            try:
                qgis_method = function_map[self.chat_response['function_name']]
                if qgis_method and self.chat_response['parameters']:
                    qgis_method(**self.chat_response['parameters'])
                else:
                    qgis_method()
            except Exception as e:
                self.handle_submit(f"There was an error with that last command: {e} is there a different command that can be tried?")
            try:
                self.canvas.refresh()
            except Exception as e:
                QgsMessageLog.critical(f"Layer failed to load: {e}!", log_tag, level=Qgis.MessageLevel.Critical)
        except KeyError:
            QMessageBox.critical(self, "API Error",
                                 f"Could not process chat response: {self.chat_response}, please see the logs for more information.")
        except Exception as e:
            QMessageBox.critical(self, "QGIS Error", f"Something bad happened: {e}.")
