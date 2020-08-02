#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 17:05:02 2020

@author: andreamorgar
@author: wizmik12

=============
Web scrapping
=============

With this script we scrap some data from a Spanish poetry site. 
We take the sitemap and we scrape all pages within it. Finally, we generate a
dataset with three columns: author, title and poem. 

Site 
----
www.poemas-del-alma.com

Procedure
-------------
We get access to the sitemap to obtain poems' hrefs

"""

#%%

# Import libraries 
import bs4, os, requests
import pandas as pd

#%%

# Get sitemap
def get_sitemap(site='https://www.poemas-del-alma.com/sitemap.php'):

    '''
    Get the poemas-del-alma.com sitemap and save it to a local file.
    '''
    # If the sitemap already exists, don't bother getting it again


    for attempt in range(1, 4):
        # we part from the initial sitemap
        page = requests.get(site)

    if not page:
        raise Exception('Failed to get sitemap.xml')

    sitemap = bs4.BeautifulSoup(page.text, 'xml')
    
    next_sitemaps = []
    poetry_urls = []

    # we need to diff between sitemap urls (there is more than one) and
    # poems' urls. The first ones are going to provide us more poem links, 
    # so we'll use them later
    with open('poetry_sitemap.txt', 'w') as f:
        for line in sitemap.find_all('a'):
            url = line.get('href')
            # print(url)
            if url.startswith('https://www.poemas-del-alma.com/sitemap'):
                next_sitemaps.append(url)
                
            elif url.startswith('https://www.poemas-del-alma.com/'):
                f.write(url + '\n')
                poetry_urls.append(url)
                    
    return next_sitemaps, poetry_urls
    

#%%

# function to scrape title, poem and author from each blog entry. 
def get_data_from_poem_url(poem_url):  
    
    poem_raw = None
    poem_author = None
    poem_title = None
    
    # print("------------------------------------------------------------------")
    
    # It seems the page rejects GET requests that do not identify a User-Agent.
    # I visited the page with a browser (Chrome) and copied the User-Agent header 
    # of the GET request (look in the Network tab of the developer tools):
    # https://stackoverflow.com/questions/38489386/python-requests-403-forbidden
    
    # we get the lxml text from the url
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    page = requests.get(poem_url, headers=headers)
    poem_soup = bs4.BeautifulSoup(page.text, 'lxml')  
    
    # get poem author 
    try:
        poem_author = poem_soup.find("h3",attrs={"class":"title-content"}).text
    except AttributeError:
        poem_author = ""
        
        print(poem_url)
        
    # get poem title 
    try:    
        poem_title = poem_soup.find("h2",attrs={"class":"title-poem"}).text
    except:
        poem_title = ""
        print(poem_url)
    
    # get poem content (we only capture the text from the tag)
    try:
        # get poem raw
        poem_content = poem_soup.find(id="contentfont")
        poem_raw = poem_content.find("p").text
        # print(poem_raw)
    except:
        print(poem_url)
    
    # finally we return a dict with all the scraped data
    return {"title":poem_title, "author":poem_author, "content" :poem_raw}
    

#%%

# We need to obtain all posible urls from the sitemap. It has pagination so we
# run the same process for each one of its pages.

# main sitemap 
sitemaps, poetry_urls = get_sitemap()

# rest of sitemap pages
for i in sitemaps:
    print(i)
    sitemaps_, poetry_urls_ = get_sitemap(i)
    
    #append the new poetry urls from the rest of sitemap pages
    poetry_urls += poetry_urls_
    
# drop duplicates
# in poetry_urls we have saved every urls from a poem entry in the sitemap
poetry_urls = list(set(list(poetry_urls)))
#%%


# We scrape the data for each one of the poem entry urls.
# We save everything in a list that we will use later to build a dataframe
poems_dict = []
len_poems = len(poetry_urls)
for i,poem in enumerate(poetry_urls):
    print("Poema "+ str(i) + " de "+ str(len_poems))
    poems_dict.append(get_data_from_poem_url(poem))


#%% 

# we build and save the dataframe   
df = pd.DataFrame(poems_dict)
df.to_csv("poems.csv",index=False)
