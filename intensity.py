""" Functions that calculate intensity of light falling on a surface (terrain)

"""
from __future__ import print_function
from __future__ import division

import numpy as np
from numpy import pi, cos, sin, gradient, arctan, hypot, arctan2

#DEF_AZIMUTH = 165   # degrees
DEF_AZIMUTH = 135   # degrees
DEF_ELEVATION = 45  # degrees


def polar_to_cart3d(azimuth, elevation):
    """ Converts the polar (azimuth, elevation) unit vector to (height, row, col) coordinates.
    """  
    azimuth_rad = azimuth * np.pi / 180.0
    elevation_rad = elevation * np.pi / 180.0
    
    height = np.sin(elevation_rad)
    row    = np.cos(elevation_rad) * np.sin(azimuth_rad)
    col    = np.cos(elevation_rad) * np.cos(azimuth_rad)
    
    return np.array([height, row, col])
    

def combined_intensities(terrain, azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION):
    
    return diffuse_intensity(terrain, azimuth=azimuth, elevation=elevation)
    
    

def diffuse_intensity(terrain, azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION):
    
    normals = surface_unit_normals(terrain)
    light = polar_to_cart3d(azimuth, elevation)
    
    np.testing.assert_approx_equal(np.linalg.norm(light), 1.0, 
                                   err_msg="sanity check: light vector should have length 1")
    
    intensity = np.dot(normals, light)
    assert np.all(intensity <= 1.0), "sanity check: cosinus should be <= 1"
    
    # Where the dot product is smaller than 0 the angle between the light source and the surface
    # is larger than 90 degrees. These pixels receive no light so we clip the intensity to 0.
    intensity = np.clip(intensity, 0.0, 1.0)
    assert np.all(intensity >= 0.0), "sanity check: cosinus should be >= 0"
    return intensity
    
    
    
def surface_unit_normals(terrain):
    """ Returns an array of shape (n_rows, n_cols, 3) with unit surface normals. 
        That is, each result[r,c,:] contains the vector of length 1, perpendicular to the surface.
    """ 
    dr, dc = np.gradient(terrain)
    
    # Vectors that do a step of 1 in the row direction, 0 in the column and dr upwards
    vr = np.dstack((dr, np.ones_like(dr), np.zeros_like(dr)))
    
    # Vectors that do a step of 0 in the row direction, 1 in the column and dc upwards
    vc = np.dstack((dc, np.zeros_like(dc), np.ones_like(dc)))

    # The surface normals can be calculated as the cross product of those vector pairs
    surface_normals = np.cross(vr, vc)  # surface_normals.shape = (200, 200, 3)
    
    # Divide the normals by their magnitude to get unit vectors. 
    # (Add artificial dimension of length 1 so that we can use broadcasting)
    normal_magnitudes = np.linalg.norm(surface_normals, axis=2)
    return surface_normals / np.expand_dims(normal_magnitudes, axis=2)  

    
def matplotlib_intensity(terrain, scale_terrain=10, fix_atan_bug=True, 
                         azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION):
    """ Calculates the shade intensity from the terrain gradient and an artificial light source
    
        Forked from Ran Novitsky's blog (but with inverted scale_terrain meaning), but the original
        source is the LightSource.shade_rgb function of the matplotlib.colors module.
        See:
            http://rnovitsky.blogspot.nl/2010/04/using-hillshade-image-as-intensity.html
            https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/colors.py
            
        input:
            terrain - a 2-d array of the terrain
            scale_terrain - scaling value of the terrain. higher number = higher gradient
            azimuth - where the light comes from: 0 south ; 90 east ; 180 north ;
                        270 west
            elevation - where the light comes from: 0 horiaon ; 90 zenith
            
        output: 
            a 2-d array of normalized hillshade
    """
    # Convert alt, az to radians
    az = azimuth * pi / 180.0
    alt = elevation * pi / 180.0
    
    # gradient in x and y directions
    dx, dy = gradient(terrain * scale_terrain)
    
    slope = 0.5 * pi - arctan(hypot(dx, dy))
    if fix_atan_bug:
        aspect = arctan2(dy, dx)
    else:
        aspect = arctan2(dx, dy)
    intensity = sin(alt) * sin(slope) + cos(alt) * cos(slope) * cos(-az - aspect - 0.5 * pi)
    
    # Normalize intenstity
    intensity = (intensity - intensity.min()) / (intensity.max() - intensity.min())
        
    return intensity

