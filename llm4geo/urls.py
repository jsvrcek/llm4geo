from django.urls import path

from llm4geo.views.qgis_chat import QGISChatView
from llm4geo.views.data_chat import DataChatView

urlpatterns = [
    path("api/chat/data", DataChatView.as_view(), name="data_chat_api"),
    path("api/chat/qgis", QGISChatView.as_view(), name="qgis_chat_api"),
]
