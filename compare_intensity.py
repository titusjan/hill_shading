""" Compares the newly implemented normalized_intensity function with the results of the old
    implementation that comes from m
    atplotlib
"""
from __future__ import print_function
from __future__ import division

import matplotlib.pyplot as plt
plt.ioff() 

from plotting import make_test_data
from plotting import plot_no_shading, plot_mpl_intensity, plot_dot_intensity

def main():

    #terrain = make_test_data('circles', noise_factor=0.0)
    terrain = make_test_data('hills', noise_factor=0.1)

    fig, axes_list = plt.subplots(2, 4, figsize=(20, 10))
    fig.tight_layout()
    
    azimuths = [45, 90, 135]
    elev = 50
    
    plot_no_shading(fig, axes_list[0, 0], terrain, plt.cm.cubehelix)
    axes_list[1, 0].set_axis_off()
    
    for idx, azim in enumerate(azimuths):
        col = idx + 1
        plot_mpl_intensity(fig, axes_list[0, col], terrain, azim=azim, elev=elev, scale_terrain = 1)
        plot_dot_intensity(fig, axes_list[1, col], terrain, azim=azim, elev=elev)

    plt.show()

if __name__ == "__main__":
    main()

        
        
    