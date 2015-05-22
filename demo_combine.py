""" Shows how to combine surface terrain with surface properties
"""
from __future__ import print_function
from __future__ import division

import matplotlib as mpl

mpl.interactive(False) 
import sys
import numpy as np
import matplotlib.pyplot as plt

from plotting import make_test_data
from plotting import draw
from hillshade import hill_shade, no_blending, INTENSITY_CMAP
from intensity import DEF_AZIMUTH, DEF_ELEVATION


def main():
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    fig.tight_layout()

    data = make_test_data('circles')
    terrain = 10 * make_test_data('hills', noise_factor=0.05)
    assert terrain.shape == data.shape, "{} != {}".format(terrain.shape, data.shape)
    print("min data: {}".format(np.min(data)))
    print("max data: {}".format(np.max(data)))

    cmap = plt.cm.get_cmap('bwr')
    cmap.set_bad('yellow')
    cmap.set_over('cyan')
    cmap.set_under('magenta')
         
    if ['--autoscale'] in sys.argv:
        print ("Auto scale legend")
        dnorm = mpl.colors.Normalize()
    else:
        dmin = 0
        dmax = 10
        print ("clip legend at ({}, {})".format(dmin, dmax))
        dnorm = mpl.colors.Normalize(vmin=dmin, vmax=dmax)
        
    # Don't auto scale the intensities, it gives the wrong impression
    inorm = mpl.colors.Normalize(vmin=0.0, vmax=1.0)
            
    azimuth = DEF_AZIMUTH 
    elevation = DEF_ELEVATION

    draw(ax[0, 0], cmap=plt.cm.gist_earth, title='Terrain height', 
         image_data = terrain)

    draw(ax[0, 1], cmap=INTENSITY_CMAP, norm=inorm, 
         title='Shaded terrain (azim = {}, elev = {})'.format(azimuth, elevation), 
         image_data = hill_shade(terrain, blend_function=no_blending, 
                                 azimuth=azimuth, elevation=elevation)) 

    draw(ax[1, 0], cmap=cmap, norm=dnorm, title='Surface properties', 
         image_data = data)
    
    draw(ax[1, 1], cmap=cmap, norm=dnorm, title='Shaded terrain with surface properties', 
         image_data = hill_shade(data, terrain=terrain,
                                 azimuth=azimuth, elevation=elevation, 
                                 cmap=cmap, norm=dnorm))
    plt.show()

if __name__ == "__main__":
    main()

        
        
    