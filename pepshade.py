""" Hill shading implementation for matplotlib

    TODO:
        clean up hill_shade_intensity
        allow hill_shade to accept separate data for the color
    
"""
import matplotlib as mpl
import numpy as np
from numpy import pi, cos, sin, gradient, arctan, hypot, arctan2
from matplotlib import cm
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

DEF_AZIMUTH = 165   # degrees
DEF_ELEVATION = 45  # degrees
    
def hill_shade(data, scale=0.1, 
               azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION, 
               cmap=cm.jet, nan_replacement=0):
    """ Calculates hillshading
    """
    assert data.ndim == 2, "data must be 2 dimensional"
    
    # replace non finite values with zero for calcualting the intensity

    is_non_finite = np.logical_not(np.isfinite(data)) # use mask?
    if np.any(is_non_finite):
        finite_data = np.copy(data)
        finite_data[is_non_finite] = nan_replacement
    else:
        finite_data = data
    
    intensity = hill_shade_intensity(finite_data, scale=scale, 
                                     azimuth=azimuth, elevation=elevation)
    normalize_fn = mpl.colors.Normalize()
    norm_data = normalize_fn(finite_data)
    rgba = cmap(norm_data)
    hsv = rgb_to_hsv(rgba[:, :, :3])
    hsv[:, :, 2] = intensity
    
    return hsv_to_rgb(hsv)
    

    
# Same as novitsky hill shading but where the gradient is
# multiplied by the scale instead of divided.
def hill_shade_intensity(data, scale=0.1, 
                         azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION):
    ''' convert data to hillshade based on matplotlib.colors.LightSource class.
      input:
           data - a 2-d array of data
           scale - scaling value of the data. higher number = lower gradient
           azdeg - where the light comes from: 0 south ; 90 east ; 180 north ;
                        270 west
           altdeg - where the light comes from: 0 horison ; 90 zenith
      output: a 2-d array of normalized hilshade
    '''
    # convert alt, az to radians
    az = azimuth * pi / 180.0
    alt = elevation * pi / 180.0
    # gradient in x and y directions
    dx, dy = gradient(data * scale)
    slope = 0.5 * pi - arctan(hypot(dx, dy))
    aspect = arctan2(dx, dy)
    intensity = sin(alt) * sin(slope) + cos(alt) * \
        cos(slope) * cos(-az - aspect - 0.5 * pi)
    intensity = (intensity - intensity.min()) / \
        (intensity.max() - intensity.min())
    return intensity

