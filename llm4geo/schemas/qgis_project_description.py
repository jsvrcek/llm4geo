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
                        },
                        "categories": {
                            "type": "array",
                            "description": "An array of renderer categories present in the layer.",
                            "items": {
                                "type": "string",
                                "description": "The name of a renderer categories in the layer."
                            }
                        },
                        "ranges": {
                            "type": "array",
                            "description": "An array of renderer ranges present in the layer.",
                            "items": {
                                "type": "string",
                                "description": "The name of a renderer ranges in the layer."
                            }
                        },
                        "rules": {
                            "type": "array",
                            "description": "An array of renderer rules present in the layer.",
                            "items": {
                                "type": "string",
                                "description": "The name of a renderer rules in the layer."
                            }
                        }
                    },
                    "required": ["name", "id", "type", "crs", "extent", "feature_count", "geometry_type", "fields", "categories", "ranges", "rules"]
                }
            }
        },
        "required": ["title", "file_path", "crs", "layers"]
    }
