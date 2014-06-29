import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

from mpl_toolkits.axes_grid1 import make_axes_locatable

# From:
# http://matplotlib.org/examples/pylab_examples/shading_example.html?highlight=codex%20shade

# Look at: 
# http://rnovitsky.blogspot.nl/2010/04/using-hillshade-image-as-intensity.html

# example showing how to make shaded relief plots
# like Mathematica
# (http://reference.wolfram.com/mathematica/ref/ReliefPlot.html)
# or Generic Mapping Tools
# (http://gmt.soest.hawaii.edu/gmt/doc/gmt/html/GMT_Docs/node145.html)


def main():
    # test data
    x, y = np.mgrid[-5:5:0.05, -5:5:0.05]
    z = np.sqrt(x ** 2 + y ** 2) + np.sin(x ** 2 + y ** 2)
    
    # create light source object.
    ls = LightSource(azdeg=0, altdeg=65)
    
    # shade data, creating an rgb array.
    cmap = plt.cm.rainbow
    rgb = ls.shade(z, cmap=cmap)
    
    fig, axes_list = plt.subplots(1, 2, figsize=(12, 5))
    
    # No hill shading
    axes = axes_list[0]
    image = axes.imshow(z, cmap)
    axes.set_title('imshow')
    axes.set_xticks([])
    axes.set_yticks([])
    
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    colorbar = fig.colorbar(image, cax=colorbar_axes, orientation='vertical')
        
    # Matplotlib default hill shading
    axes = axes_list[1]
    image = axes.imshow(rgb)
    axes.set_title('imshow with shading')
    axes.set_xticks([])
    axes.set_yticks([])    
    
    divider = make_axes_locatable(axes)    
    colorbar_axes = divider.append_axes('right', size="5%", pad=0.25, add_to_figure=True)
    colorbar = fig.colorbar(image, cax=colorbar_axes, orientation='vertical')
    
    fig.show()

if __name__ == "__main__":
    main()
    raw_input('please press enter\n')
    