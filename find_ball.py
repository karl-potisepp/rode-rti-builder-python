#!/usr/bin/python

import sys

from vipsCC import *

def bandsplit(im):
    return [im.extract_band(i) for i in range(0, im.Bands())]

def max_index(l):
    m = l[0]
    i = 0
    for j in range(1, len(l)):
        if l[j] > m:
            m = l[j]
            i = j

    return i

def find_circle(im, scale, min_radius, max_radius):
    hough = im.hough_circle(scale, min_radius, max_radius)
    pos = hough.maxpos()
    point = hough.extract_area(int(pos.real), int(pos.imag), 1, 1)
    maxp = max_index([i.avg() for i in bandsplit(point)])

    radius = maxp * scale + min_radius
    pos = pos * scale

    return (pos, radius)

def sobel(im):
    mask = VMask.VIMask(3, 3, 1, 128,
                        [ 1,  2,  1,
                          0,  0,  0,
                         -1, -2, -1])
    maskr = mask.rotate90()
    a = im.conv(mask).lin(1, -128).abs()
    b = im.conv(maskr).lin(1, -128).abs()
    return a.add(b)

def search(filename, left, top, width, height):
    source = VImage.VImage(filename)

    # prepare image  ... 3x3 median of green band
    crop = source.extract_area(left, top, width, height)
    crop = crop.extract_band(1)
    crop = crop.rank(3, 3, 4)

    # find edges
    edge = sobel(crop).more(50)

    # first hough pass ... coarse search for circles in the range 70 .. 200
    (pos, radius) = find_circle(edge, 5, 70, 200)

    # extract approximate area
    margin = 20
    left2 = int(pos.real - radius - margin)
    top2 = int(pos.imag - radius - margin)
    size = 2 * (radius + margin)
    edge = edge.extract_area(left2, top2, size, size)

    # second hough pass ... fine search
    (pos, radius) = find_circle(edge, 1, radius - 10, radius + 10)
    pos = pos + complex(left2, top2)

    pos = pos + complex(left, top)

    return (pos, radius)

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print 'usage: %s input-image left top width height' % sys.argv[0]
        sys.exit(1)

    filename = sys.argv[1]
    left = int(sys.argv[2])
    top = int(sys.argv[3])
    width = int(sys.argv[4])
    height = int(sys.argv[5])

    (pos, radius) = search(filename, left, top, width, height)

    print pos.real, pos.imag
    print radius

