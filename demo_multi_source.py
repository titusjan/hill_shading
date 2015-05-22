""" Shows how to use multiple light sources.
"""
from __future__ import print_function
from __future__ import division

import matplotlib as mpl

mpl.interactive(False) 
import matplotlib.pyplot as plt

from plotting import make_test_data
from plotting import draw
from hillshade import hill_shade, no_blending, INTENSITY_CMAP
from intensity import DEF_AZIMUTH, DEF_ELEVATION


def main():
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    fig.tight_layout()

    data = make_test_data('circles')
    terrain = 5 * make_test_data('hills', noise_factor=0.1)
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)

    # Don't auto scale the intensities, it gives the wrong impression
    inorm = mpl.colors.Normalize(vmin=0.0, vmax=1.0)
    
    azimuths = [45, 135, 270]
    elevations = [DEF_ELEVATION] * len(azimuths)
    
    # Draw shading by separate light sources
    for idx, (azim, elev) in enumerate(zip(azimuths, elevations)):
        row = idx // 2
        col = idx % 2
        draw(ax[row, col], cmap=INTENSITY_CMAP, norm=inorm, 
             title='azim = {}, elev = {}'.format(azim, elev), 
             image_data = hill_shade(terrain, blend_function=no_blending, 
                                     azimuth=azim, elevation=elev))
    
    # Draw shading by all light sources combined 
    draw(ax[1, 1], cmap=INTENSITY_CMAP, norm=inorm, 
         title='combined'.format(azim, elev), 
         image_data = hill_shade(terrain, blend_function=no_blending, 
                                 ambient_weight = 0.15, lamp_weight = [1, 1, 1], 
                                 azimuth=azimuths, elevation=elevations))

    plt.show()

if __name__ == "__main__":
    main()

        
        
    