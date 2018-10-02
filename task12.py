import requests
import math
import json
import argparse
import urllib.request
import itertools
import retinasdk
import credentials
from bs4 import BeautifulSoup
from selenium import webdriver


# set paras
liteClient = retinasdk.LiteClient("2fe758f0-8670-11e8-917d-b5028d671452")

DANDELION_APP_ID = '159581bc091046b28e91a97ca4d5032f'
DANDELION_APP_KEY = '159581bc091046b28e91a97ca4d5032f'

ENTITY_URL1 = 'https://api.dandelion.eu/datatxt/nex/v1' 
ENTITY_URL2 = 'https://api.dandelion.eu/datatxt/sent/v1'


#==============================
# task1 form check
#==============================
def get_entities(text, confidence=0.5, lang='en'):
    payload = {
        '$app_id': DANDELION_APP_ID,
        '$app_key': DANDELION_APP_KEY,
        'text': text,
        'confidence': confidence,
        'lang': lang,
        'top_entities': 2,
    }
    response = requests.get(ENTITY_URL1, params=payload)
    return response.json()

def scrap_entities(text):
    data = get_entities(text)
    entities = []
    for annotation in data['annotations']:
        entities.append(annotation['spot'])
    entities= [entity.lower() for entity in entities]
    return entities

def format_check(text):
    return min(len(scrap_entities(text))*5,15)



#==============================
# task 2 sentiment check
#==============================

def get_sentiment(text, lang='en'):
    payload = {
        '$app_id': DANDELION_APP_ID,
        '$app_key': DANDELION_APP_KEY,
        'text': text,
        'lang': lang,
    }
    response = requests.get(ENTITY_URL2, params=payload)
    return response.json()


def scrap_sentiment(data):
    return 15 - abs(float(data['sentiment']['score']))**3*10


def sentiment_check(text):
    response_paragraph = get_sentiment(text)
    sentiment_paragraph = scrap_sentiment(response_paragraph)
    return(sentiment_paragraph)



##for title-para conformity check
##def title_content_check():
##    
##    title = "So what you're saying is we just found water on Mars.... But we can't make an iPhone charger that won't break after three weeks?"
##    paragraph = "Human found water on Mars yet fail in making sustainable iphone chargers."
##    weight_title_content_match = 1
##    entities_title = scrap_entities(title)
##    entities_paragraph = scrap_entities(paragraph)
##    mismatch = 0
##    for entity in entities_title:
##        if entity not in entities_paragraph:
##            mismatch += 1
##    point_title_content_match = 0 - 10 * mismatch // len(entities_title)
##    print(point_title_content_match) # not print but return
