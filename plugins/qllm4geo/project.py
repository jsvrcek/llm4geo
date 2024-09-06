from qgis.core import QgsProject


def get_project_json():
    project = QgsProject.instance()

    project_info = {'title': project.title(), 'crs': project.crs().authid()}

    layers = []
    for layer in project.mapLayers().values():
        layer_info = {
            'name': layer.name(),
            'id': layer.id(),
            'type': layer.type(),
            'crs': layer.crs().authid(),
            'extent': layer.extent().toString(),
            'feature_count': layer.featureCount() if hasattr(layer, 'featureCount') else None,
            'geometry_type': layer.geometryType() if hasattr(layer, 'geometryType') else None,
            'fields': [field.name() for field in layer.fields()] if hasattr(layer, 'fields') else [],
            'categories': [cat.label() for cat in layer.renderer().categories()] if hasattr(layer,
                                                                                          'renderer') and hasattr(
                layer.renderer(), 'categories') else [],
            'ranges': [range_obj.label() for range_obj in layer.renderer().ranges()] if hasattr(layer, 'renderer') and hasattr(
                layer.renderer(), 'ranges') else [],
            'rules': [rule.label() for rule in layer.renderer().rootRule().children()] if hasattr(layer, 'renderer') and hasattr(
                layer.renderer(), 'rootRule') else [],

        }
        layers.append(layer_info)

    project_info['layers'] = layers

    return project_info
