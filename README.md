# art-institute
Download high quality public domain (CC0) artworks from the Art Institute of Chicago

More information here: http://committodev.com/art-heist


todo:
- find out the maximum available concurrent connection, try to download 1 by 1 from mac for a range and do the same from the server
- there is no bug but just too many open connectionss
- besides, 500 concureent threads are too many for download, the code is failing after tens of thousands of tries 


- it seems that the webiste is equipped with an anti-scrapepr technology. I need to write somescripts to anti such technology

I found there are many url that ar enot realiable? 
What I'm think now is I want to split the whole scrapper into two parts: the scraper-into-sql and sql-to-download parts. In this way, we will have a much easier control ... well not really , think about how the youtube-dl handles the archived ones. One thing I can try is to put the artwork_id into the file name, then index the whole folder before the scrapper actually starts to work. 
In this way, we don't need to maintai a extra database for its metadata.  


The skip existed file function need to be reworked