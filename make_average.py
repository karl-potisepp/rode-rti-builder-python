#!/usr/bin/python

import sys

from vipsCC import *

def make_average(output_filename, image_filenames):
    images = [VImage.VImage(i) for i in image_filenames]
    total = images[0]
    for i in images:
        total = total.add(i)
    average = total.lin(1.0 / len(image_filenames), 0)

    average.write(output_filename)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: %s output-image images ... ' % sys.argv[0]
        sys.exit(1)

    output_filename = sys.argv[1]
    image_filenames = sys.argv[2:]

    make_average(output_filename, image_filenames)

