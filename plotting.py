""" Various functions to support the demos
"""

from __future__ import print_function
from __future__ import division

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d

from intensity import matplotlib_intensity, normalized_intensity
from hillshade import DEF_AZIMUTH, DEF_ELEVATION, DEF_CMAP

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

#########
# Misc. #
#########

def add_colorbar(axes, cmap, norm=None):
    """ Aux function that makes a color bar from the image and adds it to the figure
    """
    assert cmap, "cmap undefined"
    assert norm.scaled(), "Norm function must be scaled to prevent side effects"
    #print("cnorm.vmin: {}".format(norm.vmin))
    #print("cnorm.vmax: {}".format(norm.vmax))
        
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    
    # mpl.colorbar.ColorbarBase can have side effects on norm!
    colorbar = mpl.colorbar.ColorbarBase(colorbar_axes, cmap=cmap, norm=norm, orientation='vertical')
    return colorbar


def remove_ticks(axes):
    """ Aux function that removes the ticks from the axes
    """
    axes.set_xticks([])
    axes.set_yticks([])

####################
# imshow functions #    
####################


def draw(axes, image_data, title='', 
         cmap=None, cnorm=None,  
         interpolation=IMSHOW_INTERP
         , ticks=False):
    """ Makes an image plot. 
        The image_data can be any array that can be plotted with the matplotlib imshow function.
    """
    print()
    print("Drawing: {}".format(title))
    print("  image_data.shape: {}".format(image_data.shape))
    
    if cnorm is None:
        cnorm = mpl.colors.Normalize(vmin=np.nanmin(image_data), vmax=np.nanmax(image_data))

    axes.imshow(image_data, interpolation=interpolation, norm=cnorm, cmap=cmap)
    axes.set_title(title)
    add_colorbar(axes, cmap, norm=cnorm)
    if not ticks:
        remove_ticks(axes)    
        
    
def plot_no_shading(axes, data, cmap=DEF_CMAP):
    """ Draws an image of the data without shading
    """
    axes.imshow(data, cmap, interpolation=IMSHOW_INTERP, origin=IMSHOW_ORIGIN)
    axes.set_title('Data without shading')
    add_colorbar(axes, cmap)
    #remove_ticks(axes)


def plot_mpl_intensity(axes, terrain, cmap=plt.cm.gist_gray, 
                       azim=DEF_AZIMUTH, elev=DEF_ELEVATION, scale_terrain = DEF_SCALE):
    """ Shows the shading component calculated from the matplotlib algorithm
    """
    intensity = matplotlib_intensity(terrain, fix_atan_bug=True,  
                                     azimuth=azim, elevation=elev, 
                                     scale_terrain = scale_terrain)
    axes.set_title('MPL (azim={}, elev={}) (scale={})'.format(azim, elev, scale_terrain))
    axes.imshow(intensity, cmap, interpolation=IMSHOW_INTERP, origin=IMSHOW_ORIGIN)
    add_colorbar(axes, cmap)
    #remove_ticks(axes)    


def plot_dot_intensity(axes, terrain, cmap=plt.cm.gist_gray, 
                           azim=DEF_AZIMUTH, elev=DEF_ELEVATION):
    """ Shows the shading component calculated from the dot product of the light source and the
        surface numbers.
    """
    intensity = normalized_intensity(terrain, azimuth=azim, elevation=elev)
    axes.set_title('Dot (azim={}, elev={})'.format(azim, elev))
    axes.imshow(intensity, cmap, interpolation=IMSHOW_INTERP, origin=IMSHOW_ORIGIN)
    add_colorbar(axes, cmap)
    #remove_ticks(axes)    

