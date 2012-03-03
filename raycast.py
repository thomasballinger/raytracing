"""Renders 3d scences by raytracing"""
import vectormath
import sys
import numpy
from PIL import Image
import random

# EVIL global variables for debugging
bounces = []
BOUNCELIMIT = 15

class Solid(object):
    """Represents an object in a 3d world which can interact with light"""
    def get_intersections(self, ray):
        raise NotImplementedError()
    def get_bounced_ray(self, ray, intersection):
        raise NotImplementedError()
    def render_intersection(self, intersection, ray, world, bouncenum):
        raise NotImplementedError()
class Triangle(Solid):
    """A depth-less plane"""
    def __init__(self, points):
        self.points = numpy.array(points, dtype=numpy.float_)
    def get_intersections(self, ray):
        return vectormath.get_line_intersection_with_plane(ray, self.points)
    def get_bounced_ray(self, ray, intersection):
        pass

class Checkerboard(Solid):
    """A depth-less plane"""
    def __init__(self, ray1, ray2, reflectivity=.5):
        if not ray1[0] == ray2[0]:
            raise Exception('Rays should have same origin');
        self.ray1 = numpy.array(ray1, dtype=numpy.float_)
        self.ray2 = numpy.array(ray2, dtype=numpy.float_)
        self.normal = numpy.cross(self.ray1[1] - self.ray1[0], self.ray2[1] - self.ray1[0])
        self.reflectivity = reflectivity

    def get_normal_ray(self, point):
        return (point, point+self.normal)

    def get_intersections(self, ray):
        r = vectormath.get_line_intersections_with_plane(ray, (self.ray1[0], self.ray1[1], self.ray2[1]))
        return r

    def get_bounced_ray(self, ray, intersection):
        """Returns a ray refleced across the normal at a point
        """
        intersection = numpy.array(intersection, dtype=numpy.float_)
        ray = numpy.array(ray)
        normal_ray = self.get_normal_ray(intersection)
        n_vec = normal_ray[1] - normal_ray[0]
        unit_n_vec = n_vec / numpy.linalg.norm(n_vec)
        ray_vec = ray[1] - ray[0]
        unit_ray_vec = ray_vec / numpy.linalg.norm(ray_vec)
        bounce_vec = unit_ray_vec - 2 * unit_n_vec * (numpy.dot(unit_ray_vec, unit_n_vec))
        result = (intersection, intersection + bounce_vec)
        return result

    def __repr__(self):
        return ' Checkerboard of rays '+str(tuple(self.ray1))+' and '+str(tuple(self.ray2))

    def render_intersection(self, intersection, ray, world, bouncenum):
        """Returns the value to render, possibly by recusively rendering reflections"""
        global bounces
        bounces.append(self)

        # getting color
        r1mod = (vectormath.get_projection_of_ray_onto_ray(
                [self.ray1[0], intersection],
                self.ray1
                ) % vectormath.get_distance(*self.ray1))
        r2mod = (vectormath.get_projection_of_ray_onto_ray(
                [self.ray2[0], intersection],
                self.ray2
                ) % vectormath.get_distance(*self.ray2))
        if (numpy.floor(r1mod) + numpy.floor(r2mod)) % 2 == 0:
            color = 0
        else:
            color = 1
        if bouncenum > BOUNCELIMIT:
            print 'bouncelimit acheived, ignoring further reflections for this ray'
            print bounces
            bounces = []
            return self.color * .5 + self.color * .5 * world.render_light(intersection, ray)
        else:
            bounce_ray = self.get_bounced_ray(ray, intersection)

        v = (
                color * .5 +
                self.reflectivity/2 * world.render_ray(bounce_ray, bouncenum+1) +
                color * (1 - self.reflectivity/2) * world.render_light(intersection, ray)
                )
        return v

