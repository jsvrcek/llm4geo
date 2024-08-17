from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QSettings
import requests

class ApiInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QSettings("jsvrcek", "qllm4geo")

        # Other UI setup code...

        # Load the saved API URL if it exists
        saved_url = self.settings.value("api_host", "")
        self.input_field.setText(saved_url)

        self.setWindowTitle("LLM4GEO")
        self.setLayout(QVBoxLayout())

        # Add a label
        self.label = QLabel("CHAT:")
        self.layout().addWidget(self.label)

        self.url_field = QLineEdit(self)
        self.layout().addWidget(self.url_field)
        self.url_field.setText(saved_url)

        self.input_field = QLineEdit(self)
        self.layout().addWidget(self.input_field)

        # Add a submit button
        self.submit_button = QPushButton("Submit", self)
        self.layout().addWidget(self.submit_button)

        # Connect the button click event to a method
        self.submit_button.clicked.connect(self.make_api_call)

    def make_api_call(self):
        api_host = self.url_field.text()
        self.settings.setValue("api_host", api_host)
        
        api_url = f"{api_host}/api/chat"
        input_text = self.input_field.text()
        request = {"text_input": input_text}
        try:
            response = requests.post(api_url, request)
            response.raise_for_status()  # Raise an error for bad responses

            # Show the result in a message box
            QMessageBox.information(self, "API Response", f"API Response: {response.text}")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "API Error", f"An error occurred: {e}")
