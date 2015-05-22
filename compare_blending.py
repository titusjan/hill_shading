""" Compares the different methods of blending color
    Shows that the matplotlib and pegtop implementation rely heavily on the intensity of the
    color map and therefore give poor results when using a color map that has less 
    variation in intensity, such as the rainbow plot.
"""
from __future__ import print_function
from __future__ import division

import matplotlib as mpl
mpl.interactive(False) 

import sys
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

from plotting import make_test_data, draw, mpl_hill_shade
from intensity import mpl_surface_intensity
from hillshade import hsv_blending, pegtop_blending, rgb_blending, DEF_AZIMUTH, DEF_ELEVATION

def main():

    fig, ax = plt.subplots(3, 2, figsize=(7, 10))
    fig.tight_layout()    

    if 1:
        data = make_test_data('circles', noise_factor=0.05) 
        terrain = data * 2
    else:
        data = make_test_data('hills') * -1
        terrain = make_test_data('circles', noise_factor=0.05) * 2
        
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)

    if len(sys.argv) > 1:
        cmap_name = sys.argv[1]
    else:
        #cmap_name = 'copper' # from http://matplotlib.org/examples/pylab_examples/shading_example.html?highlight=codex%20shade
        #cmap_name = 'gist_earth' # works reasonably fine with all of them
        cmap_name = 'cubehelix'  # shows that HSV blending does not work were color is black
        #cmap_name = 'rainbow'    # shows that mpl & pegtop don't work when there is no increasing intensity
        #cmap_name = 'Paired_r'     # is nice to inspect when the data is different from the terrain
        
    print ("Using colormap: {!r}".format(cmap_name))
    cmap = plt.cm.get_cmap(cmap_name)
    cmap.set_bad('red')
    cmap.set_over('red')
    cmap.set_under('red')
    
    cnorm = mpl.colors.Normalize() 
    
    draw(ax[0, 0], cmap=cmap, title='No shading', 
         image_data = data)

    draw(ax[0, 1], cmap=plt.cm.gray, title='Matplotlib intensity', 
         image_data = mpl_surface_intensity(terrain))

    ls = LightSource(azdeg=DEF_AZIMUTH, altdeg=DEF_ELEVATION)
    draw(ax[1, 0], cmap=cmap, norm=cnorm, title='Matplotlib hill shading', 
         image_data = ls.shade(data, cmap=cmap))
    
    draw(ax[1, 1], cmap=cmap, norm=cnorm, title='Pegtop blending', 
         image_data = mpl_hill_shade(data, terrain=terrain,  
                                     cmap=cmap, blend_function=pegtop_blending))
    
    draw(ax[2, 0], cmap=cmap, norm=cnorm, title='RGB blending', 
         image_data = mpl_hill_shade(data, terrain=terrain, 
                                     cmap=cmap, blend_function=rgb_blending))    
    
    draw(ax[2, 1], cmap=cmap, norm=cnorm, title='HSV blending', 
         image_data = mpl_hill_shade(data, terrain=terrain, 
                                     cmap=cmap, blend_function=hsv_blending))    

    plt.show()

if __name__ == "__main__":
    main()

        
        
    