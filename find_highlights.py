#!/usr/bin/python

import sys

from vipsCC import *

# make a black @size x @size image with a white circle of radius @radius at the
# centre
def make_circle_mask(size, radius):
    # this is a float mask with the origin at the corner 
    mask = VImage.VImage_create_fmask(size, size, 1, float(radius) / size, 
                                      0, 0, 0, 0)
    return mask.rotquad()

def gauss_blur(im, radius):
    mask = VMask.VIMask_gauss_sep(radius / 2.0, 0.2)
    return im.convsep(mask)

def search(avg_filename, pos, radius, image_filenames):
    avg = VImage.VImage(avg_filename)
    margin = 20
    left = int(pos.real - radius - margin)
    top = int(pos.imag - radius - margin)
    size = int(2 * (radius + margin))
    mask = make_circle_mask(size, radius)

    diffs = [VImage.VImage(i).subtract(avg) for i in image_filenames]
    crops = [i.extract_area(left, top, size, size) for i in diffs]
    blurs = [gauss_blur(i, 10) for i in crops]
    masked = [i.multiply(mask) for i in blurs]
    positions = [i.maxpos() + complex(left, top) - pos for i in masked]

    for i in range(0, len(positions)):
        x = positions[i].real
        y = positions[i].imag
        d = (x ** 2 + y ** 2) ** 0.5
        if d > radius:
            print '%s has a highlight at (%d, %d)' % (image_filenames[i], x, y)

    return positions

def find_vector(pos, r):
    x = pos.real
    y = pos.imag
    # distance to highlight
    d = (x ** 2 + y ** 2) ** 0.5
    # clip against radius ... we can't let it get bigger, but it might be
    # marginally due to rounding 
    if d > r:
        d = r
    # height of highlight 
    z = (r ** 2 - d ** 2) ** 0.5
    # normalise to get x/y/z unit vector
    return (x / r, y / r, z / r)

def write_lp(lp_filename, radius, image_filenames, positions):
    with open(lp_filename, 'w') as f:
        f.write('%d\n' % len(positions))
        for i in range(0, len(positions)):
            (x, y, z) = find_vector(positions[i], radius)
            f.write('%s\t%f %f %f\n' % (image_filenames[i], x, y, z))

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print 'usage: %s lp-filename avg-image cx cy radius images ... ' % sys.argv[0]
        sys.exit(1)

    lp_filename = sys.argv[1]
    avg_filename = sys.argv[2]
    pos = complex(int(sys.argv[3]), int(sys.argv[4]))
    radius = int(sys.argv[5])
    image_filenames = sys.argv[6:]

    positions = search(avg_filename, pos, radius, image_filenames)

    for i in range(0, len(positions)):
        print image_filenames[i], positions[i].real, positions[i].imag

    write_lp(lp_filename, radius, image_filenames, positions)

