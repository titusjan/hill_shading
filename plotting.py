""" Various functions to support the demos
"""

from __future__ import print_function
from __future__ import division

import numpy as np
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d

from intensity import mpl_surface_intensity
from hillshade import DEF_AZIMUTH, DEF_ELEVATION, DEF_CMAP, color_data, rgb_blending

DEF_SCALE = 10.0
#IMSHOW_INTERP = 'nearest'
IMSHOW_INTERP = None # default interpolation
IMSHOW_ORIGIN = 'lower'


########################
# Test data generation #
########################

def _generate_concentric_circles(size):
    "Generates concentric circles test data"
    grid = np.linspace(-5, 5, size)
    x, y = np.meshgrid(grid, grid)
    data = np.sqrt(x ** 2 + y ** 2) + np.sin(x ** 2 + y ** 2)
    return data


def _generate_hills(size):
    "Generates noisy hills test data"
    _, _, data = axes3d.get_test_data(6.0 / size)  
    return -0.1 * data # to make in about the same height as the circles


def make_test_data(shape, noise_factor=0.0, size=200):
    """ Generates test data with optional noise.
        The shape can be either 'circles' or 'hills'
        Returns: a square array.
    """
    if shape == 'circles':
        data = _generate_concentric_circles(size)
    elif shape == 'hills':
        data = _generate_hills(size)
    else:
        raise ValueError("Invalid shape string: {!r}".format(shape))
    
    noise = noise_factor * np.random.randn(*data.shape) # unpack shape
    return data + noise

###########
# drawing #
###########

def add_colorbar(axes, cmap, norm=None):
    """ Aux function that makes a color bar from the image and adds it to the figure
    """
    assert cmap, "cmap undefined"
    assert norm.scaled(), "Norm function must be scaled to prevent side effects"
    #print("cnorm.vmin: {}".format(norm.vmin))
    #print("cnorm.vmax: {}".format(norm.vmax))
        
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    
    # mpl.colorbar.ColorbarBase can have side effects on norm if norm is auto scaling!
    colorbar = mpl.colorbar.ColorbarBase(colorbar_axes, cmap=cmap, norm=norm, 
                                         orientation='vertical', extend='both')
    return colorbar


def remove_ticks(axes):
    """ Aux function that removes the ticks from the axes
    """
    axes.set_xticks([])
    axes.set_yticks([])


def draw(axes, image_data, title='', 
         cmap=None, norm=None,  
         interpolation=IMSHOW_INTERP,
         origin=IMSHOW_ORIGIN,  
         ticks=False):
    """ Makes an image plot. 
        The image_data can be any array that can be plotted with the matplotlib imshow function.
    """
    print()
    print("Drawing: {}".format(title))
    print("  image_data.shape: {}".format(image_data.shape))
    
    if norm is None:
        norm = mpl.colors.Normalize(vmin=np.nanmin(image_data), vmax=np.nanmax(image_data))

    axes.imshow(image_data, interpolation=interpolation, norm=norm, cmap=cmap, origin=origin)
    axes.set_title(title)
    add_colorbar(axes, cmap, norm=norm)
    if not ticks:
        remove_ticks(axes)    
        

########
# misc #
########
    
def mpl_hill_shade(data, terrain=None, 
                   cmap=DEF_CMAP, vmin=None, vmax=None, norm=None, blend_function=rgb_blending,  
                   azimuth=DEF_AZIMUTH, elevation=DEF_ELEVATION):
    """ Hill shading that uses the matplotlib intensities. Is only for making comparison between
        blending methods where we need to include the matplotlib hill shading. For all other
        plots we can use the combined_intensities function that is used in the regular hill_shade()
        
    """
    if terrain is None:
        terrain = data
    
    assert data.ndim == 2, "data must be 2 dimensional"
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)

    norm_intensities = mpl_surface_intensity(terrain, azimuth=azimuth, elevation=elevation)
    
    rgba = color_data(data, cmap=cmap, vmin=vmin, vmax=vmax, norm=norm)
    return blend_function(rgba, norm_intensities)

