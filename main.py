import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
import pandas as pd
import numpy as np
import json
import relation as rel


class Vertex(object):
    def __init__(self, id, type):
        self.vertex = {"id": id,
                       "attributes": {'label': type},
                       "timestamp": "1"}


class Edge(object):
    def __init__(self, id, source, target, name):
        self.edge = {"id": id,
                     "source": source,
                     "target": target,
                     "directed": "false",
                     "attributes": {'label': name},
                     "timestamp": "1"}


def __add_vertex__(G, id, type):
    vertex = Vertex(id, type)
    G.append(vertex)
    return G


def __add_edge__(G, source, target, label, mu):
    id = '{}-{}-{}-(mu:{})'.format(source, label, target, mu)
    edge = Edge(id, source, target, label)
    G.append(edge)
    return G


def __add_new_point__(graph, new_point, point_vertex_id):
    if new_point.id not in added_points:
        graph = __add_vertex__(graph, point_vertex_id, new_point.amenity)
        added_points.append(new_point.id)
    return graph


def __add_new_street__(graph, new_street, street_vertex_id):
    if new_street.id not in added_street:
        graph = __add_vertex__(graph, street_vertex_id, new_street.Name)
        added_street.append(new_street.id)
    return graph


def __add_new_green__(graph, green_id, label, green_vertex_id):
    if green_id not in added_green:
        graph = __add_vertex__(graph, green_vertex_id, label)
        added_green.append(green_id)
    return graph


def __get_directional_relations_from_point_to_polygons__(graph, point, polygons, min_mu=0.0, point_string='point{}',
                                                         polygon_string='polygon{}'):
    result = map(lambda x: rel.directions_polygon(point.geometry, x), polygons.geometry)
    point_vertex_id = point_string.format(point.id)
    for polygon_index, relations_dict in enumerate(list(result)):
        for direction in relations_dict:
            if relations_dict[direction] > min_mu:
                polygon_vertex_id = polygon_string.format(polygon_index)
                graph = __add_new_point__(graph, point, point_vertex_id)
                graph = __add_new_green__(graph, polygon_index, polygons.name[polygon_index], polygon_vertex_id)
                graph = __add_edge__(graph, point_vertex_id, polygon_vertex_id, direction, relations_dict[direction])
    return graph


def __get_neighbor_relations_from_point_to_lines__(graph, point, lines, lowest_distance=50, greatest_distance=80,
                                                   min_mu=0.0, point_string='point{}', line_string='line{}',
                                                   relation_name='neighbor'):
    point_vertex_id = point_string.format(point.id)
    for line_index, line in lines.iterrows():
        mu = rel.neighbor(point.geometry, line.geometry, lowest_distance, greatest_distance)
        if mu > min_mu:
            line_vertex_id = line_string.format(line.id)
            graph = __add_new_point__(graph, point, point_vertex_id)
            graph = __add_new_street__(graph, line, line_vertex_id)
            graph = __add_edge__(graph, point_vertex_id, line_vertex_id, relation_name, mu)
    return graph


def __get_neighbor_relations_from_point_to_points__(graph, point, points, lowest_distance=50, greatest_distance=80,
                                                   min_mu=0.0, point_string='point{}', second_point_string='point{}',
                                                    relation_name='neighbor'):
    point_vertex_id = point_string.format(point.id)
    for list_point_index, second_point in points.iterrows():
        if second_point.id != point.id:
            mu = rel.neighbor(point.geometry, second_point.geometry, lowest_distance, greatest_distance)
            if mu > min_mu:
                second_point_vertex_id = second_point_string.format(second_point.id)
                graph = __add_new_point__(graph, point, point_vertex_id)
                graph = __add_new_point__(graph, second_point, second_point_vertex_id)
                graph = __add_edge__(graph, point_vertex_id, second_point_vertex_id, relation_name, mu)
    return graph


def __get_directional_relations_from_point_to_points__(graph, point, points, lowest_distance=50, greatest_distance=80,
                                                   min_mu=0.0, point_string='point{}', second_point_string='point{}'):
    point_vertex_id = point_string.format(point.id)
    for list_point_index, second_point in points.iterrows():
        if second_point.id != point.id:
            relations_dict = rel.directions_points(point.geometry, second_point.geometry)
            for direction in relations_dict:
                if relations_dict[direction] > min_mu:
                    second_point_vertex_id = second_point_string.format(second_point.id)
                    graph = __add_new_point__(graph, point, point_vertex_id)
                    graph = __add_new_point__(graph, second_point, second_point_vertex_id)
                    graph = __add_edge__(graph, point_vertex_id, second_point_vertex_id, direction, relations_dict[direction])
    return graph

def execute():
    # Read files
    # Spatial points file
    poi = gpd.read_file('data/locales_cdelu.shp').reset_index()
    # poi = gpd.read_file('data/centro_cdelu.shp').reset_index()
    poi['amenity'] = poi['amenity'].str.lower()
    print(poi.groupby('amenity').size())
    poi["id"] = poi.index
    streets = gpd.read_file('data/calles_principales.shp').reset_index()
    streets["id"] = streets.index
    streets["Name"] = streets['Name'].str.lower()
    print(streets.groupby('Name').size())
    greens = gpd.read_file('data/areas_verdes.shp').reset_index()
    greens["id"] = greens.index
    greens["name"] = greens['name'].str.lower()
    print(greens.groupby('name').size())
    schools = poi.loc[poi['amenity'] == 'school', :]
    G = []
    for point_row_id, point in poi.iterrows():
        # Calculate directional relationships between points and areas
        G = __get_directional_relations_from_point_to_polygons__(G, point, greens, min_mu=0.45, polygon_string='GreenArea{}')
        G = __get_neighbor_relations_from_point_to_lines__(G, point, streets, lowest_distance=30, greatest_distance=80, min_mu=0.0, line_string='street{}')
        G = __get_neighbor_relations_from_point_to_points__(G, point, schools, min_mu=0.00, relation_name='neighbor_2_school')
        G = __get_directional_relations_from_point_to_points__(G, point, schools, min_mu=0.45)

    with open('data/graph_20200805.json', 'w', encoding='utf-8') as f:
        json_string = json.dumps([ob.__dict__ for ob in G], indent=4)
        f.write(json_string)

added_green = []
added_street = []
added_points = []

execute()

