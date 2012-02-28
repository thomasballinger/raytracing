"""Vector math functions required for ray caster

point representation: numpy.array([0,1,2])
ray representation: [numpy.array([0,1,2]), numpy.array([2,3,4])]
"""
import numpy

def get_line_intersections_with_sphere(line, center, radius):
    """Returns a list of intersection points

    >>> get_line_intersections_with_sphere([[0.,1,-2], [0,1,2]], [0.,0,0], 1.0)
    [(0.0, 1.0, 0.0)]
    >>> get_line_intersections_with_sphere([[0.,0,3],[0,0,2]], [0., 0, 0], 1)
    [(0.0, 0.0, -1.0), (0.0, 0.0, 1.0)]
    """
    v1, v2 = line
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    x3, y3, z3 = center
    r = radius

    a = (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2
    b = 2*((x2 - x1)*(x1 - x3) + (y2 - y1)*(y1 - y3) + (z2 - z1)*(z1 - z3) )
    c = x3**2 + y3**2 + z3**2 + x1**2 + y1**2 + z1**2 - 2*(x3*x1 + y3*y1 + z3*z1) - r**2
    radicand = b**2 - 4*a*c

    def xyz_from_u(u):
        return (x1 + u * (x2 - x1), y1 + u * (y2 - y1), z1 + u * (z2 - z1))

    if radicand < 0:
        return []
    elif radicand == 0:
        return [xyz_from_u(u) for u in [-b / (2*a)]]
    elif radicand > 0:
        return [xyz_from_u(u) for u in [(-b + numpy.sqrt(radicand)) / (2*a), (-b - numpy.sqrt(radicand)) / (2*a)]]
    else:
        raise Exception("logic error!")

def get_position_from_plane_and_distance(width_ray, height_ray, distance):
    """
    Finds a positions "distance" back along the line perpendicular to both rays
    >>> tuple(get_position_from_plane_and_distance(((0,-1,-1), (0,-1,1)), ((0,-1,-1), (0,1,-1)), 10))
    (-10.0, -1.0, -1.0)
    >>> tuple(get_position_from_plane_and_distance(((-1,-1,0), (1,-1,0)), ((-1,-1,0), (-1,1,0)), 10))
    (-1.0, -1.0, 10.0)

    """
    width_v = get_v_from_ray(width_ray)
    height_v = get_v_from_ray(height_ray)
    c = numpy.cross(width_v, height_v);
    normalized_cross = c / numpy.linalg.norm(c)
    correct_distance_cross =  normalized_cross * distance
    origin = width_ray[0]
    position = origin + correct_distance_cross
    return position

def get_v_from_ray(ray):
    v = numpy.array(ray[1]) - numpy.array(ray[0])
    return v

def get_distance(point1, point2):
    """Returns the distance
    >>> get_distance((0,0,1), (-1,0,0))
    1.4142...
    """
    return numpy.sqrt(numpy.abs(numpy.sum(numpy.array(point1) - numpy.array(point2))))

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
