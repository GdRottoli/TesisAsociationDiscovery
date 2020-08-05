from shapely.geometry import Polygon, Point, LineString
import math


def __distance__(geo1, geo2):
    return geo1.distance(geo2)


def __north__(point1, point2):
    if __distance__(point1, point2) < 500:
        if point1.y > point2.y:
            if point1.x == point2.x:
                return 1
            else:
                return abs(
                    2/math.pi* math.atan(
                        abs(
                            (point1.y - point2.y) /
                            (point1.x - point2.x))
                    )
                )
        else:
            return 0
    else:
        return 0


def __south__(point1, point2):
    if __distance__(point1, point2) < 500:
        if point1.y < point2.y:
            if point1.x == point2.x:
                return 1
            else:
                return abs(
                    2/math.pi* math.atan(
                        abs(
                            (point1.y - point2.y) /
                            (point1.x - point2.x))
                    )
                )
        else:
            return 0
    else:
        return 0


def __east__(point1, point2):
    if __distance__(point1, point2) < 500:
        if point1.x > point2.x:
            if point1.y == point2.y:
                return 1
            else:
                return abs(
                    2/math.pi* math.atan(
                        abs(
                            (point1.x - point2.x)) /
                            (point1.y - point2.y)
                    )
                )
        else:
            return 0
    else:
        return 0


def __west__(point1, point2):
    if __distance__(point1, point2) < 400:
        if point1.x < point2.x:
            if point1.y == point2.y:
                return 1
            else:
                return abs(
                    2 / math.pi * math.atan(
                        abs(
                        (point1.x - point2.x)) /
                        (point1.y - point2.y)
                    )
                )
        else:
            return 0
    else:
        return 0


def directions_polygon(point, polygon):
    centroid = polygon.centroid
    return {"north": __north__(point, centroid),
            "south": __south__(point, centroid),
            "east": __east__(point, centroid),
            "west": __west__(point, centroid)}


def directions_points(point1, point2):
    return {"north": __north__(point1, point2),
            "south": __south__(point1, point2),
            "east": __east__(point1, point2),
            "west": __west__(point1, point2)}


def neighbor(geometry1, geometry2, limit1 = 50, limit2 = 50, exp = 1.0):
    d = __distance__(geometry1, geometry2)
    return 1 if d <= limit1 else (-(d - limit1)/(limit2 - limit1) + 1)**exp if d <= limit2 else 0
