from rest_framework import serializers


class TextInputSerializer(serializers.Serializer):
    text_input = serializers.CharField()


class QGISSerializer(serializers.Serializer):
    text_input = serializers.CharField()
    project_description = serializers.JSONField()
    chat_history = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True, default="")
    )
