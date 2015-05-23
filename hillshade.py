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
INTENSITY_CMAP.set_over('blue')    # to check that no intensity is above 1
INTENSITY_CMAP.set_under('yellow') # to check that no intensity is below 0

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
    
        Forked from Ran Novitsky's blog (no license found)
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
    
    
def hill_shade(data, terrain=None, 
               azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION, 
               ambient_weight=0.15, lamp_weight=1, 
               cmap=DEF_CMAP, vmin=None, vmax=None, norm=None, 
               blend_function=rgb_blending):
    """ Calculates a shaded relief given a 2D array of surface heights. 
    
        You can specify data properties and terrain height in separate parameters. The data array
        determines the (unshaded) color, the terrain is used to calculate the shading component.
        If the terrain is left to None, the data array will be used as terrain as well. The terrain
        parameter can also be used to scale the surface heights. E.g. use: terrain = data * 10
        
        The relief is calculated from one or more artificial light sources which positions are
        specified by their azimuth and elevation angle. Each lamp can have a weight, which 
        corresponds to its strength. Ambient light is light that reaches the surface via indirect 
        illumination. If the ambient weight set to 0, pixels that are not illuminated by any lamp 
        are rendered completely black, which is usually undesirable.   
        
        The algorithm uses a color map to color the relief. The minimum and maximum values of the
        color scale can be specified by vmin and vmax (or by giving a normalization function). If
        these are all None (the default), the color bar will be auto-scaled.
        
        The blend_function is the function that merges the color and shade components into the
        final result. It was found that rbg_blending, the default, gives the best results. If set
        to no_blending, only the intensities of the shade component are returned. This is useful
        for debugging.
    
        :param data: 2D array with terrain properties
        :param terrain: 2D array with terrain heights
        :param azimuth: azimuth angle [degrees] of the lamp direction(s). Can be scalar or list.
        :param elevation: elevation angle [degrees] of the lamp direction(s). Can be scalar or list.
        :param ambient_weight: the relative strength of the abmient illumination
        :param lamp_weight: the relative strength of the lamp or lamps 
        :param cmap: matplotlib color map to color the data (default: 'gist_earth')
        :param vmin: use to set a minimum value of the color scale 
        :param vmax: use to set a maximum value of the color scale
        :param norm: colorbar normalization function. E.g.: mpl.colors.Normalize(vmin=0.0, vmax=1.0)
        :param blend_function: function that blends shading and color (default = rbg_blending)
        
        :returns: 3D array (n_rows, n_cols, 3) with for each pixel an RGB color. 
            If blend_function=no_blending the result is a 2D array with only shading intensities.
    """
    if terrain is None:
        terrain = data
    
    assert data.ndim == 2, "data must be 2 dimensional"
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)
    
    # Calculates relative surface intensity for all lamps
    azimuths = enforce_list(azimuth)
    elevations = enforce_list(elevation)
    lamp_weights = enforce_list(lamp_weight)
    assert_same_length(azimuths, elevations, 'azimuths', 'elevations')
    assert_same_length(azimuths, lamp_weights, 'azimuths', 'lamp_weights')
   
    rel_intensities = [np.ones_like(terrain)]
    weights = [ambient_weight] 
    for azim, elev, lmpw in zip(azimuths, elevations, lamp_weights):
        rel_int = relative_surface_intensity(terrain, azimuth=azim, elevation=elev)
        rel_intensities.append(rel_int)
        weights.append(lmpw)
    
    rel_intensities = np.dstack(rel_intensities)
    weights = np.array(weights)
    
    unit_weights = weights / np.sum(weights)
    surface_intensity = np.average(rel_intensities, axis=2, weights=unit_weights)
        
    rgba = color_data(data, cmap=cmap, vmin=vmin, vmax=vmax, norm=norm)
    return blend_function(rgba, surface_intensity)


