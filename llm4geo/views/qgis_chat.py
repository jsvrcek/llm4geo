import json

from django.conf import settings
from django.http import JsonResponse
from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from llm4geo.serializers import TextInputSerializer

supported_functions = {"add_map_layer": """Adds a map layer using QgsProject.instance().addMapLayer() the parameters to this method are the required parameters for qgis.core.QgsRasterLayer(),
                                        for example the parameters for loading an osm layer using QgsRasterLayer would be, ["type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png", "OpenStreetMap", "wms"], therefore the desired response for loading an OSM layer would be:
                                        {"chat": "Loading an OpenStreetMap layer.", "mapped_function": {"function_name": "add_map_layer", "parameters": ["type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png", "USGSImageryOnly", "wms"]}}. If the user wants some other layer you would need to use the parameters from some wms layer from USGS or available on data.gov that might meet their requirement, . 
                                        Here is a list of available urls: 
                                        type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png
                                        type=xyz&url=https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}
                                        type=xyz&url=https://carto.nationalmap.gov/arcgis/services/transportation/MapServer/tile/{z}/{y}/{x}
                                        type=xyz&url=https://carto.nationalmap.gov/arcgis/services/structures/MapServer/tile/{z}/{y}/{x}
                                        type=xyz&url=https://basemap.nationalmap.gov/arcgis/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}
                                        type=xyz&url=https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/tile/{z}/{y}/{x}
                                        type=xyz&url=https://basemap.nationalmap.gov/arcgis/services/USGSShadedReliefOnly/MapServer/tile/{z}/{y}/{x}
                                        """,
                     "remove_all_map_layers":  "Removes all map layers using QgsProject.instance().removeAllMapLayers() it takes no parameters."}

class QGISChatView(APIView):

    system = f"You are trying to help the user do some action or series of actions."
    prompt = ChatPromptTemplate.from_messages([SystemMessage(content="hello"), ("human", "{input}")])

    json_schema = {
        "title": "QGISFunction",
        "description": "This schema defines the structure for a qgis function call.",
        "type": "object",
        "properties": {
            "chat": {"type": "string",
                     "description": "The chat response describing which qgis methods would normally be called are being called and why.  Explain to the user where they might find documentation to help them do that. This chat should end in asking if the user wants to perform the function with the layers.  For example if the function being called is add_map_layer, a good example of a return value here would be. 'It seems like you want to load a map layer which can normally be done via the Open Layer Source Manager (ctrl+L) or by using the pyqgis method addMapLayer(). This response would change based on the method you are recommending and whatever information you have about the qgis application."},
            "mapped_function": {
                "type": "object",
                "properties": {
                    "function_name": {"type": "string",
                                      "enum": list(supported_functions.keys())},
                    "parameters": {
                        "type": "array",
                        "items": {"type": "string",
                                  "description": f"The parameters that would be used to call the related function.  Here is a JSON where the key is an available function name and the corresponding value is a description of what kind of parameters should be used. {json.dumps(supported_functions)}"}
                    }
                },
                "required": ["function_name", "parameters"]
            }
        },
        "required": ["chat", "function"]
    }

    def get_response(self, text):
        model = settings.LLM_MODEL(model=settings.OPENAI_MODEL, openai_api_key=settings.OPENAI_API_KEY)
        structured_llm = model.with_structured_output(self.json_schema)
        structured_llm_with_prompt = self.prompt | structured_llm
        with get_openai_callback() as cb:
            response = structured_llm_with_prompt.invoke(text)
            print(response)
            print(cb)
        # TODO: Create a model constructor
        return response

    def post(self, request):
        print(request.data)
        serializer = TextInputSerializer(data=request.data)
        if serializer.is_valid():
            text_input = serializer.validated_data['text_input']
            return JsonResponse(self.get_response(text_input))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)