
# coding: utf-8

# # search by id

# In[1]:


import requests 
import bs4 
import os
import urllib
import re
import multiprocessing

# MAX_FILE_DOWNLOAD_COUNT = 200
ARTWORK_ID_START = 120000
ARTWORK_ID_END = ARTWORK_ID_START + 1000

NUM_THREADS = 5

MAXIMUM_CHAR_IN_FILENAME = 250
CHAR_TO_KEEP_IN_END_OF_FILENAME = 20
CC0_LICENSE_ONLY = False
SKIP_EXISTED_FILE = True
DOWNLOAD_DIR = 'downloads-120k-121k-5/'

VERBOSE_LEVEL = 1


# In[2]:


if ARTWORK_ID_START > ARTWORK_ID_END:
    ARTWORK_ID_START, ARTWORK_ID_END = ARTWORK_ID_END, ARTWORK_ID_START


# In[3]:


# the idel filename:
# title(year)-artist[style][origin]-(referencnumber).jpg

# restrict the length of title so the entire line is less than 255
# within title, if shorten is needed, keep the last 20 char and the rest starting from the start

# the folder structure:
# /downloads/style/artist/file.jpg


# In[4]:


def check_any_alpha(string):
    for c in string:
        if c.isalpha():
            return True
    return False


# In[5]:


def download_by_id(artwork_id):
    
    print("Search Progress: %d/%d, artwork id: %d"%(artwork_id-ARTWORK_ID_START+1, ARTWORK_ID_END-ARTWORK_ID_START, artwork_id))
    
    urlbase = 'https://www.artic.edu/artworks/'
    url = urlbase + str(artwork_id)
    print(url)

    res = requests.get(url)
    try:
        res.raise_for_status()

        soup = bs4.BeautifulSoup(res.text, 'lxml')

#         print(soup)

        item = soup.find('div', class_='m-article-header__img-container')

        #find the license
        imglicense = soup.find('a', class_="m-article-header__img-credit")
        
        if CC0_LICENSE_ONLY and imglicense:
            imglic = imglicense.text
            cleanlic = imglic.strip()
            if cleanlic != "CC0 Public Domain Designation":
                return
        else:
            #title
            titletag = soup.find('h1', class_='sr-only')
            title = titletag.text
            if VERBOSE_LEVEL > 1:
                print(title)

            #artist
            try:
                artist = soup.find("dd", attrs = {'itemprop' : 'creator'}).find("span").find("a").next
            except:
                artist = 'UnknownArtist'
            if VERBOSE_LEVEL > 1:
                print(artist)    

            #style
            try:
                style = soup.find(itemprop="provider").get("content")
            except:
                style = 'None'
            if VERBOSE_LEVEL > 1:
                print(style)

            #origin
            try:
                origin = soup.find("dd", attrs = {'itemprop' : 'locationCreated'}).find("span").next
            # origin = soup.find(itemprop="locationCreated").get("content")
            except:
                origin = ''
            if VERBOSE_LEVEL > 1:
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
            if VERBOSE_LEVEL > 1:
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
            if VERBOSE_LEVEL > 1:
                print(refnum)

            # make the directory 
            mydirectory = os.path.join(DOWNLOAD_DIR, style, artist)
            # soup.find(itemprop="provider").get("content")
            os.makedirs(mydirectory, exist_ok=True)
            print(mydirectory)

            # make the filename
            attr = "(%s)-%s[%s](%s).jpg"%(date,artist,style, refnum)
            if VERBOSE_LEVEL > 1:
                print(attr)
            filename = title+attr
            if VERBOSE_LEVEL > 1:
                print(filename)
            filenamelength = len(filename)
            print("filenamelength:%s"%filenamelength)
            if filenamelength >= MAXIMUM_CHAR_IN_FILENAME:
                title_available_length = MAXIMUM_CHAR_IN_FILENAME - len(attr)
                title_cut = title[:title_available_length-CHAR_TO_KEEP_IN_END_OF_FILENAME]+'...'+title[-CHAR_TO_KEEP_IN_END_OF_FILENAME:] 
                filename = title_cut+attr
                if VERBOSE_LEVEL > 1:
                    print("After Cut:")
            filename = filename.replace("/","-")
            if VERBOSE_LEVEL > 0:
                print(filename)

            if SKIP_EXISTED_FILE and os.path.isfile(os.path.join(mydirectory, os.path.basename(filename))):
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

                if VERBOSE_LEVEL > 1:
                    print("Downloaded")
                    
                return

            except:
                with open("log.txt", "a") as f:
                    f.write(str(artwork_id) + "| IMAGE UNAVAILABLE \n")
    except Exception as e:
        print (e)
        with open("log.txt", "a") as f:
                f.write(str(artwork_id) + "| URL UNAVAILABLE \n")


# In[7]:


import tqdm


# In[8]:


work_id_list = [x for x in range(ARTWORK_ID_START, ARTWORK_ID_END, 1)]

print("Current search range: ", ARTWORK_ID_START, '-', ARTWORK_ID_END)

pool = multiprocessing.Pool(processes=NUM_THREADS) #use 5 processes to download the data
# output = pool.map(download_by_id,work_id_list)  #output is a list of [None,None,...] since download_stuff doesn't return anything

for _ in tqdm.tqdm(pool.imap_unordered(download_by_id, work_id_list), total=len(work_id_list)):
    pass

print("Script finished.")
print("The designed search range was: ", ARTWORK_ID_START, '-', ARTWORK_ID_END)


