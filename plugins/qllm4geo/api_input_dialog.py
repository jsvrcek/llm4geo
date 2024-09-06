from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QSettings
from qgis.core import QgsMessageLog, Qgis
from qgis.gui import QgsMapCanvas

import requests
from .actions import function_map, ChatResponse, log_tag


class ApiInputDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = QgsMapCanvas(parent)
        self.settings = QSettings("jsvrcek", "qllm4geo")

        self.chat_response = None
        # Load the saved API URL if it exists
        saved_url = self.settings.value("api_host", "")

        self.setWindowTitle("LLM4GEO")
        self.setLayout(QVBoxLayout())

        self.url_label = QLabel("LLM API URL:")
        self.layout().addWidget(self.url_label)
        self.url_field = QLineEdit(self)
        self.layout().addWidget(self.url_field)
        self.url_field.setText(saved_url)


        self.chat_label = QLabel("Chat:")
        self.layout().addWidget(self.chat_label)
        self.input_field = QTextEdit(self)
        self.layout().addWidget(self.input_field)

        self.url_label = QLabel("Response:")
        self.layout().addWidget(self.url_label)
        self.response_field = QTextEdit(self)
        self.response_field.setReadOnly(True)
        self.layout().addWidget(self.response_field)

        self.submit_button = QPushButton("Submit", self)
        self.layout().addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.handle_submit)

        self.apply_button = QPushButton("Apply", self)
        self.layout().addWidget(self.apply_button)
        self.apply_button.clicked.connect(self.handle_apply)
        self.apply_button.setEnabled(False)

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

    def make_request(self, input_text) -> ChatResponse:
        request = {"text_input": input_text}
        try:
            self.input_field.clear()
            response = requests.post(self.get_api_url(), request)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "API Error", f"An error occurred: {e}")

    def handle_submit(self):
        self.response_field.append("\nYou:")
        self.response_field.append(self.input_field.toPlainText())
        response = self.make_request(self.input_field.toPlainText())
        self.input_field.clear()
        if not response:
            return
        self.chat_response = response
        self.response_field.append("\nChatBot:")
        self.response_field.append(response['chat'])
        self.submit_button.setText('Retry')
        self.apply_button.setEnabled(True)
        if response['mapped_function']['parameters']:
            self.response_field.append(f"\n I can do that using {response['mapped_function']}({response['mapped_function']['parameters']})")
        else:
            self.response_field.append(f"I can do that now.")
        self.response_field.append(f"Click apply or retry.")

    def handle_apply(self):
        try:
            qgis_method = function_map[self.chat_response['mapped_function']['function_name']]
            if qgis_method and self.chat_response['mapped_function']['parameters']:
                qgis_method(self.chat_response['mapped_function']['parameters'])
            else:
                qgis_method()
            try:
                self.canvas.refresh()
            except:
                QgsMessageLog.logMessage("Layer failed to load!", log_tag, level=Qgis.Error)
        except KeyError:
            QMessageBox.critical(self, "API Error", f"Could not process chat response: {self.chat_response}")
