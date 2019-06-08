import requests 
import bs4 
import os
import urllib
import re
import multiprocessing
import tqdm

from utility import *

class AIC_SCRAPPER():
    def __init__(self, MAX_FILE_DOWNLOAD_COUNT=200, ARTWORK_ID_START = 1, ARTWORK_ID_END = 100,
                NUM_THREADS = 8, MAXIMUM_CHAR_IN_FILENAME = 250, CHAR_TO_KEEP_IN_END_OF_FILENAME = 20,
                CC0_LICENSE_ONLY = False, SKIP_EXISTED_FILE=True, DOWNLOAD_DIR = 'downloads/',
                VERBOSE_LEVEL = 1):
        
        self.MAX_FILE_DOWNLOAD_COUNT = MAX_FILE_DOWNLOAD_COUNT
        self.ARTWORK_ID_START = ARTWORK_ID_START
        self.ARTWORK_ID_END = ARTWORK_ID_END
        self.NUM_THREADS = NUM_THREADS
        self.MAXIMUM_CHAR_IN_FILENAME = MAXIMUM_CHAR_IN_FILENAME
        self.CHAR_TO_KEEP_IN_END_OF_FILENAME = CHAR_TO_KEEP_IN_END_OF_FILENAME
        self.CC0_LICENSE_ONLY = CC0_LICENSE_ONLY
        self.SKIP_EXISTED_FILE = SKIP_EXISTED_FILE
        self.DOWNLOAD_DIR = DOWNLOAD_DIR
        self.VERBOSE_LEVEL = VERBOSE_LEVEL

        if self.ARTWORK_ID_START > self.ARTWORK_ID_END:
            self.ARTWORK_ID_START, self.ARTWORK_ID_END = self.ARTWORK_ID_END, self.ARTWORK_ID_START
            
    def make_artwork_url(self, artwork_id):
        urlbase = 'https://www.artic.edu/artworks/'
        url = urlbase + str(artwork_id)
        if self.VERBOSE_LEVEL > 1:
            print(url)
        return url
            
    def inquiry_by_id(self, artwork_id):
        
        
        
        url = self.make_artwork_url(artwork_id)
        res = requests.get(url)
        status_code = res.status_code
        if self.VERBOSE_LEVEL > 1:
            print("%d|: %d"%(artwork_id, status_code))

        return status_code
        
    def download_by_id(self, artwork_id):
    
