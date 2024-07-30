from django.urls import path
from llm4geo.views import ChatExportsView

urlpatterns = [
    path('api/chat/', ChatExportsView.as_view(), name='chat_api'),
]