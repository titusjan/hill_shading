# The MIT License (MIT)
# 
# Copyright (c) 2015 Pepijn Kenter
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
   
""" Functions that calculate intensity (irradiance) of light falling on a surface (terrain)
"""

from __future__ import print_function
from __future__ import division

import numpy as np

DEF_AZIMUTH = 135   # degrees
DEF_ELEVATION = 45  # degrees

DEF_AMBIENT_WEIGHT = 1
DEF_LAMP_WEIGHT = 5

DO_SANITY_CHECKS = True # If True intermediate results will be checked for boundary values.

    
def weighted_intensity(terrain,  
                       azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION, 
                       ambient_weight=DEF_AMBIENT_WEIGHT, lamp_weight=DEF_LAMP_WEIGHT):
    """ Calculates weighted average of the ambient illumination and the that of one or more lamps.
    
        The azimuth and elevation parameters can be scalars or lists. Use the latter for multiple 
        lamps. They should be of equal length.
         
        The lamp_weight can be given per lamp or one value can be specified, which is then used for
        all lamps sources.
        
        See also the hill_shade doc string.
    """
    # Make sure input is in the correct shape
    azimuths = enforce_list(azimuth)
    elevations = enforce_list(elevation)
    assert_same_length(azimuths, elevations, 'azimuths', 'elevations')
    
    lamp_weights = enforce_list(lamp_weight)
    if len(lamp_weights) == 1:
        lamp_weights = lamp_weights * len(azimuths) 
    assert_same_length(azimuths, lamp_weights, 'azimuths', 'lamp_weights')

    # Create weights and rel_intensities arrays   
    rel_intensities = [np.ones_like(terrain)]
    weights = [ambient_weight] 
    for azim, elev, lmpw in zip(azimuths, elevations, lamp_weights):
        rel_int = relative_surface_intensity(terrain, azimuth=azim, elevation=elev)
        rel_intensities.append(rel_int)
        weights.append(lmpw)
    
    rel_intensities = np.dstack(rel_intensities)
    weights = np.array(weights)
    
    # The actual weighted-average calculation
    unit_weights = weights / np.sum(weights)
    surface_intensity = np.average(rel_intensities, axis=2, weights=unit_weights)
    return surface_intensity


def relative_surface_intensity(terrain, azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION):
    """ Calculates the intensity that falls on the surface for light of intensity 1. 
        This equals cosine(theta) where theta is the angle between the direction of the light 
        source and the surface normal. When the cosine is negative, the angle is > 90 degrees. 
        In that case the surface receives no light so we clip to 0. The result of this function is 
        therefore always between 0 and 1.
    """
    # cosine(theta) is the dot-product of the normal vector and the vector that contains the  
    # direction of the light source. Both vectors must be unit vectors (have length 1).
    normals = surface_unit_normals(terrain)
    light = polar_to_cart3d(azimuth, elevation)
    intensity = np.dot(normals, light)
    
    if DO_SANITY_CHECKS:
        np.testing.assert_approx_equal(np.linalg.norm(light), 1.0, 
                                       err_msg="sanity check: light vector should have length 1")
        assert np.all(intensity >= -1.0), "sanity check: cos(theta) should be >= -1"
        assert np.all(intensity <= 1.0), "sanity check: cos(theta) should be <= 1"
    
    # Where the dot product is smaller than 0 the angle between the light source and the surface
    # is larger than 90 degrees. These pixels receive no light so we clip the intensity to 0.
    intensity = np.clip(intensity, 0.0, 1.0)
    return intensity
    
    
