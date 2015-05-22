""" Compares out  function with the results of the old
    implementation that comes from matplotlib
"""
from __future__ import print_function
from __future__ import division

import matplotlib.pyplot as plt
plt.ioff() 

import matplotlib as mpl
from plotting import make_test_data, draw
from hillshade import INTENSITY_CMAP
from intensity import mpl_surface_intensity, combined_intensities


def main():

    fig, ax = plt.subplots(3, 4, figsize=(15, 10))
    fig.tight_layout()
    
    #terrain = make_test_data('circles', noise_factor=0.0)
    terrain = make_test_data('hills', noise_factor=0.1)

    # Scale terrain. 
    terrain *= 5

    # Don't auto scale the intensities, it gives the wrong impression
    inorm = mpl.colors.Normalize(vmin=0.0, vmax=1.0)

    # Draw the terrain as color map
    draw(ax[0, 0], cmap=plt.cm.gist_earth, title='No shading', ticks=True,  
         image_data = terrain)
    
    # Draw empty space
    ax[1, 0].set_axis_off()
    ax[2, 0].set_axis_off()
    
    cmap = INTENSITY_CMAP
    azim0_is_east = True # If true, azimuth 0 will correspond to east just as in our implementation
    azimuths = [45, 90, 135]
    #elev = 50
    
    # At low elevation you will see still noise bumps in places that are completely in the shadows.
    # This may seem nice but it is incorrect.
    elev = 15 
    
    for idx, azim in enumerate(azimuths):
        col = idx + 1
        
        draw(ax[0, col], cmap=cmap, norm=inorm, 
             title="MPL normalized (azim = {}, elev = {})".format(azim, elev),  
             image_data = mpl_surface_intensity(terrain, azimuth=azim, elevation=elev, 
                                               azim0_is_east=azim0_is_east, normalize=True))
           
        draw(ax[1, col], cmap=cmap, norm=inorm, 
             title="MPL (azim = {}, elev = {})".format(azim, elev), 
             image_data = mpl_surface_intensity(terrain, azimuth=azim, elevation=elev, 
                                               azim0_is_east=azim0_is_east, normalize=False))   
        
        draw(ax[2, col], cmap=cmap, norm=inorm, 
             title="Diffuse (azim = {}, elev = {})".format(azim, elev), 
             image_data = combined_intensities(terrain, azimuth=azim, elevation=elev))

    plt.show()

if __name__ == "__main__":
    main()

        
        
    