#         print("Search Progress: %d/%d, artwork id: %d"%(artwork_id-self.ARTWORK_ID_START+1, self.ARTWORK_ID_END-self.ARTWORK_ID_START, artwork_id))

        url = self.make_artwork_url(artwork_id)
        res = requests.get(url)
        try:
            res.raise_for_status()

            soup = bs4.BeautifulSoup(res.text, 'lxml')

    #         print(soup)

            item = soup.find('div', class_='m-article-header__img-container')

            #find the license
            imglicense = soup.find('a', class_="m-article-header__img-credit")

            if self.CC0_LICENSE_ONLY and imglicense:
                imglic = imglicense.text
                cleanlic = imglic.strip()
                if cleanlic != "CC0 Public Domain Designation":
                    return
            else:
                #title
                titletag = soup.find('h1', class_='sr-only')
                title = titletag.text
                if self.VERBOSE_LEVEL > 1:
                    print(title)

                #artist
                try:
                    artist = soup.find("dd", attrs = {'itemprop' : 'creator'}).find("span").find("a").next
                except:
                    artist = 'UnknownArtist'
                if self.VERBOSE_LEVEL > 1:
                    print(artist)    

                #style
                try:
                    style = soup.find(itemprop="provider").get("content")
                except:
                    style = 'None'
                if self.VERBOSE_LEVEL > 1:
                    print(style)

                #origin
                try:
                    origin = soup.find("dd", attrs = {'itemprop' : 'locationCreated'}).find("span").next
                # origin = soup.find(itemprop="locationCreated").get("content")
                except:
                    origin = ''
                if self.VERBOSE_LEVEL > 1:
                    print(origin)

                # date
                try: 
                    date = soup.find("p", attrs = {'class' : 'title f-secondary o-article__inline-header-display'}).next
                except:
                    try:
                        date = soup.find("dd", attrs = {'itemprop' : 'dateCreated'}).find("a").next
                    except:
                        date = ''
                date=date.replace("/",'-')
                if self.VERBOSE_LEVEL > 1:
                    print(date)

                # reference number
                try:
                    refidx = -1
                    refnum = soup.findAll('dd')[refidx].find("span").next
                    while check_any_alpha(refnum):
                        refidx -=1
                        refnum = soup.findAll('dd')[refidx].find("span").next
                except:
                    refnum = ''
                if self.VERBOSE_LEVEL > 1:
                    print(refnum)

                # make the directory 
                mydirectory = os.path.join(self.DOWNLOAD_DIR, style, artist)
                # soup.find(itemprop="provider").get("content")
                os.makedirs(mydirectory, exist_ok=True)
                print(mydirectory)

                # make the filename
                attr = "(%s)-%s[%s](%s).jpg"%(date,artist,style, refnum)
                if self.VERBOSE_LEVEL > 1:
                    print(attr)
                filename = title+attr
                if self.VERBOSE_LEVEL > 1:
                    print(filename)
                filenamelength = len(filename)
                print("filenamelength:%s"%filenamelength)
                if filenamelength >= self.MAXIMUM_CHAR_IN_FILENAME:
                    title_available_length = self.MAXIMUM_CHAR_IN_FILENAME - len(attr)
                    title_cut = title[:title_available_length-self.CHAR_TO_KEEP_IN_END_OF_FILENAME]+'...'+title[-self.CHAR_TO_KEEP_IN_END_OF_FILENAME:] 
                    filename = title_cut+attr
                    if self.VERBOSE_LEVEL > 1:
                        print("After Cut:")
                filename = filename.replace("/","-")
                if self.VERBOSE_LEVEL > 0:
                    print(filename)

                if self.SKIP_EXISTED_FILE and os.path.isfile(os.path.join(mydirectory, os.path.basename(filename))):
                    with open("log.txt", "a") as f:
                        f.write(str(artwork_id) + "|" + " FILE EXISTED: " + filename +   "\n")
                    return
                try: 
                    print("Try to download:")
                    item.img.get("data-iiifid")
                    imglink = item.img.get("data-iiifid")
                    fulllink = imglink + '/full/4000,/0/default.jpg'

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
                        f.write(str(artwork_id) + "|"+ " NEW FILE: " + filename +   "\n")

                    if self.VERBOSE_LEVEL > 1:
                        print("Downloaded")

                    return

                except:
                    with open("log.txt", "a") as f:
                        f.write(str(artwork_id) + "| IMAGE UNAVAILABLE \n")
        except Exception as e:
            print (e)
            with open("log.txt", "a") as f:
                    f.write(str(artwork_id) + "| URL UNAVAILABLE \n")
                    
    def download_in_id_range(self):
        
        work_id_list = [x for x in range(self.ARTWORK_ID_START, self.ARTWORK_ID_END, 1)]

        print("Current search range: ", self.ARTWORK_ID_START, '-', self.ARTWORK_ID_END)

        pool = multiprocessing.Pool(processes=self.NUM_THREADS) #use 5 processes to download the data

        for _ in tqdm.tqdm(pool.imap_unordered(self.download_by_id, work_id_list), total=len(work_id_list)):
            pass

        print("Script finished.")
        print("The designed search range was: ", self.ARTWORK_ID_START, '-', self.ARTWORK_ID_END)
        
    def check_url_avails_in_range(self):

        work_id_list = [x for x in range(self.ARTWORK_ID_START, self.ARTWORK_ID_END, 1)]

        print("Current inquiry range: ", self.ARTWORK_ID_START, '-', self.ARTWORK_ID_END)

        pool = multiprocessing.Pool(processes=self.NUM_THREADS) #use 5 processes to download the data

        for _ in tqdm.tqdm(pool.imap_unordered(self.inquiry_by_id, work_id_list), total=len(work_id_list)):
            pass
        


