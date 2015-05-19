""" Hill shading implementation for matplotlib

"""
from __future__ import print_function
from __future__ import division

import matplotlib as mpl
import numpy as np
from numpy import pi, cos, sin, gradient, arctan, hypot, arctan2
from matplotlib import cm
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

DEF_AZIMUTH = 165   # degrees
DEF_ELEVATION = 45  # degrees
    
def hill_shade(data, terrain=None, 
               scale_terrain=0.1, azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION, 
               cmap=cm.jet, terrain_nan_value=0):
    """ Calculates hillshading
    """
    if terrain is None:
        terrain = data
    
    assert data.ndim == 2, "data must be 2 dimensional"
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)
    
    # replace non finite values with zero for calcualting the intensity
    is_non_finite = np.logical_not(np.isfinite(terrain)) # TODO: use mask?
    if np.any(is_non_finite):
        finite_terrain = np.copy(terrain)
        finite_terrain[is_non_finite] = terrain_nan_value
    else:
        finite_terrain = terrain
    
    normalize_fn = mpl.colors.Normalize()
    norm_data = normalize_fn(data)
    rgba = cmap(norm_data)
    hsv = rgb_to_hsv(rgba[:, :, :3])

    intensity = hill_shade_intensity(finite_terrain, scale_terrain=scale_terrain, 
                                     azimuth=azimuth, elevation=elevation)
    hsv[:, :, 2] = intensity
    
    return hsv_to_rgb(hsv)
    

    
# Same as novitsky hill shading but where the gradient is
# multiplied by the scale instead of divided.
def hill_shade_intensity(terrain, scale_terrain=0.1, 
                         azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION):
    """ convert data to hillshade based on matplotlib.colors.LightSource class.
      input:
           terrain - a 2-d array of the terrain
           scale - scaling value of the terrain. higher number = higher gradient
           azdeg - where the light comes from: 0 south ; 90 east ; 180 north ;
                        270 west
           altdeg - where the light comes from: 0 horison ; 90 zenith
      output: a 2-d array of normalized hilshade
    """
    # convert alt, az to radians
    az = azimuth * pi / 180.0
    alt = elevation * pi / 180.0
    # gradient in x and y directions
    dx, dy = gradient(terrain * scale_terrain)
    slope = 0.5 * pi - arctan(hypot(dx, dy))
    aspect = arctan2(dx, dy)
    intensity = sin(alt) * sin(slope) + cos(alt) * \
        cos(slope) * cos(-az - aspect - 0.5 * pi)
    intensity = (intensity - intensity.min()) / \
        (intensity.max() - intensity.min())
    return intensity

