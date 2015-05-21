""" Hill shading implementation for matplotlib

"""
from __future__ import print_function
from __future__ import division

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from numpy import pi, cos, sin, gradient, arctan, hypot, arctan2
from matplotlib import cm
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

DEF_AZIMUTH = 165   # degrees
DEF_ELEVATION = 45  # degrees
DEF_CMAP = plt.cm.gist_earth
    
    
def replace_nans(array, array_nan_value):
    """ Returns a copy of the array with the NaNs replaced by nan_value
    """
    finite_array = np.copy(array)
    is_non_finite = np.logical_not(np.isfinite(array)) # TODO: use mask?
    if np.any(is_non_finite):
        finite_array[is_non_finite] = array_nan_value
    return finite_array
    
    
def normalize(values, vmin=None, vmax=None):
    """ Normalize values between 0 and 1.
        values below vmin will be set to 0, values above vmax to 1.
        If vmin and vmax are None, they are determined from the data (i.e. auto-scaling)
    """
    norm_fn = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    return norm_fn(values) 
    

def hsv_blending(rgba, norm_intensities):
    """ Calculates image colors by placing the normalized intensities in the Value layer of the
        HSV color of the normalized data.
                
        :param rgba: [nrows, ncols, 3|4] RGB or RGBA array. The alpha layer will be ignored.
        :param norm_intensities: normalized intensities
        
        Returns 3D array that can be plotted with matplotlib.imshow(). The last dimension is RGB.
    """
    hsv = rgb_to_hsv(rgba[:, :, :3])
    hsv[:, :, 2] = norm_intensities
    return hsv_to_rgb(hsv)
    
    
def pegtop_blending(rgba, norm_intensities):
    """ Calculates image colors with the Pegtop Light shading of ImageMagick
    
        See:
            http://www.imagemagick.org/Usage/compose/#pegtoplight
    
        Forked from Ran Novitsky's blog
            http://rnovitsky.blogspot.nl/2010/04/using-hillshade-image-as-intensity.html    
        
        :param rgba: [nrows, ncols, 3|4] RGB or RGBA array. The alpha layer will be ignored.
        :param norm_intensities: normalized intensities
        
        Returns 3D array that can be plotted with matplotlib.imshow(). The last dimension is RGB.
    """
    # get rgb of normalized data based on cmap
    rgb = rgba[:, :, :3]
    
    # form an rgb eqvivalent of intensity
    d = norm_intensities.repeat(3).reshape(rgb.shape)
    
    # simulate illumination based on pegtop algorithm.
    return 2 * d * rgb + (rgb ** 2) * (1 - 2 * d)
    
    
def hill_shade(data, terrain=None, 
               cmap=DEF_CMAP, vmin=None, vmax=None, blend_function=hsv_blending,  
               azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION, 
               scale_terrain=0.1, terrain_nan_value=0):
    """ Calculates hill shading by putting the intensity in the Value layer of the HSV space.
    """
    if terrain is None:
        terrain = data
    
    assert data.ndim == 2, "data must be 2 dimensional"
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)

    finite_terrain = replace_nans(terrain, terrain_nan_value)
    norm_intensities = matplotlib_intensity(finite_terrain, scale_terrain=scale_terrain, 
                                            azimuth=azimuth, elevation=elevation)
    
    return color_data(data, norm_intensities, 
                      cmap=cmap, vmin=vmin, vmax=vmax, blend_function=blend_function)


def color_data(data, norm_intensities, 
               cmap=DEF_CMAP, vmin=None, vmax=None, blend_function=hsv_blending):
    """ Auxiliary function that colors the data and blends the normalized intensities.
        Use this if you want to calculate your own normalized intensities, otherwise use the 
        hill_shade function, which is more high-level. See this function for the explanation of
        the parameters.
    """
    norm_data = normalize(data, vmin, vmax)
    rgba = cmap(norm_data)
    return blend_function(rgba, norm_intensities)


    
def matplotlib_intensity(terrain, scale_terrain=10, 
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
        output: a 2-d array of normalized hillshade
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
    
    intensity = (intensity - intensity.min()) / (intensity.max() - intensity.min())
        
    return intensity

