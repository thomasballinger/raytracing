Raycasting
----------

Features:

* Ambient, specular, and diffuse light

* Spheres, planes 

* Multiple views

To Do:

* more flexible checkerboard

* finite planes (triangles, squares)
   off of the object, mirror characteristic
   
* Optimize diffuse light (no need to look up at each bounce)
  I think this is light hashing - 
  Right now light gets calculated many times for very similar intersections.
  Maybe that is what a "lightmap" is!?!

* Optimize until realtime ascii rendering is possible

* refactor to use origin, vector representations instead of rays, and
   factor out everything mathy

* figure out proper way to add light - logarithmically, I imagine?

Not planning to impement at this time:

* Color - light emitted from an object - color = green
