"""Renders 3d scences by raytracing"""
import vectormath
import numpy
from PIL import Image
import random

bounces = []

class Sphere(object):
    """Represents a sphere object in a 3d world

    >>> Sphere((0,0,0), 1).get_first_intersection(((4,0,0), (3,0,0)))
    (1.0, 0.0, 0.0)
    """
    def __init__(self, center, radius):
        self.center = numpy.array(center, dtype=numpy.float64)
        self.radius = float(radius)
        self.color = min(1, random.random() + .1)

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
        intersection = numpy.array(intersection, dtype=float)
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
        return 'Sphere of radius '+str(self.radius)+' at '+str(self.center)

    def render_intersection(self, intersection, ray, world, bouncenum):
        """Returns the value to render, possibly by recusively rendering reflections"""
        global bounces
        bounces.append(self)
        bounce_ray = self.get_bounced_ray(ray, intersection)
        if bouncenum > 10:
            print 'bouncelimit acheived'
            print bounces
            bounces = []
            return self.color
        return .3 * self.color + .7 * world.render_ray(bounce_ray, bouncenum+1)

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
        self.screen_width_ray = numpy.array(screen_width_ray, dtype=numpy.float64)
        self.screen_height_ray = numpy.array(screen_height_ray, dtype=numpy.float64)
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
        return ('View at '+str(self.camera_position)+' pointed at '+
                str(self.screen_height_ray[0]) +
                '\n with horizontal vector '+str(self.unit_w_vec)+
                '\n and up vector '+str(self.unit_h_vec))

class World(object):
    def __init__(self):
        self.objects = []
        self.views = []

    def add_view(self, view):
        self.views.append(view)

    def add_object(self, obj):
        self.objects.append(obj)

    def render_ray(self, ray, bouncenum):
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

        #intersections.sort(key=lambda x: vectormath.get_distance(ray[0], x[1]))
        intersections.sort(key=object_intersection_sort_method)
        if intersections and object_intersection_sort_method(intersections[0]) < float('inf'):
            return intersections[0][0].render_intersection(intersections[0][1], ray, self, bouncenum)
        else:
            return self.render_no_intersection_value(ray)

    def render_no_intersection_value(self, ray):
        return .05

    def debug_render_view(self, view, w_samples, h_samples, width, height):
        for ray in view.get_ray_generator(w_samples, h_samples, width, height):
            print ray
            print self.render_ray(ray, 1)

    def render_images(self, w_samples, h_samples, viewscreen_width, viewscreen_height):
        """"""
        for view in self.views:
            im = self.render_view(view, w_samples, h_samples, viewscreen_width, viewscreen_height)
            im.show()

    def render_view(self, view, w_samples, h_samples, viewscreen_width, viewscreen_height):
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
        return im

    def __repr__(self):
        s = 'World with views:'
        for view in self.views:
            s = s + '\n ' + repr(view)
        s += '\nand containing objects: '
        for obj in self.objects:
            s = s + '\n ' + repr(obj)
        return s

def getTestView():
    return View(((0,0,0), (1,0,0)), ((0,0,0), (0,1,0)), 2)

def test():
    w = World()
    w.add_object(Sphere((0,0,0), 1))
    w.add_object(Sphere((3,0,0), 1))
    w.add_object(Sphere((0,4,0), 2))
    w.add_object(Sphere((0,0,6), 5))
    #w.add_view(View(((0,0,-5), (2,0,-4)), ((0,0,-5), (0,2,-5)), -4))
    w.add_view(View(((0,0,-3), (2,0,-3)), ((0,0,-3), (0,2,-3)), -4))
    w.add_view(View(((0,0,-5), (2,0,-6)), ((0,0,-5), (0,2,-5)), -4))
    print w
    w.render_images(100, 100, 5, 5)
    #w.debug_render_view(w.views[0], 10, 10, 5, 5)
    raw_input()
    import os
    os.system('killall display')

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
    test()
