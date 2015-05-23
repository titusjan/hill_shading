""" Shows how to use multiple light sources in one shading.

    Draws four images. Three with one lamp illuminating the scene (north east, north west, south),
    and one image where all three light sources together illuminate the scene.
    
    To only show the intensities, call the script with the --bw argument.
"""
from __future__ import print_function
from __future__ import division

import sys
import matplotlib as mpl

mpl.interactive(False) 
import matplotlib.pyplot as plt

from plotting import make_test_data
from plotting import draw
from hillshade import hill_shade, no_blending, rgb_blending, INTENSITY_CMAP


def main():
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    fig.tight_layout()

    data = -25 * make_test_data('hills', noise_factor=0.025) # secretly swapped :-)
    #data = -25 * make_test_data('circles', noise_factor=0.025) # secretly swapped :-)
    terrain = data
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)
    
    if '--bw' in sys.argv:
        # Only intensities
        blend_function = no_blending
        cmap=INTENSITY_CMAP
        
        # Don't auto scale the intensities, it gives the wrong impression
        norm = mpl.colors.Normalize(vmin=0.0, vmax=1.0)
    else:
        blend_function = rgb_blending
        cmap = plt.cm.get_cmap('gist_earth')
        norm = mpl.colors.Normalize()
    
    azimuths = [45, 135, 270] # North-East, North-West and South.
    elevations = [60] * len(azimuths)
    
    # Draw shading by separate light sources
    for idx, (azim, elev) in enumerate(zip(azimuths, elevations)):
        row = idx // 2
        col = idx % 2
        draw(ax[row, col], cmap=cmap, norm=norm, 
             title='azim = {}, elev = {}'.format(azim, elev), 
             image_data = hill_shade(data, terrain, blend_function=blend_function, 
                                     ambient_weight = 1, lamp_weight = 5,
                                     cmap=cmap, norm=norm,  
                                     azimuth=azim, elevation=elev))
    
    # Draw shading by all light sources combined 
    draw(ax[1, 1], cmap=cmap, norm=norm, 
         title='combined'.format(azim, elev), 
         image_data = hill_shade(data, terrain, blend_function=blend_function, 
                                 ambient_weight = 1, lamp_weight = [5, 5, 5],
                                 cmap=cmap, norm=norm,  
                                 azimuth=azimuths, elevation=elevations))

    plt.show()

if __name__ == "__main__":
    main()

        
        
    