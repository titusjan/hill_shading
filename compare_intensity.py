""" Compares the newly implemented normalized_intensity function with the results of the old
    implementation that comes from m
    atplotlib
"""
from __future__ import print_function
from __future__ import division

import matplotlib.pyplot as plt
plt.ioff() 

from plotting import make_test_data, plot_no_shading, plot_mpl_intensity, plot_dot_intensity

def main():

    #terrain = make_test_data('circles', noise_factor=0.0)
    terrain = make_test_data('hills', noise_factor=0.1)

    fig, ax = plt.subplots(2, 4, figsize=(20, 10))
    fig.tight_layout()
    
    plot_no_shading(ax[0, 0], terrain, plt.cm.cubehelix)
    ax[1, 0].set_axis_off()
    
    azimuths = [45, 90, 135]
    elev = 50
    
    for idx, azim in enumerate(azimuths):
        col = idx + 1
        plot_mpl_intensity(ax[0, col], terrain, azim=azim, elev=elev, scale_terrain = 1)
        plot_dot_intensity(ax[1, col], terrain, azim=azim, elev=elev)

    plt.show()

if __name__ == "__main__":
    main()

        
        
    