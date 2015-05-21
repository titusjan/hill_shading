""" Tests various hill shading implementation which differ in the way they blend the
    shading intensity and the color of the data.

    Matplotlib shading:
    http://matplotlib.org/examples/pylab_examples/shading_example.html?highlight=codex%20shade

    Ran Novitsky
    http://rnovitsky.blogspot.nl/2010/04/using-hillshade-image-as-intensity.html

    TODO: look at
    (http://reference.wolfram.com/mathematica/ref/ReliefPlot.html)
    or Generic Mapping Tools (http://gmt.soest.hawaii.edu/)
    
    - Use inproduct to calculate angle between normal an light source.
"""
from __future__ import print_function
from __future__ import division

import sys
import matplotlib as mpl

mpl.interactive(False) 
if len(sys.argv) > 1 and sys.argv[1]=='--qt':
    print("Force 'Qt4Agg' backend")
    mpl.use('Qt4Agg')  
    mpl.rcParams['backend.qt4'] = 'PySide'
    

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d

from intensity import matplotlib_intensity, normalized_intensity
from hillshade import DEF_AZIMUTH, DEF_ELEVATION, DEF_CMAP

DEF_SCALE = 10.0
#IMSHOW_INTERP = 'nearest'
IMSHOW_INTERP = None # default interpolation
IMSHOW_ORIGIN = 'lower'

def add_colorbar(fig, axes, cmap, norm=None):
    """ Aux function that makes a color bar from the image and adds it to the figure
    """
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    colorbar = mpl.colorbar.ColorbarBase(colorbar_axes, cmap=cmap, norm=norm, orientation='vertical')
    return colorbar


def remove_ticks(axes):
    """ Aux function that removes the ticks from the axes
    """
    axes.set_xticks([])
    axes.set_yticks([])
    
    
def plot_data(fig, axes, data, cmap=DEF_CMAP):
    """ Draws an image of the data without shading
    """
    axes.imshow(data, cmap, interpolation=IMSHOW_INTERP, origin=IMSHOW_ORIGIN)
    axes.set_title('Data without shading')
    add_colorbar(fig, axes, cmap)
    #remove_ticks(axes)


def plot_mpl_intensity(fig, axes, terrain, cmap=plt.cm.gist_gray, 
                       azim=DEF_AZIMUTH, elev=DEF_ELEVATION, scale_terrain = DEF_SCALE):
    """ Shows the shading component calculated from the matplotlib algorithm
    """
    intensity = matplotlib_intensity(terrain, fix_atan_bug=True,  
                                     azimuth=azim, elevation=elev, 
                                     scale_terrain = scale_terrain)
    axes.set_title('MPL (azim={}, elev={}) (scale={})'.format(azim, elev, scale_terrain))
    axes.imshow(intensity, cmap, interpolation=IMSHOW_INTERP, origin=IMSHOW_ORIGIN)
    add_colorbar(fig, axes, cmap)
    #remove_ticks(axes)    


def plot_dot_intensity(fig, axes, terrain, cmap=plt.cm.gist_gray, 
                           azim=DEF_AZIMUTH, elev=DEF_ELEVATION):
    """ Shows the shading component calculated from the dot product of the light source and the
        surface numbers.
    """
    intensity = normalized_intensity(terrain, azimuth=azim, elevation=elev)
    axes.set_title('Dot (azim={}, elev={})'.format(azim, elev))
    axes.imshow(intensity, cmap, interpolation=IMSHOW_INTERP, origin=IMSHOW_ORIGIN)
    add_colorbar(fig, axes, cmap)
    #remove_ticks(axes)    


def generate_concentric_circles():
    x, y = np.mgrid[-5:5:0.05, -5:5:0.05] # 200 by 200
    data = np.sqrt(x ** 2 + y ** 2) + np.sin(x ** 2 + y ** 2)
    return data


def generate_hills_with_noise():
    _, _, data = axes3d.get_test_data(0.03)  # 200 by 200
    noise = 0.5 * np.random.randn(*data.shape) # unpack shape
    return -data + noise  


def main():

    if 0:
        terrain = generate_concentric_circles()
    else:
        terrain = generate_hills_with_noise()
        
    # Uncomment the line below to see Nans in the terrain
    #terrain[20:40, 30:50] = np.nan

    fig, axes_list = plt.subplots(2, 4, figsize=(20, 10))
    
    #azim = [0, 45, 90]
    #azim = [-45, 0, 45]
    #azim = [-90, 0, 90]
    #azim = [0, 90, 180]
    azim = [45, 90, 135]
    elev = 60
    
    plot_data(fig, axes_list[0, 0], terrain, plt.cm.cubehelix)
    plot_data(fig, axes_list[1, 0], terrain, plt.cm.cubehelix) # duplicate to fill space
    for idx in range(3):
        col = idx + 1
        plot_mpl_intensity(fig, axes_list[0, col], terrain, azim=azim[idx], elev=elev, scale_terrain = 1)
        plot_dot_intensity(fig, axes_list[1, col], terrain, azim=azim[idx], elev=elev)

    plt.show()

if __name__ == "__main__":
    main()
    if mpl.is_interactive() and  mpl.get_backend() == 'MacOSX':
        #raw_input('please press enter\n') # python 2
        input('please press enter\n')
        
        
    