class Sphere(Solid):
    """Represents a sphere object in a 3d world

    >>> Sphere((0,0,0), 1).get_first_intersection(((4,0,0), (3,0,0)))
    (1.0, 0.0, 0.0)
    """
    def __init__(self, center, radius, reflectivity=.5, color=None):
        self.center = numpy.array(center, dtype=numpy.float_)
        self.radius = float(radius)
        if color:
            self.color = color
        else:
            self.color = min(1, random.random() + .1)
        self.reflectivity = reflectivity

    def get_first_intersection(self, ray):
        line_intersections = self.get_intersections(ray)
        if len(line_intersections) == 1:
            return line_intersections[0]
        elif len(line_intersections) == 0:
            return None
        else:
            line_intersections.sort(key=lambda x: vectormath.get_distance(ray[0], x))
            return line_intersections[0]

    def get_intersections(self, ray):
        line_intersections = vectormath.get_line_intersections_with_sphere(ray, self.center, self.radius)
        return line_intersections

    def get_normal_ray(self, point):
        return (self.center, point)

    def get_bounced_ray(self, ray, intersection):
        """Returns a ray refleced across the normal at a point

        >>> s = Sphere((0,0,0), 1)
        >>> s.get_bounced_ray(((0, 0, 4), (0, 0, 3)), (0, 0, 1))
        (array([ 0.,  0.,  1.]), array([ 0.,  0.,  2.]))
        >>> s.get_bounced_ray(((0, 3, 4), (0, 2, 3)), (0, 0, 1))
        (array([ 0.,  0.,  1.]), array([ 0... -0.7...1.7...]))

        """
        intersection = numpy.array(intersection, dtype=numpy.float_)
        ray = numpy.array(ray)
        normal_ray = self.get_normal_ray(intersection)
        n_vec = normal_ray[1] - normal_ray[0]
        unit_n_vec = n_vec / numpy.linalg.norm(n_vec)
        ray_vec = ray[1] - ray[0]
        unit_ray_vec = ray_vec / numpy.linalg.norm(ray_vec)
        bounce_vec = unit_ray_vec - 2 * unit_n_vec * (numpy.dot(unit_ray_vec, unit_n_vec))
        result = (intersection, intersection + bounce_vec)
        return result

    def __repr__(self):
        return ' Sphere of radius '+str(self.radius)+' at '+str(self.center)

    def render_intersection(self, intersection, ray, world, bouncenum):
        """Returns the value to render, possibly by recusively rendering reflections"""
        global bounces
        bounces.append(self)
        bounce_ray = self.get_bounced_ray(ray, intersection)
        if bouncenum > BOUNCELIMIT:
            print 'bouncelimit acheived, ignoring further reflections for this ray'
            print bounces
            bounces = []
            return self.color
        v = (
                (0.0) * self.color +
                self.reflectivity * world.render_ray(bounce_ray, bouncenum+1) +
                (1 - self.reflectivity) * world.render_light(intersection, ray)
                )
        if v < 0:
            print 'from self:', (0.0) * self.color
            print 'from reflection:', self.reflectivity * world.render_ray(bounce_ray, bouncenum+1)
            print 'from light source:', (1 - self.reflectivity) * world.render_light(intersection, ray)
            print 'reflectivity of ', self.reflectivity
            raw_input()
        return v

class Light(object):
    """Point light source for evaluating light on surfaces.
    This light never bounces.

    >>> l = Light((0,0,-10))
    >>> l
     Light at [  0.   0. -10.]
    >>> l.get_light_theta(((0,0,0),(0,0,-1)))
    3.1415...
    >>> l.get_light_theta(((0,0,0),(1,0,0)))
    1.5707...
    """
    def __init__(self, position):
        self.position = numpy.array(position, dtype=numpy.float_)
        self.brightness = 1

    def __repr__(self):
        return ' Light at '+str(self.position)

    def get_light_theta(self, normal_ray):
        """Returns the light level contributed by this light"""
        normal_ray = numpy.array(normal_ray, dtype=numpy.float_)
        intersection = normal_ray[0]
        light_vec = intersection - self.position
        unit_light_vec = light_vec / numpy.linalg.norm(light_vec)
        n_vec = normal_ray[1] - normal_ray[0]
        unit_n_vec = n_vec / numpy.linalg.norm(n_vec)
        r = numpy.arccos(numpy.dot(unit_light_vec, unit_n_vec))
        return r

    def get_light_contribution(self, requested_intersection, ray, world):
        result = world.get_first_ray_intersection(ray)
        if result:
            obj, intersection = result
        else:
            return 0
            print 'got no intersection result'
        SAME_INTERSECTION_TOLERANCE = .00001
        if vectormath.get_distance(intersection, requested_intersection) < SAME_INTERSECTION_TOLERANCE:
            normal_ray = obj.get_normal_ray(intersection)
            theta = self.get_light_theta(normal_ray)
            return max(0.0, numpy.cos(theta))
        else:
            print 'different intersection found - this point is in shadow!'
            return 0

