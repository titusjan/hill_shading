""" Hill shading implementation for matplotlib

"""
from __future__ import print_function
from __future__ import division

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from intensity import  diffuse_intensity
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

DEF_AZIMUTH = 165   # degrees
DEF_ELEVATION = 45  # degrees


# For a list of colormaps see:
#    http://matplotlib.org/examples/color/colormaps_reference.html

# For choosing a good color map see:
#    http://matplotlib.org/users/colormaps.html 

#DEF_CMAP = plt.cm.cool
#DEF_CMAP = plt.cm.cubehelix # doesn't work well with HSV blending
#DEF_CMAP = plt.cm.hot       # doesn't work well with HSV blending
#DEF_CMAP = plt.cm.bwr
#DEF_CMAP = plt.cm.gist_earth
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
    

def rgb_blending(rgba, norm_intensities):
    """ Calculates image colors by multiplying the rgb value with the normalized intensities
                
        :param rgba: [nrows, ncols, 3|4] RGB or RGBA array. The alpha layer will be ignored.
        :param norm_intensities: normalized intensities
        
        Returns 3D array that can be plotted with matplotlib.imshow(). The last dimension is RGB.
    """
    assert rgba.ndim == 3, "rgb must be 3 dimensional"
    assert norm_intensities.ndim == 2, "norm_intensities must be 2 dimensional"
    
    # Add artificial dimension of length 1 at the end of norm_intensities so that it can be
    # multiplied with the rgb array using numpy broad casting
    expanded_intensities = np.expand_dims(norm_intensities, axis=2) 
    rgb = rgba[:, :, :3]
    return rgb * expanded_intensities
        

def hsv_blending(rgba, norm_intensities):
    """ Calculates image colors by placing the normalized intensities in the Value layer of the
        HSV color of the normalized data.
        
        IMPORTANT: may give incorrect results for color maps that include colors close to 
            white and black (e.g. cubehelix or hot). 
                
        :param rgba: [nrows, ncols, 3|4] RGB or RGBA array. The alpha layer will be ignored.
        :param norm_intensities: normalized intensities
        
        Returns 3D array that can be plotted with matplotlib.imshow(). The last dimension is RGB.
    """
    rgb = rgba[:, :, :3]
    hsv = rgb_to_hsv(rgb)
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
               cmap=DEF_CMAP, vmin=None, vmax=None, blend_function=rgb_blending,  
               azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION, 
               scale_terrain=0.1, terrain_nan_value=0):
    """ Calculates hill shading by putting the intensity in the Value layer of the HSV space.
    """
    if terrain is None:
        terrain = data
    
    assert data.ndim == 2, "data must be 2 dimensional"
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)

    finite_terrain = replace_nans(terrain, terrain_nan_value)
    norm_intensities = diffuse_intensity(finite_terrain, scale_terrain=scale_terrain, 
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

