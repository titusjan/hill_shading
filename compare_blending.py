""" Compares the different methods of blending color
    Shows that the matplotlib and pegtop implementation rely heavily on the intensity of the
    color map and therefore give poor results when using a color map that has less 
    variation in intensity, such as the rainbow plot.
"""
from __future__ import print_function
from __future__ import division

import matplotlib as mpl

mpl.interactive(False) 

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

from plotting import make_test_data
from plotting import draw
from intensity import matplotlib_intensity
from hillshade import hill_shade, rgb_blending, hsv_blending, pegtop_blending 
from hillshade import DEF_AZIMUTH, DEF_ELEVATION


def main():

    if 1:
        data = make_test_data('circles', noise_factor=0.05)
        terrain = np.copy(data)
        #terrain = make_test_data('circles')
        cmap = plt.cm.rainbow
        cnorm = mpl.colors.Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data)) # color normalize function
        scale = 1
    else:
        # Shows that hsv-blending can give wrong results when combined wiht a color map that 
        # includes colors close to black or white (such as 'cubehelix'). Note the incorrect purple
        # spot where the data is close to zero.
        # The matploblib hill shading cannot have a different terrain and data so shows only data.
        data = make_test_data('hills', noise_factor=5)
        terrain = make_test_data('circles')
        cmap = plt.cm.cubehelix
        cnorm = mpl.colors.Normalize()
        scale = 10
        
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)
    # Uncomment the line below to see Nans in the terrain
    #terrain[20:40, 30:50] = np.nan

    print("min data: {}".format(np.min(data)))
    print("max data: {}".format(np.max(data)))

    fig, ax = plt.subplots(3, 2, figsize=(15, 10))
    fig.tight_layout()
    
    draw(ax[0, 0], cmap=cmap, title='No shading', 
         image_data = data)

    draw(ax[0, 1], cmap=plt.cm.gray, title='Matplotlib intensity', 
         image_data = matplotlib_intensity(terrain, scale_terrain = scale))

    ls = LightSource(azdeg=DEF_AZIMUTH, altdeg=DEF_ELEVATION)
    draw(ax[1, 0], cmap=cmap, norm=cnorm, title='Matplotlib hill shading', 
         image_data = ls.shade(data, cmap=cmap))
    
    draw(ax[1, 1], cmap=cmap, norm=cnorm, title='Pegtop blending', 
         image_data = hill_shade(data, terrain=terrain, scale_terrain = scale, 
                                 cmap=cmap, blend_function=pegtop_blending))
    
    draw(ax[2, 0], cmap=cmap, norm=cnorm, title='RGB blending', 
         image_data = hill_shade(data, terrain=terrain, scale_terrain = scale, 
                                 cmap=cmap, blend_function=rgb_blending))    
    
    draw(ax[2, 1], cmap=cmap, norm=cnorm, title='HSV blending', 
         image_data = hill_shade(data, terrain=terrain, scale_terrain = scale, 
                                 cmap=cmap, blend_function=hsv_blending))    

    plt.show()

if __name__ == "__main__":
    main()

        
        
    