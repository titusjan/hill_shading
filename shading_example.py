""" Tests various hill shading algorithms

Matplotlib shading:
    http://matplotlib.org/examples/pylab_examples/shading_example.html?highlight=codex%20shade

Ran Novitsky
    http://rnovitsky.blogspot.nl/2010/04/using-hillshade-image-as-intensity.html

For a list of colormaps:
    http://matplotlib.org/examples/color/colormaps_reference.html

TODO: look at
    (http://reference.wolfram.com/mathematica/ref/ReliefPlot.html)
    or Generic Mapping Tools (http://gmt.soest.hawaii.edu/)
    
    - Fix azimuth and elevation keywords
    
    - Clean up hill_shade_intensity
    - Allow hill_shade to accept separate data for the color
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
from matplotlib import cm
from matplotlib.colors import LightSource
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d

from novitsky import set_shade, hillshade
from pepshade import hill_shade, hill_shade_intensity

DEF_AZI = 210.0 # default azimuth angle in degrees
#DEF_AZI = 315.0 # default azimuth angle in degrees
DEF_ALT = 45.0  # default elevation angle in degrees
DEF_SCALE = 10.0
DEF_INTERP = 'nearest'
#DEF_INTERP = None

# see http://matplotlib.org/users/colormaps.html for choosing a good color map
#DEF_CMAP = plt.cm.rainbow
#DEF_CMAP = plt.cm.cool
#DEF_CMAP = plt.cm.cubehelix # doesn't work yet
#DEF_CMAP = plt.cm.hot
DEF_CMAP = plt.cm.bwr
#DEF_CMAP = plt.cm.gist_earth
    


def no_shading(fig, axes, data, cmap=DEF_CMAP, interpolation=DEF_INTERP):
    " Shows data without hill shading"

    image = axes.imshow(data, cmap, interpolation=interpolation)
    axes.set_title('No shading')
    axes.set_xticks([])
    axes.set_yticks([])
    
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    colorbar = fig.colorbar(image, cax=colorbar_axes, orientation='vertical')


def mpl_hill_shading(fig, axes, data, cmap=DEF_CMAP, 
                     azdeg=DEF_AZI, altdeg=DEF_ALT, 
                     interpolation=DEF_INTERP):
    " Shows data matplotlibs implementation of hill shading"
    ls = LightSource(azdeg=azdeg, altdeg=altdeg)
    rgb = ls.shade(data, cmap=cmap)
    
    norm = mpl.colors.Normalize(vmin=np.min(data), vmax=np.max(data))
    
    # Norm will not be used to normalize rgb in in the imshow() call but 
    # is used to normalize the color bar. An alternative is to use ColorbarBase
    # as is demonstrated in novitsky_hill_shading below
    image = axes.imshow(rgb, cmap, norm=norm, interpolation=interpolation)
    axes.set_title('Matplotlib hill shading')
    axes.set_xticks([])
    axes.set_yticks([])    
    
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    colorbar = fig.colorbar(image, cax=colorbar_axes, orientation='vertical')
    

def novitsky_hill_shading(fig, axes, data, terrain=None, cmap=DEF_CMAP, 
                          azdeg=DEF_AZI, altdeg=DEF_ALT, scale_terrain = DEF_SCALE,
                          interpolation=DEF_INTERP):
    " Shows data with hill shading by Ran Novitsky"

    norm = mpl.colors.Normalize(vmin=np.min(data), vmax=np.max(data))
    
    rgb = set_shade(data, cmap=cmap, azdeg=azdeg, altdeg=altdeg, scale_terrain = scale_terrain)
    image = axes.imshow(rgb, interpolation=interpolation)

    axes.set_title('Ran Novitsky hill shading')
    axes.set_xticks([])
    axes.set_yticks([])    
    
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    colorbar = mpl.colorbar.ColorbarBase(colorbar_axes, cmap=cmap, norm=norm, orientation='vertical')


def intensity(fig, axes, terrain, cmap=DEF_CMAP, 
              azdeg=DEF_AZI, altdeg=DEF_ALT, scale_terrain = DEF_SCALE,
              interpolation=DEF_INTERP):
    " Shows only the shading component of the shading by Ran Novitsky"
    # Intensity will always be between 0 and 1
    
    if 0:
        intensity = hillshade(terrain, azdeg=azdeg, altdeg=altdeg, scale_terrain = scale_terrain)
        axes.set_title('Ran Novitsky intensity')
    else:    
        intensity = hill_shade_intensity(terrain, azimuth=azdeg, elevation=altdeg, scale_terrain = scale_terrain)
        axes.set_title('Pepijn Kenter intensity')
    
    image = axes.imshow(intensity, cmap, interpolation=interpolation)
    axes.set_xticks([])
    axes.set_yticks([])    
    
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    colorbar = fig.colorbar(image, cax=colorbar_axes, orientation='vertical')


def kenter_hill_shading(fig, axes, data, terrain=None, cmap=DEF_CMAP, 
                        azdeg=DEF_AZI, altdeg=DEF_ALT, scale_terrain = DEF_SCALE, 
                        interpolation=DEF_INTERP):
    " Shows data with hill shading by Ran Novitsky"

    norm = mpl.colors.Normalize(vmin=np.min(data), vmax=np.max(data))
    
    rgb = hill_shade(data, terrain=terrain, 
                     azimuth=azdeg, elevation=altdeg, scale_terrain = scale_terrain, 
                     cmap=cmap, cnorm_fn=norm)
    image = axes.imshow(rgb, interpolation=interpolation)

    axes.set_title('Pepijn Kenter hill shading')
    axes.set_xticks([])
    axes.set_yticks([])    
    
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    colorbar = mpl.colorbar.ColorbarBase(colorbar_axes, cmap=cmap, norm=norm, orientation='vertical')

def generate_concentric_circles():
    x, y = np.mgrid[-5:5:0.05, -5:5:0.05] # 200 by 200
    data = np.sqrt(x ** 2 + y ** 2) + np.sin(x ** 2 + y ** 2)
    return data

def generate_hills_with_noise():
    _, _, data = axes3d.get_test_data(0.03)  # 200 by 200
    noise = 5 * np.random.randn(*data.shape) # unpack shape
    return -data + noise  


def main():

    if 0:
        data = generate_concentric_circles()
        terrain = generate_concentric_circles()
    else:
        data    = generate_hills_with_noise()
        terrain = generate_concentric_circles()
        
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)

    # Uncomment the line below to see Nans in the terrain
    #terrain[20:40, 30:50] = np.nan

    fig, axes_list = plt.subplots(2, 2, figsize=(10, 10))
    
    if 1:
        no_shading            (fig, axes_list[0, 0], terrain)
        mpl_hill_shading      (fig, axes_list[0, 1], terrain)
        novitsky_hill_shading (fig, axes_list[1, 0], data, terrain=terrain, scale_terrain = 0.01)
        kenter_hill_shading   (fig, axes_list[1, 1], data, terrain=terrain, scale_terrain = 5)
        #intensity             (fig, axes_list[1, 0], terrain, plt.cm.gist_gray, scale_terrain = 10)
    else:
        intensity   (fig, axes_list[0, 0], terrain, plt.cm.gist_gray, scale_terrain = 10)
        intensity   (fig, axes_list[0, 1], terrain, plt.cm.gist_gray, scale_terrain = 5)
        intensity   (fig, axes_list[1, 0], terrain, plt.cm.gist_gray, scale_terrain = 2)
        intensity   (fig, axes_list[1, 1], terrain, plt.cm.gist_gray, scale_terrain = 1000)

    plt.show()

if __name__ == "__main__":
    main()
    if mpl.is_interactive() and  mpl.get_backend() == 'MacOSX':
        raw_input('please press enter\n')
    