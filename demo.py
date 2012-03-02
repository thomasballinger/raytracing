#!/usr/bin/env python
from raycast import World, Sphere, Light, View, Checkerboard
def test():
    w = World()
    w.add_object(Sphere((0,0,0), 1))
    w.add_object(Sphere((3,0,0), 1))
    w.add_object(Sphere((0,4,0), 2))
    w.add_object(Sphere((3,0,2), 2))
    w.add_object(Sphere((-3,-3,-3), 2, 1))

    # imitation light
    #w.add_object(Sphere((100,100,0), 80, 0, .95))

    w.add_light(Light((100, 100, 0)))

    w.add_object(Checkerboard(((0,-5,0), (0,-5, 5)), ((0,-5,0),(5,-5,0))))

    #w.add_view(View(((0,0,-5), (2,0,-4)), ((0,0,-5), (0,2,-5)), -4))
    #w.add_view(View(((0,0,-3), (2,0,-3)), ((0,0,-3), (0,2,-3)), -4))
    w.add_view(View(((0,0,-5), (2,0,-6)), ((0,0,-5), (0,2,-5)), -4))
    #w.add_view(View(((0,0,-100), (2,0,-100)), ((0,0,-100), (0,2,-100)), -4))
    print w
    w.render_images(100, 100, 5, 5)
    #w.render_asciis(220, 100, 5, 5)
    #w.debug_render_view(w.views[0], 10, 10, 5, 5)
    #raw_input()
    #os.system('killall display')

test()