class View(object):
    """Represents a camera, and a rectangle on a plane, between which rays can be traced

    view plane defined by three points in space, but we use four (two rays)
    and the origins of both rays must equal each other

    camera defined by a distance from this plane, is always perpendicular

    >>> v = View(((0,0,3), (1,0,3)), ((0,0,3), (0,1,3)), 2)
    >>> v
     View at [ 0.  0.  5.] pointed at [ 0.  0.  3.]
      with horizontal vector [ 1.  0.  0.]
      and up vector [ 0.  1.  0.]

    array([ 0.,  0.,  5.])
    >>> list(v.get_ray_generator(10, 10, 20, 20))[0]
    (array([ 0.,  0.,  5.]), array([-10., -10.,   3.]))
    """
    def __init__(self, screen_width_ray, screen_height_ray, distance):
        if screen_height_ray[0] != screen_width_ray[0]:
            raise Exception('Rays should have same origin');
        self.screen_width_ray = numpy.array(screen_width_ray, dtype=numpy.float_)
        self.screen_height_ray = numpy.array(screen_height_ray, dtype=numpy.float_)
        self.camera_distance = float(distance)
        self.camera_position = vectormath.get_position_from_plane_and_distance(
                screen_width_ray, screen_height_ray, distance)
        self.w_vec = self.screen_width_ray[1] - self.screen_width_ray[0]
        self.h_vec = self.screen_height_ray[1] - self.screen_height_ray[0]
        self.unit_w_vec = self.w_vec / numpy.linalg.norm(self.w_vec)
        self.unit_h_vec = self.h_vec / numpy.linalg.norm(self.h_vec)

    def get_ray_generator(self, num_x_samples, num_y_samples, width, height):
        """Returns evenly spaced rays for rendering"""

        view_start = (self.screen_width_ray[0] -
                (width * self.unit_w_vec/2) -
                (height * self.unit_h_vec/2))

        for row in xrange(num_y_samples):
            for col in xrange(num_x_samples):
                point = (view_start +
                        self.unit_w_vec * (float(width) * col / (num_x_samples - 1)) +
                        self.unit_h_vec * (float(height) * row / (num_y_samples - 1)))
                yield (self.camera_position, point)

    def __repr__(self):
        return (' View at '+str(self.camera_position)+' pointed at '+
                str(self.screen_height_ray[0]) +
                '\n  with horizontal vector '+str(self.unit_w_vec)+
                '\n  and up vector '+str(self.unit_h_vec))

