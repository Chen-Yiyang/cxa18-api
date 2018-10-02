import argparse
import urllib.request
import requests
import json
import math
import json
import credentials
from bs4 import BeautifulSoup
import ssl
ssl.match_hostname = lambda cert, hostname: True


def generate_request(user_id):
    REQUEST_URL = 'http://api.twittercounter.com?twitter_id='+user_id+'&apikey=26b2eece5c647c64b837e5433c322139'
    return REQUEST_URL
 
def get_response(user_id):
    REQUEST_URL = generate_request(user_id)
    response = requests.get(REQUEST_URL)
    return response.json()
 
##def get_follower_number(data):
##    return data['followers_current']
 
def author_authentification(user_id):
    response = get_response(user_id)

    try:
        followers = response['followers_current']
        
        #point_auther_authentification = math.log(int(0.001*get_follower_number(response)))
        point_auther_authentification = math.log(1+int(0.1*followers)) # to make sure pt > 0
        if point_auther_authentification < 20:
            return point_auther_authentification
        else:
            return 20
    except KeyError:
        # user not found
        return 5


### mainer_id = "265902729" # for testing now
##print(author_authentification(user_id))

