Raycasting
----------
<img src='http://i.imgur.com/GIdn4.png' title='Example Rendering' width='800px' />


Features:

* Ambient, specular, and diffuse light

* Spheres, planes 

* Multiple views

To Do:

* more flexible checkerboard (checker size based on defining vectors)

* finite planes (triangles, squares)
   
* Optimize diffuse light (no need to look up at each bounce)
  fuzzy light hashing - 
  right now light gets calculated many times for very similar intersections.

* Optimize until realtime ascii rendering is possible

* refactor to use origin, vector representations instead of rays, and
   factor out everything mathy

* figure out proper way to add light - logarithmically, I imagine?

Not planning to impement at this time:

* Color - light emitted from an object - color = green
