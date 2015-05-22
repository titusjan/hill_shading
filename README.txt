Contains a Hill Shading implementation for Matplotlib.

The hill_shade function can be found in the hillshade.py module. The intensity.py module contains 
functions for calculating the intensity as it falls on a terrain/surface. The rest of the files is 
for plotting demos. 

There is no installation procedure, just copy what you need into your code.

This software is released under the MIT license.

Matplotlib hill shading:
    http://matplotlib.org/examples/pylab_examples/shading_example.html?highlight=codex%20shade

Pegtop shading:
    http://rnovitsky.blogspot.nl/2010/04/using-hillshade-image-as-intensity.html

TODO:
	Make it work with NaNs and Masked arrays. It currently does not work with Nans since the
	blending works based on RBG values where the 'is_bad' color will just be blended.

2015-05-22, Pepijn Kenter.
