import json

from django.conf import settings
from django.http import JsonResponse
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from llm4geo.serializers import QGISSerializer

supported_functions = {"add_map_layer": {
    "description": "Adds a raster layer to the map.  This method should be preferred if the user mentions needing a picture, background, raster data, or images.",
    "properties": {
        "function_name": {"const": "add_map_layer"},
        "parameters": {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": """A QGIS layer uri for example "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png" """,
                    "enum": [
                        "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                        "type=xyz&url=https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
                        "type=xyz&url=https://carto.nationalmap.gov/arcgis/services/transportation/MapServer/tile/{z}/{y}/{x}",
                        "type=xyz&url=https://carto.nationalmap.gov/arcgis/services/structures/MapServer/tile/{z}/{y}/{x}",
                        "type=xyz&url=https://basemap.nationalmap.gov/arcgis/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
                        "type=xyz&url=https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
                        "type=xyz&url=https://basemap.nationalmap.gov/arcgis/services/USGSShadedReliefOnly/MapServer/tile/{z}/{y}/{x}"
                    ]},
                "layer_name": {
                    "type": "string",
                    "description": "An arbitrary name of the layer based on the input or a unique value from the uri",
                },
                "provider": {
                    "type": "string",
                    "description": "The provider used to create the layer. ",
                    "enum": ["wms"]
                    # "arcgisrest",
                    #      "db2",
                    #      "delimitedtext",
                    #      "geonode",
                    #      "gpx",
                    #      "grass",
                    #      "mdal",
                    #      "mssql",
                    #      "oracle",
                    #      "ows",
                    #      "pdal",
                    #      "postgres",
                    #      "spatialite",
                    #      "virtual",
                    #      "wcs",
                    #      "wfs",
                    #      "wms"]
                }
            },
            "required": ["uri", "name", "provider"],
        }
    }
},
    "add_feature_layer": {
        "description": "Adds a feature (or vector) layer to the map. This method should be preferred if the user mentions loading data, vectors, features, analysis, or query.",
        "properties": {
            "function_name": {"const": "add_feature_layer"},
            "parameters": {
                "type": "object",
                "properties": {
                    "uri": {
                        "type": "string",
                        "description": """A QGIS layer uri for example "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png".  
                                    Available URIs are:
                                      Roads 10M scale: url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/8
                                         Roads 1M scale: url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/9
                                         Ferries 1M scale: url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/10
                                         National Trails: url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/11
                                         Rail 1M scale: url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/12""",
                        "enum": [
                            "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/8",
                            "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/9",
                            "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/10",
                            "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/11",
                            "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/12",
                        ]
                    },
                    "layer_name": {
                        "type": "string",
                        "description": "An arbitrary name of the layer based on the input or a unique value from the uri",
                    },
                    "provider": {
                        "type": "string",
                        "description": "The provider used to create the layer.",
                        "enum": ["arcgisfeatureserver"]
                    }
                },
                "required": ["uri", "name", "provider"],

            }
        }
    },
    "color_category": {
        "description": "Colors a layer renderer category using RGB values.  If the input matches a category this can be called like color_category(myLayer, myCategory, [0,0,0]) where myLayer will be the layer name that the catogory is in, myCategory will be the actual name of the category that the user wants to change and [0,0,0] is an RGB value representation of the color that the user wants.",
        "properties": {
            "function_name": {"const": "color_category"},
            "parameters": {
                "type": "object",
                "properties": {
                    "layer_name": {
                        "type": "string",
                        "description": "THe layer that the category belongs to.",
                    },
                    "renderer_name": {
                        "type": "string",
                        "description": "The category to select.  This is the specific thing that the user wants to change the color of.",
                    },
                    "color": {
                        "description": "The RGB value to use as an array for example [255,255,255].",
                        "type": "array",
                        "items": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 255
                        },
                        "minItems": 3,
                        "maxItems": 3
                    }
                },
                "required": ["layer", "category", "rgb"],
            }
        }
    },
    "color_range": {
        "description": "Colors a layer renderer range using RGB values.  If the input matches a category this can be called like color_range(myLayer, myRange, [0,0,0]) where myLayer will be the layer name that the range is in, myRange will be the actual name of the category that the user wants to change and [0,0,0] is an RGB value representation of the color that the user wants.",
        "properties": {
            "function_name": {"const": "color_range"},
            "parameters": {
                "type": "object",
                "properties": {
                    "layer_name": {
                        "type": "string",
                        "description": "THe layer that the category belongs to.",
                    },
                    "renderer_name": {
                        "type": "string",
                        "description": "The range to select.  This is the specific thing that the user wants to change the color of.",
                    },
                    "color": {
                        "description": "The RGB value to use as an array for example [255,255,255].",
                        "type": "array",
                        "items": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 255
                        },
                        "minItems": 3,
                        "maxItems": 3
                    }
                },
                "required": ["layer", "range", "rgb"],
            }
        }
    },
    "color_rule": {
        "description": "Colors a layer renderer rule using RGB values.  If the input matches a category this can be called like color_rule(myLayer, myRule, [0,0,0]) where myLayer will be the layer name that the rule is in, myRule will be the actual name of the category that the user wants to change and [0,0,0] is an RGB value representation of the color that the user wants.",
        "properties": {
            "function_name": {"const": "color_rule"},
            "parameters": {
                "type": "object",
                "properties": {
                    "layer_name": {
                        "type": "string",
                        "description": "THe layer that the category belongs to.",
                    },
                    "renderer_name": {
                        "type": "string",
                        "description": "The rule to select.  This is the specific thing that the user wants to change the color of.",
                    },
                    "color": {
                        "description": "The RGB value to use as an array for example [255,255,255].",
                        "type": "array",
                        "items": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 255
                        },
                        "minItems": 3,
                        "maxItems": 3
                    }
                },
                "required": ["layer", "rule", "rgb"],
            }
        }
    },
    "remove_all_map_layers": {
        "description": "Removes all map layers.",
        "properties": {
            "function_name": {"const": "remove_all_map_layers"},
        }
    },
    "go_to_location": {
        "description": "Used to navigate to a location.  If a user wants to 'navigate to', 'zoom to', 'go to', or 'locate' a city, this method can be used. It takes a four coordinate bounding box as a list [west,south,east,north] in degrees, for example if a user asks to go to paris that might result in the following call, `go_to_location(2.2242, 48.8151, 2.4699, 48.9021)`.  If only two points are available then add .05 to each number so that there are four numbers.  For example a bbox is not available and only a point is available for a location, such as -70, 40, then the call should be go_to_location(-70, 40, -69.95, 40.05).  You can get a geojson of the city and use the bounding box, or use the center point, and create a buffer around the location.",
        "properties": {
            "function_name": {"const": "go_to_location"},
            "parameters": {
                "type": "object",
                "properties": {
                    "west": {
                        "type": "number",
                        "description": "The west longitude of the location.",
                    },
                    "south": {
                        "type": "number",
                        "description": "The south latitude of the location.",
                    },
                    "east": {
                        "type": "number",
                        "description": "The east longitude of the location.",
                    },
                    "north": {
                        "type": "number",
                        "description": "The north latitude of the location.",
                    },
                },
                "required": ["west", "south", "east", "north"],
            }
        }
    },
}

def get_qgis_project_description():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the QGIS project."
            },
            "crs": {
                "type": "string",
                "description": "The Coordinate Reference System (CRS) of the QGIS project, represented by its EPSG code (e.g., 'EPSG:4326')."
            },
            "layers": {
                "type": "array",
                "description": "An array of layers in the QGIS project.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the layer."
                        },
                        "id": {
                            "type": "string",
                            "description": "The unique ID of the layer."
                        },
                        "type": {
                            "type": "integer",
                            "description": "The type of the layer (e.g., 0 for vector, 1 for raster)."
                        },
                        "crs": {
                            "type": "string",
                            "description": "The Coordinate Reference System (CRS) of the layer, represented by its EPSG code."
                        },
                        "extent": {
                            "type": "string",
                            "description": "The spatial extent of the layer, represented as a string."
                        },
                        "feature_count": {
                            "type": "integer",
                            "description": "The number of features (e.g., points, lines, polygons) in the layer."
                        },
                        "geometry_type": {
                            "type": "integer",
                            "description": "The geometry type of the layer (e.g., 0 for point, 1 for line, 2 for polygon)."
                        },
                        "fields": {
                            "type": "array",
                            "description": "An array of field names present in the layer.",
                            "items": {
                                "type": "string",
                                "description": "The name of a field in the layer."
                            }
                        }
                    },
                    "required": ["name", "id", "type", "crs", "extent", "feature_count", "geometry_type", "fields"]
                }
            }
        },
        "required": ["title", "file_path", "crs", "layers"]
    }


class QGISChatView(APIView):
    system = f"You are trying to help the user do some action or series of actions."
    prompt = ChatPromptTemplate.from_messages([SystemMessage(content="hello"), ("human", "{input}")])

    json_schema = {
        "title": "QGISFunction",
        "description": """This is used for giving feedback to a user on calling a function to execute some procedure in QGIS. You should try to give helpful feedback as the chat output, as well as pick the best function to suite their needs.  Assume the user is new and go step by step. Here is an example if a user says, 'load some openstreetmap data' you would return a response like this... Don't describe the project unless the response uses it.""",
        "type": "object",
        "properties": {
            "chat": {"type": "string",
                     "description": "The chat response describing which qgis methods would normally be called are being called and why.  Explain to the user where they might find documentation to help them do that. This chat should end in asking if the user wants to perform the function with the layers.  For example if the function being called is add_map_layer, a good example of a return value here would be. 'It seems like you want to load a map layer which can normally be done via the Open Layer Source Manager (ctrl+L) or by using the pyqgis method addMapLayer(). This response would change based on the method you are recommending and whatever information you have about the qgis application.  You don't have to use this exact text, try to respond meaningfully to the users prompt."},
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
                "dependentSchemas": supported_functions,
                "required": ["function_name", "parameters"]
            }
        },
        "required": ["chat", "function"]
    }

    def get_response(self, text, project_description):
        augmented_text = f"{text} and the users current project uses a schema of: \n\n {get_qgis_project_description()} and the users project specifically uses: \n\n {project_description} using use that description to help"
        model = settings.LLM_MODEL(model=settings.OPENAI_MODEL, openai_api_key=settings.OPENAI_API_KEY)
        structured_llm = model.with_structured_output(self.json_schema)
        structured_llm_with_prompt = self.prompt | structured_llm
        response = structured_llm_with_prompt.invoke({"input": augmented_text})
        # TODO: Create a model constructor
        return response

    def post(self, request):
        print(f"Received request: {request.data}")
        serializer = QGISSerializer(data=request.data)
        if serializer.is_valid():
            text_input = serializer.validated_data['text_input']
            project_description = serializer.validated_data['project_description']
            return JsonResponse(self.get_response(text_input, project_description))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
