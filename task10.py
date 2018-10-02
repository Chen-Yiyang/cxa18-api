import requests
import math
import json
import sys, os
import argparse
import urllib.request
import retinasdk
import credentials
from bs4 import BeautifulSoup
from selenium import webdriver

# for entities handling
from task12 import *

#=============================
# Snope
#=============================

def get_soup(url):
    """Create a soup from url"""
    opener = urllib.request.build_opener()
    opener.addheader = [('User-agent', "Mozilla/5.0")]
    page = opener.open(url)
    soup = BeautifulSoup(page,'lxml')
    return soup

def get_truth(snopes_href):
    """returns if the rumor is considered true or false"""
    snopes_url = snopes_href
    soup = get_soup(snopes_url)
    review = soup.find('span', {'itemprop': 'reviewRating'})
    if review:
        if ('True' in str(review)):
            return True
    else:
        review = soup.find('font', {'class': 'status_color'})
        if review:
            if 'TRUE' in str(review):
                return True
    return False
##
##def snope_check(text):
##    keys = scrap_entities(text)
##    if len(keys) > 3:
##        keys = keys[:2]
##    for i in range(len(keys)):
##        keys[i] = '"'+keys[i]+'"'
##    # print(keys)
##    
##    exe_dir = os.path.dirname(os.path.realpath(sys.argv[0])) +  '/phantomjs-2.1.1-windows/bin/phantomjs.exe'
##    driver = webdriver.PhantomJS(executable_path=exe_dir)
##
##    url = 'https://www.snopes.com/?s=%s' % '+'.join(keys)
##    # print(url)
##    driver.get(url)
##
##    html = driver.page_source
##    soup = BeautifulSoup(html,"lxml")
##    # print(soup.prettify())
##    # check out the docs for the kinds of things you can do with 'find_all'
##    # this (untested) snippet should find tags with a specific class ID
##    # see: http://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class
##
##    count = 0
##    serp = soup.find_all('a', 'search-results-post')
##    if len(serp) > 11:
##        serp = serp[:10]
##    serps = []
##    for serp_item in serp:
##        serps.append(serp_item.get('href'))
##    if serp:
##        for serp_item in serps:
##            if ((get_truth(serp_item)) and ('fact-check' in serp_item)):
##                count += 1
##            if ((not get_truth(serp_item)) and ('fact-check' in serp_item)):
##                match = True
##                for key in keys:
##                    if key not in serp_item:
##                        match = False
##                if match == True:
##                    count = -1
##                break
##    if count > 0: 
##        count = math.log(count*5)*5
##    elif count < 0:
##        count = 0
##    else:
##        count = 5
##    return count
##
