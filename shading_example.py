import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

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
    
    # plot un-shaded and shaded images.
    plt.figure(figsize=(12, 5))
    plt.subplot(121)
    plt.imshow(z, cmap)
    plt.title('imshow')
    plt.xticks([])
    plt.yticks([])
    plt.subplot(122)
    plt.imshow(rgb)
    plt.title('imshow with shading')
    plt.xticks([])
    plt.yticks([])
    plt.show()

if __name__ == "__main__":
    main()
    raw_input('please press enter\n')
    