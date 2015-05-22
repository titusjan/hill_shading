""" Hill shading implementation for matplotlib

"""
from __future__ import print_function
from __future__ import division

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from intensity import  relative_surface_intensity
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

DEF_AZIMUTH = 135   # degrees
DEF_ELEVATION = 45  # degrees


# For a list of colormaps see:
#    http://matplotlib.org/examples/color/colormaps_reference.html

# For choosing a good color map see:
#    http://matplotlib.org/users/colormaps.html 

INTENSITY_CMAP = plt.cm.get_cmap('gray')
INTENSITY_CMAP.set_bad('red')
INTENSITY_CMAP.set_over('blue')
INTENSITY_CMAP.set_under('yellow')

#DEF_CMAP = plt.cm.get_cmap('cool')
#DEF_CMAP = plt.cm.get_cmap('cubehelix')  # doesn't work well with HSV blending
#DEF_CMAP = plt.cm.get_cmap('hot')        # doesn't work well with HSV blending
DEF_CMAP = plt.cm.get_cmap('gist_earth')
    
    
def is_non_finite_mask(array):
    "Returns mask with ones where the data is infite or Nan"
    np.logical_not(np.isfinite(array))
    
    
def replace_nans(array, array_nan_value, mask=None):
    """ Returns a copy of the array with the NaNs replaced by nan_value
    """
    finite_array = np.copy(array)
    if mask is None:
        mask =  is_non_finite_mask(array)
    if np.any(mask):
        finite_array[mask] = array_nan_value
    return finite_array
    
    
def normalize(values, vmin=None, vmax=None, norm=None):
    """ Normalize values between using a mpl.colors.Normalize object or (vmin, vmax) interval.
        If norm is specified, vmin and vmax are ignored.
        If norm is None and vmin and vmax are None, the values are autoscaled.
    """
    if norm is None:
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        
    return norm(values) 
    

def color_data(data, cmap, vmin=None, vmax=None, norm=None):
    """ Auxiliary function that colors the data.
    """
    norm_data = normalize(data, vmin=vmin, vmax=vmax, norm=norm)
    rgba = cmap(norm_data)
    return rgba


def no_blending(rgba, norm_intensities):
    """ Just returns the intensities. Use in hill_shade to just view the calculated intensities
    """
    assert norm_intensities.ndim == 2, "norm_intensities must be 2 dimensional"
    return norm_intensities


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
        
        IMPORTANT: may give incorrect results for color maps that include colors close to black 
            (e.g. cubehelix or hot). 
                
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
               lamp_weight=1, ambient_weight=0.15,  
               cmap=DEF_CMAP, vmin=None, vmax=None, norm=None, blend_function=rgb_blending,  
               azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION):
    """ Calculates hill shading.
    """
    if terrain is None:
        terrain = data
    
    assert data.ndim == 2, "data must be 2 dimensional"
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)
    
    relative_intensity = relative_surface_intensity(terrain, azimuth=azimuth, elevation=elevation)
    
    ambient_intensity = np.ones_like(relative_intensity)
    intensities = np.dstack((relative_intensity, ambient_intensity))
    
    weights = np.array([lamp_weight, ambient_weight])
    unit_weights = weights / np.sum(weights)
    surface_intensity = np.average(intensities, axis=2, weights=unit_weights)
        
    rgba = color_data(data, cmap=cmap, vmin=vmin, vmax=vmax, norm=norm)
    return blend_function(rgba, surface_intensity)


