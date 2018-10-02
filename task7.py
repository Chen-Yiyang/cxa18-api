import webhoseio
import requests
import json
import argparse
import urllib.request
import itertools
import retinasdk
import credentials
import similarweb

from task12 import *

# extract keywords
def keywords_extraction(text_str):
    """extract keywords using the Dandelion API"""
    return scrap_entities(text_str)


# related news
def related_news(keywords):
    """
    search for related news by keywords
    use Webhose.io API
    """

    if len(keywords)>=4:
        keywords = keywords[0:3]
    
    keyword_str = " ".join(keywords)
    
    #API key
    webhoseio.config(token="0e3f95f5-2fc7-494f-881e-e29915cc3e9a")
    query_params = {
        "q": keyword_str + " language:english site_type:news",
        "ts": "1528948373304",
        "sort": "relevancy"
    }
    
    resp = webhoseio.query("filterWebContent", query_params)
    posts = resp['posts']    

    if len(posts) < 2:
        return None, None, True
    
    MAX_ARTICLES = 5 # take first 5
    
    related_articles = []
    related_urls = []
    
    for i in range(min(MAX_ARTICLES, len(posts))):
        post = posts[i]['thread']
        related_url = {
            'url': post['url'],
            'title': post['title']}
        related_urls.append(related_url)
        related_articles.append(post['site_full'])  # currently redirected link

    return related_articles, related_urls, False


# web traffic track for global rank
def web_traffic_track(website_tracked):
    """
    Similar Web API for global ranking of a website
    the global rank of Jun 2018 will be used, as it is latest available
    """
    
    SIMILAR_WEB_API = "a2f9ba0d39ac49e3b1735845d7915347"

    # a try-exception may be needed
    domains = website_tracked.split(".")
    domains = domains[-2:]
    website_tracked = '.'.join(domains)

    API_URL = "https://api.similarweb.com/v1/website/{website}/global-rank/global-rank?api_key=a2f9ba0d39ac49e3b1735845d7915347&start_date=2018-06&end_date=2018-06" \
              "&main_domain_only=false".format(website = website_tracked)
    
    response = requests.get(API_URL)
    result = response.json()
    rank = result['global_rank'][0]['global_rank'] # take Jun 18
    
    return rank
