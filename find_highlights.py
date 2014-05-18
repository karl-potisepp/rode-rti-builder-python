#!/usr/bin/python

import sys

from vipsCC import *

def gauss_blur(im, radius):
    mask = VMask.VIMask_gauss_sep(radius / 2.0, 0.2)
    return im.convsep(mask)

def search(avg_filename, pos, radius, image_filenames):
    avg = VImage.VImage(avg_filename)
    diffs = [VImage.VImage(i).subtract(avg) for i in image_filenames]

    margin = 20
    left = int(pos.real - radius - margin)
    top = int(pos.imag - radius - margin)
    size = int(2 * (radius + margin))
    crops = [i.extract_area(left, top, size, size) for i in diffs]
    blurs = [gauss_blur(i, 10) for i in crops]
    poses = [i.maxpos() for i in blurs]

    return [i + complex(left, top) - pos for i in poses]

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print 'usage: %s avg-image cx cy radius images ... ' % sys.argv[0]
        sys.exit(1)

    avg_filename = sys.argv[1]
    pos = complex(int(sys.argv[2]), int(sys.argv[3]))
    radius = int(sys.argv[4])
    image_filenames = sys.argv[5:]

    positions = search(avg_filename, pos, radius, image_filenames)

    for i in range(0, len(positions)):
        print image_filenames[i], positions[i].real, positions[i].imag

