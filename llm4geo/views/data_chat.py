from django.conf import settings
from django.http import JsonResponse
from langchain_community.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from llm4geo.serializers import TextInputSerializer


class DataChatView(APIView):
    system = """You are trying to help people get data.  Geospatial data comes from a variety of sources including the USGS and OpenStreetMap.  Users will want these datasets in formats which can be used in their preferred geospatial client.
    Datasource needs to be one of "usgs-transportation", "usgs-water", "osm", "landsat", "usgs-imagery", "usgs-elevation" and file format can be one or more options.  File formats should only be recommended for data types they support.  If a user wants feature data such as roads, buildings or any descriptive geographical information then a format that supports feature data should be recommended such as gpkg or shapefile, whichever supports their desired use case the best.  If the user isn't sure which format makes sense for feature data, then geopackage is typically a good recommendation.  If the user wants imagery data (or other kinds of raster data) then they likely want landsat data.  Geotiff (gtiff) or geopackage (gpkg) would be good choices for that data type. KML is a file format that supports embedded styles and works with Google Earth and ATAK.  Elevation data is only supported by gtiff.

    Here are some examples.

    Example User: I need data for Africa. 
    Example Response: {{"dataSource": "osm", "fileFormat": ["gpkg"]}}

    Example User: My job involves the US. 
    Example Response: {{"dataSource": "usgs-transportation", "fileFormat": ["ESRI Shapefile"]}}

    Example User: I need a imagery that will work within ArcGIS.
    Example Response: {{"dataSource": "landsat", "fileFormat": ["gtiff"]}}
    
    Example User: I need rivers in the US that will open in QGIS.
    Example Response: {{"dataSource": "usgs-water", "fileFormat": ["gpkg"]}}
    """

    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")])

    json_schema = {
        "title": "export",
        "description": "A list of file formats and data sources reco",
        "type": "object",
        "properties": {
            "dataSource": {
                "type": "string",
                "enum": ["usgs-transportation", "osm", "landsat", "usgs-water", "usgs-imagery", "usgs-elevation"],
                "description": """Data source can be one of the following:
                                - usgs-transportation: A feature service with roads for the united states
                                - osm: OpenStreetMap has feature data for the entire world, including buildings and transportation routes
                                - landsat: Landsat features global imagery that has four bands, blue, green, red, and near infrared. This is useful for things like measuring vegetation changes with NDVI or water changes with NDWI
                                - usgs-water: Water feature data that is only available in the US. 
                                - usgs-imagery: High quality imagery that is only available in the US
                                - usgs-elevation: High quality elevation data that is only available in the US
                                """
            },
            "fileFormat": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["gpkg", "Esri Shapefile", "gtiff", "kml"]
                },
                "minItems": 1
            }
        },
        "required": ["dataSource", "fileFormat"],
        "additionalProperties": False
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