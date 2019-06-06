import requests 
import bs4 
import os
import urllib
import re

MAX_FILE_DOWNLOAD_COUNT = 1

file_downloaded_count = 0

for work in range(93000, 92800, -1):

    if file_downloaded_count >= MAX_FILE_DOWNLOAD_COUNT:
        break

    urlbase = 'https://www.artic.edu/artworks/'
    url = urlbase + str(work)
    print(url)

    res = requests.get(url)
    try:
        res.raise_for_status()

        soup = bs4.BeautifulSoup(res.text, 'lxml')

        print(soup)

        item = soup.find('div', class_='m-article-header__img-container')

        #find the license
        imglicense = soup.find('a', class_="m-article-header__img-credit")
        if imglicense:
            imglic = imglicense.text
            cleanlic = imglic.strip()

            if cleanlic == "CC0 Public Domain Designation":
        
                #title
                titletag = soup.find('h1', class_='sr-only')
                title = titletag.text
                print(title)

                #artist
                #TODO come back and do this right
                #artist = soup.find("data-gtm-event")
                #print(artist)    

                #set or create a folder based on art style
                mydirectory = soup.find(itemprop="provider").get("content")
                os.makedirs(mydirectory, exist_ok=True)
                print(mydirectory)

                try: 
                    item.img.get("data-iiifid")
                    imglink = item.img.get("data-iiifid")
                    fulllink = imglink + '/full/4000,/0/default.jpg'

                    #rename the file with the title and artist
                    filename = title + ' -- ' + str(work) + '.jpg'
                    #filename = title + '.jpg'
                    print(filename)

                    #download the file
                    print('Downloading image %s...' % (fulllink))
                    res = requests.get(fulllink)
                    res.raise_for_status()

                    #save the file
                    imageFile = open(os.path.join(mydirectory, os.path.basename(filename)), 'wb')
                    for chunk in res.iter_content(1000000):
                        imageFile.write(chunk)
                    imageFile.close()

                    with open("log.txt", "a") as f:
                        f.write(str(work) + "|" + title +   "\n")

                    file_downloaded_count += 1

                except:
                    with open("log.txt", "a") as f:
                        f.write(str(work) + "| IMAGE UNAVAILABLE \n")
    except:
        with open("log.txt", "a") as f:
                f.write(str(work) + "| URL UNAVAILABLE \n")