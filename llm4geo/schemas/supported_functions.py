from copy import deepcopy
import json

supported_functions = {
    "add_map_layer": {
        "title": "add_map_layer",
        "description": "Adds a raster layer to the map.  This method should be preferred if the user mentions needing a picture, background, raster data, or images.",
        "type": "object",
        "properties": {
            "uri": {
                "type": "string",
                "description": """A QGIS layer uri for example "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png""",
                "enum": [
                    "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    "type=xyz&url=https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
                    "type=xyz&url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/tile/{z}/{y}/{x}",
                    "type=xyz&url=https://carto.nationalmap.gov/arcgis/rest/services/structures/MapServer/tile/{z}/{y}/{x}",
                    "type=xyz&url=https://basemap.nationalmap.gov/arcgis/services/rest/USGSTopo/MapServer/tile/{z}/{y}/{x}",
                    "type=xyz&url=https://basemap.nationalmap.gov/arcgis/services/rest/USGSShadedReliefOnly/MapServer/tile/{z}/{y}/{x}"
                ]},
            "layer_name": {
                "type": "string",
                "description": "An arbitrary name of the layer based on the input or a unique value from the uri",
            },
            "provider": {
                "type": "string",
                "description": "The provider used to create the layer. ",
                "enum": ["wms"]
            }
        },
        "required": ["uri", "layer_name", "provider"],
    },
    "add_feature_layer": {
        "title": "add_feature_layer",
        "description": "Adds a feature (vector) layer to the map. This method should be preferred if the user mentions loading data, vectors, features, analysis, or query.",
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
                                         Rail 1M scale: url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/12
                                         Water Area - Large Scale: url=https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/9  
                                         Waterbody - Large Scale: url=https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/12""",
                "enum": [
                    "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/8",
                    "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/9",
                    "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/10",
                    "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/11",
                    "url=https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/12",
                    "url=https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/9",
                    "url=https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/12",
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
        "required": ["uri", "layer_name", "provider"],
    },
    "color_category": {
        "title": "color_category",
        "description": "Colors a layer renderer category using RGB values.  If the input matches a category this can be called like color_category(myLayer, myCategory, [0,0,0]) where myLayer will be the layer name that the catogory is in, myCategory will be the actual name of the category that the user wants to change and [0,0,0] is an RGB value representation of the color that the user wants.",
        "type": "object",
        "properties": {
            "layer_name": {
                "type": "string",
                "description": "The layer that the category belongs to.",
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
        "required": ["layer_name", "renderer_name", "color"],
    },
    "color_range": {
        "title": "color_range",
        "description": "Colors a layer renderer range using RGB values.  If the input matches a category this can be called like color_range(myLayer, myRange, [0,0,0]) where myLayer will be the layer name that the range is in, myRange will be the actual name of the category that the user wants to change and [0,0,0] is an RGB value representation of the color that the user wants.",
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
        "required": ["layer_name", "renderer_name", "color"],
    },
    "color_rule": {
        "title": "color_rule",
        "description": "Colors a layer renderer rule using RGB values.  If the input matches a category this can be called like color_rule(myLayer, myRule, [0,0,0]) where myLayer will be the layer name that the rule is in, myRule will be the actual name of the category that the user wants to change and [0,0,0] is an RGB value representation of the color that the user wants.",
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
        "required": ["layer_name", "renderer_name", "color"],
    },
    "remove_all_map_layers": {
        "title": "remove_all_map_layers",
        "description": "Removes all map layers.",
    },
    "go_to_location": {
        "title": "go_to_location",
        "description": "Used to navigate to a location.  If a user wants to 'navigate to', 'zoom to', 'go to', or 'locate' a city, this method can be used. It takes a four coordinate bounding box as a list [west,south,east,north] in degrees, for example if a user asks to go to paris that might result in the following call, `go_to_location(2.2242, 48.8151, 2.4699, 48.9021)`.  If only two points are available then add .05 to each number so that there are four numbers.  For example a bbox is not available and only a point is available for a location, such as -70, 40, then the call should be go_to_location(-70, 40, -69.95, 40.05).  You can get a geojson of the city and use the bounding box, or use the center point, and create a buffer around the location.",
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
    },
}

function_name_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "GetFunctionName",
    "description": """This is used for giving feedback to a user on calling a function to execute some procedure in QGIS. You should try to give helpful feedback as the chat output, as well as pick the best function to suite their needs.  Assume the user is new and go step by step. Don't describe the project unless the response uses it.""",
    "type": "object",
    "properties": {
        "chat": {"type": "string",
                 "description": "Provide brief feedback to the user on which function you think should be called and why.  For example if the user says, 'Load osm' then you might pick the load_map_data since osm is available as a data source for that function."},
        "function_name": {"type": "string",
                          "description": f"Choose a function name from one of the provided enumeration using this information {json.dumps(supported_functions)}. Note the available options for each of the functions and use that in consideration for the response.  For example if the user wants to load Road data, then add_feature_data would be the best response given that they want 'data' which most often means features or vector data, and there is a road layer available for that method.  Only use provided enums for function_name.  Don't make up new values for function_name.",
                          "enum": [function_name for function_name in supported_functions.keys()],
                          }
    },
    "required": ["chat", "function_name"]
}


def get_function_name_schema():
    return deepcopy(function_name_schema)


def get_supported_functions():
    return deepcopy(supported_functions)


def get_function_schema(function_name, project_description):

    return supported_functions[function_name]