def surface_unit_normals(terrain):
    """ Returns an array of shape (n_rows, n_cols, 3) with unit surface normals. 
        That is, each result[r,c,:] contains the vector of length 1, perpendicular to the surface.
    """ 
    dr, dc = np.gradient(terrain)
    
    # Vectors that do a step of 1 in the row direction, 0 in the column direction and dr upwards
    vr = np.dstack((dr, np.ones_like(dr), np.zeros_like(dr)))   # shape = (n_rows, n_cols, 3)
    
    # Vectors that do a step of 0 in the row direction, 1 in the column direction and dc upwards
    vc = np.dstack((dc, np.zeros_like(dc), np.ones_like(dc)))   # shape = (n_rows, n_cols, 3)

    # The surface normals can be calculated as the cross product of those vector pairs
    surface_normals = np.cross(vr, vc)  # surface_normals.shape = (n_rows, n_cols, 3)
    
    # Divide the normals by their magnitude to get unit vectors. 
    # (Add artificial dimension of length 1 so that we can use broadcasting)
    normal_magnitudes = np.linalg.norm(surface_normals, axis=2)
    return surface_normals / np.expand_dims(normal_magnitudes, axis=2)  


def polar_to_cart3d(azimuth, elevation):
    """ Converts the polar (azimuth, elevation) unit vector to (height, row, col) coordinates.
    """  
    azimuth_rad = azimuth * np.pi / 180.0
    elevation_rad = elevation * np.pi / 180.0
    
    height = np.sin(elevation_rad)
    row    = np.cos(elevation_rad) * np.sin(azimuth_rad)
    col    = np.cos(elevation_rad) * np.cos(azimuth_rad)
    
    return np.array([height, row, col])

    
def assert_same_length(s0, s1, label0, label1):
    """ Asserts list s1 and s2 have the same lengths
    """
    if len(s0) != len(s1):
        raise AssertionError("size mismatch between {} (len={}) and {} (len={})"
                             .format(label0, s0, label1, s1))
           
def enforce_list(var):
    """ Runs the list() constructor on the var parameter.
    """
    try:
        return list(var) # iterable
    except TypeError:
        return [var]


# The mpl_surface_intensity is included to compare the matplotlib implementation with 
# the relative_surface_intensity() results.
#
def mpl_surface_intensity(terrain, 
                          azimuth=165, elevation=DEF_ELEVATION, 
                          azim0_is_east=False, normalize=False):
    """ Calculates the intensity that falls on the surface when illuminated with intensity 1 
        
        This is the implementation as is used in matplotlib.
        Forked from Ran Novitsky's blog (no license found).
        The original source is the LightSource.shade_rgb function of the matplotlib.colors module.
        See:
            http://rnovitsky.blogspot.nl/2010/04/using-hillshade-image-as-intensity.html
            https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/colors.py
            
        input:
            terrain - a 2-d array of the terrain
            azimuth - where the light comes from: 0 south ; 90 east ; 180 north ;
                        270 west
            elevation - where the light comes from: 0 horizon ; 90 zenith
            
        output: 
            a 2-d array of normalized hillshade
    """
    from numpy import pi, cos, sin, gradient, arctan, hypot, arctan2
    
    # Convert alt, az to radians
    az = azimuth * pi / 180.0
    alt = elevation * pi / 180.0
    
    # gradient in x and y directions
    dx, dy = gradient(terrain)
    
    slope = 0.5 * pi - arctan(hypot(dx, dy))
    if azim0_is_east:
        # The arctan docs specify that the parameters are (y, x), in that order.
        # This makes an azimuth of 0 correspond to east. 
        aspect = arctan2(dy, dx)
    else:
        aspect = arctan2(dx, dy)
    intensity = sin(alt) * sin(slope) + cos(alt) * cos(slope) * cos(-az - aspect - 0.5 * pi)

    if DO_SANITY_CHECKS:
        assert np.all(intensity >= -1.0), "sanity check: cos(theta) should be >= -1"
        assert np.all(intensity <= 1.0), "sanity check: cos(theta) should be <= 1"

    # The matplotlib source just normalizes the intensities. However, I believe that their 
    # intensities are the same as mine so that, where they are < 0 the angle between the light 
    # source and the surface is larger than 90 degrees. These pixels receive no light so 
    # they should be clipped. This is done when the normalize parameter is set to False.
    
    if normalize:
        intensity = (intensity - intensity.min()) / (intensity.max() - intensity.min())
    else:
        intensity = np.clip(intensity, 0.0, 1.0)
        
    return intensity

