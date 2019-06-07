# art-institute
Download high quality public domain (CC0) artworks from the Art Institute of Chicago

More information here: http://committodev.com/art-heist


todo:
- find out the maximum available concurrent connection, try to download 1 by 1 from mac for a range and do the same from the server
- there is a bug in the code that it failed to obtain the image URL for some of the pages, for example, 23936
- besides, 500 concureent threads are too many for download, the code is failing after tens of thousands of tries 