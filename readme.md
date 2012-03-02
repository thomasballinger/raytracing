Raycasting

Need to define the color of a pixel, once the first intersecting
object of the pixel ray has been found


* Light emitted from an object - color = green
* Direct reflextion - "Specular reflection" - bouncing the ray directly
   off of the object, mirror characteristic
* light from light source (reverse ray tracing) could be used to
   illuminate objects, plus some diffuse reflection?
   Maybe just use this information for how to ambiantly light objects?
* Shadow shortcut ?
* refactor to use origin, vector representations instead of rays, and
   factor out everything mathy
* figure out proper way to add light - logarithmically, I imagine?
* Add light hashing - right now light gets calculated many times for
   very similar intersections.