class World(object):
    def __init__(self):
        self.objects = []
        self.views = []
        self.lights = []

    def add_view(self, view):
        self.views.append(view)

    def add_object(self, obj):
        self.objects.append(obj)

    def add_light(self, light):
        self.lights.append(light)

    def get_first_ray_intersection(self, ray):
        intersections = []
        for obj in self.objects:
            intersections.extend([obj, intersect] for intersect in obj.get_intersections(ray))

        def object_intersection_sort_method(x):
            obj, intersection = x
            proj = vectormath.get_projection_of_ray_onto_ray((ray[0], intersection), ray)
            if proj < .0001: # behind object - return inf so goes to back of list
                return float('inf')
            else:
                return proj
        intersections.sort(key=object_intersection_sort_method)
        if intersections and object_intersection_sort_method(intersections[0]) < float('inf'):
            return intersections[0] # this is an (object, intersection) pair
        else:
            return None

    def render_ray(self, ray, bouncenum):
        result = self.get_first_ray_intersection(ray)

        if result:
            obj, intersection = result
            return obj.render_intersection(intersection, ray, self, bouncenum)
        else:
            return self.render_no_intersection_value(ray)

    def render_no_intersection_value(self, ray):
        return .05

    def render_light(self, intersection, ray):
        value = 0
        for light in self.lights:
            value += light.get_light_contribution(intersection, ray, self)
        return value

    def debug_render_view(self, view, w_samples, h_samples, width, height):
        for ray in view.get_ray_generator(w_samples, h_samples, width, height):
            print ray
            print self.render_ray(ray, 1)

    def render_images(self, w_samples, h_samples, viewscreen_width, viewscreen_height):
        """"""
        for view in self.views:
            im = self.render_view(view, w_samples, h_samples, viewscreen_width, viewscreen_height)
            im.save('/tmp/lastImage.png')
            im.show()

    def render_asciis(self, w_samples, h_samples, viewscreen_width, viewscreen_height):
        """"""
        for view in self.views:
            s = self.render_ascii(view, w_samples, h_samples, viewscreen_width, viewscreen_height)
            print
            print s
            print

    def render_view(self, view, w_samples, h_samples, viewscreen_width, viewscreen_height):
        sys.stderr.write('Rendering view '+str(view)+'\n')
        im = Image.new("1", (w_samples, h_samples))
        pixels = im.load()
        w_counter = 0
        h_counter = 0
        for ray in view.get_ray_generator(w_samples, h_samples, viewscreen_width, viewscreen_height):
            global bounces
            bounces = []
            r = self.render_ray(ray, 1)
            # height switches so as to correspond with PIL Image indexing,
            #  so width corresponds to first view vector, height to the second

            #TODO figure out what values Image wants in pixel array
            pixels[w_counter, (h_samples - h_counter - 1)] = int(256*r)
            w_counter = w_counter + 1
            if w_counter == w_samples:
                w_counter = 0
                h_counter = h_counter + 1
                sys.stderr.write(str(h_counter)+'/'+str(h_samples)+'\n')
        return im

    def render_ascii(self, view, w_samples, h_samples, viewscreen_width, viewscreen_height):
        sys.stderr.write('Rendering view '+str(view)+'\n')
        im = numpy.zeros((h_samples, w_samples), dtype=numpy.character)
        w_counter = 0
        h_counter = 0

        def get_ascii_char(r):
            """Returns a representative ascii char based on a 0-1 value

            Takes the whole pixel into account, not parts of it - hence
            characters that change the intensity of the whole space are used
            """
            zeroToTen = int((r+.0499) * 10)
            zeroToTenDict = {
                    0:' ',
                    1:'.',
                    2:'-',
                    3:'~',
                    4:'o',
                    5:'e',
                    6:'O',
                    8:'0',
                    9:'&',
                    10:'#',
                    }
            char = zeroToTenDict.get(zeroToTen, '?')
            return char

        for ray in view.get_ray_generator(w_samples, h_samples, viewscreen_width, viewscreen_height):
            global bounces
            bounces = []
            r = self.render_ray(ray, 1)
            # height switches so as to correspond with PIL Image indexing,
            #  so width corresponds to first view vector, height to the second

            im[(h_samples - h_counter - 1), w_counter] = get_ascii_char(r)
            w_counter = w_counter + 1
            if w_counter == w_samples:
                w_counter = 0
                h_counter = h_counter + 1
                sys.stderr.write(str(h_counter)+'/'+str(h_samples)+'\n')
        newlines = numpy.zeros((h_samples, 1), dtype=numpy.character)
        newlines[:] = '\n'
        with_newlines = numpy.hstack([im, newlines])
        s = ''.join(with_newlines.flat)
        return s

    def __repr__(self):
        s = 'World with views:'
        for view in self.views:
            s = s + '\n' + repr(view)
        s += '\nand containing objects: '
        for obj in self.objects:
            s = s + '\n' + repr(obj)
        return s

def getTestView():
    return View(((0,0,0), (1,0,0)), ((0,0,0), (0,1,0)), 2)


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
    #test()
