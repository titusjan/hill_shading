#!/bin/env python

# From: http://rnovitsky.blogspot.nl/2010/04/using-hillshade-image-as-intensity.html
from __future__ import print_function
from __future__ import division

from pylab import *

def set_shade(a, intensity=None, cmap=cm.jet, scale_terrain=10.0, azdeg=165.0, altdeg=45.0):
    """ sets shading for data array based on intensity layer
        or the data's value itself.

        inputs:
          a - a 2-d array or masked array
          intensity - a 2-d array of same size as a (no chack on that)
                            representing the intensity layer. if none is given
                            the data itself is used after getting the hillshade values
                            see hillshade for more details.
          cmap - a colormap (e.g matplotlib.colors.LinearSegmentedColormap
                      instance)
          scale_terrain,azdeg,altdeg - parameters for hilshade function see there for
                      more details
        output:
          rgb - an rgb set of the Pegtop soft light composition of the data and 
                   intensity can be used as input for imshow()
        based on ImageMagick's Pegtop_light:
        http://www.imagemagick.org/Usage/compose/#pegtoplight
    """
    if intensity is None:
        # hilshading the data
        intensity = hillshade(a, scale_terrain=10.0, azdeg=165.0, altdeg=45.0)
    else:
        # or normalize the intensity
        intensity = (intensity - intensity.min()) / \
            (intensity.max() - intensity.min())
            
    # get rgb of normalized data based on cmap
    rgb = cmap((a - a.min()) / float(a.max() - a.min()))[:, :, :3]
    
    # form an rgb eqvivalent of intensity
    d = intensity.repeat(3).reshape(rgb.shape)
    
    # simulate illumination based on pegtop algorithm.
    rgb = 2 * d * rgb + (rgb ** 2) * (1 - 2 * d)
    return rgb


def hillshade(data, scale_terrain=10.0, azdeg=165.0, altdeg=45.0):
    """ convert data to hillshade based on matplotlib.colors.LightSource class.
      input:
           data - a 2-d array of data
           scale_terrain - scaling value of the data. higher number = lower gradient
           azdeg - where the light comes from: 0 south ; 90 east ; 180 north ;
                        270 west
           altdeg - where the light comes from: 0 horison ; 90 zenith
      output: a 2-d array of normalized hilshade
    """
    # convert alt, az to radians
    az = azdeg * pi / 180.0
    alt = altdeg * pi / 180.0
    # gradient in x and y directions
    dx, dy = gradient(data / float(scale_terrain))
    slope = 0.5 * pi - arctan(hypot(dx, dy))
    aspect = arctan2(dx, dy)
    intensity = sin(alt) * sin(slope) + cos(alt) * \
        cos(slope) * cos(-az - aspect - 0.5 * pi)
    intensity = (intensity - intensity.min()) / \
        (intensity.max() - intensity.min())
    return intensity
