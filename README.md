rode-rti-builder-python
=======================

This is a proof-of-concept Python utility to process RTI input made as during the hackathon of the Rode Imaging Event at Niguliste Church in Tallinn (May 17-18 2014).  

Requirements:
* Python 2.7
* PyQt5
* patience

What works:
* selecting the input folder and searching it for JPEG/TIFF files
* calculating the average out of all the input images
* selecting the area containing the ball on the average image and calculating the x, y, width and height of the bounding box

What doesn't:
* locating the ball using bounding box info
* running the RTI processing algorithm

Rode Imaging Event: http://www.nigulistemuuseum.ee/en/niguliste-exhibitions/on-view/rode-imaging-event/

Reflectance Transformation Imaging (RTI): http://culturalheritageimaging.org/Technologies/RTI/
