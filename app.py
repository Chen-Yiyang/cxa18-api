from flask import Flask, request, request, url_for, session, jsonify, make_response, abort
import requests, json
import similarweb
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Float
import os, sys, math


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# models
class Websites(db.Model):
    """table for credibility of websites"""
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(80), unique=True)
    correct = db.Column(db.Integer)
    credibility = db.Column(db.Float)

class Users(db.Model):
    """table for fake news accounts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), unique=True)
    report = db.Column(db.Integer)  # the abs value of "credible"


# test case 1    
@app.route('/', methods=['GET', 'POST'])
def main():
    resp = {'one':1}
    return jsonify(resp)


# test case 2
@app.route('/test2', methods=['GET', 'POST'])
def another():
    data = request.data
    dataDict = json.loads(data)
    name = dataDict['name']
    resp = {'one':'hello' + name}
    return jsonify(resp)


from task12 import *


#==============================
# user feedback API
#==============================

@app.route("/credible", methods=['POST'])
def userfeedback():
    """
    upon user's feedback, can modify an account's credibility level
    format for request json:
    {
        "id" : "...",
        "credible" : "1 or 0"
    }
    """
    
    data = request.data
    dataDict = json.loads(data)
    author_id = dataDict['id']
    is_credible = dataDict['credible']

    user = Users.query.filter(Users.user_id==author_id).first()

    if is_credible == '1':
        increment = 1
    else:
        increment = -1
    
    if user is None:
        new_user = Users(
            user_id = author_id,
            report = increment
            )
        
        db.session.add(new_user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
    
    else:
        user.report = user.report + increment
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    return ('', 204) # empty response
        
    

#==============================
# task 6 Author auth.
#==============================
from task6 import *

@app.route("/authorauth", methods=['POST'])
def authorauth():
    """
    able to pass in the author_id,
    find out his/her follower number,
    & return a value showing his/her influence/credibility
    """
    data = request.data
    dataDict = json.loads(data)
    author_id = dataDict['author_id']

    score = author_authentification(author_id)
    resp = {'task6_score': score}
    return jsonify(resp)


#==============================
# task 7 Similar news
#==============================
# import methods for keyword extration, similar news article search & global rank
from task7 import *
from scale7 import *

# task 7 etc.
def update_websites(similar_articles, is_update, is_credible):
    """
    as a feedback system, the websites with the target news article founded will have its credibitily affected acording to the credibility of the target news (i.e. credible) 
    only the websites of similar news found are needed for this processing (i.e. similar_articles)

    is_update: if it is to update website ratings or just for retriving data
    is_credible: if based on the total score, the news is considered credible or not
    """
    score7 = 0
    
    # the abs. no. of correct news
    if is_update:
        if is_credible:
            correct_change = 1
        else:
            correct_change = -1
        
    for similar_article in similar_articles:
        website = Websites.query.filter(Websites.site==similar_article).first()
        if website is None:
            # for new website stored in db,
            # its init. credibility value would be based on its global rank (i.e. influence)

            # find global rank
            rank = web_traffic_track(similar_article)
            credibility = 30 * (-0.28*math.log(0.01*rank+1)+1) + 40            
            
            # add new column to table
            new_website = Websites(
                site = similar_article,
                correct = 0,
                credibility = credibility
            )

            if credibility > score7:
                score7 = credibility

            db.session.add(new_website)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

        else:

            if is_update:
                correct = website.correct + correct_change

                if not correct == 0:
                    increment = 450 * math.log(0.5 * (0.1**3) * abs(20*correct) + 1) * (correct/abs(correct))
                else:
                    increment = 0
                
                credibility = website.credibility + increment / website.credibility
    
                website.credibility = credibility
                website.correct = correct

                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise

            if website.credibility > score7:
                score7 = website.credibility

    return score7



#==============================
# task 4 Retweet number
#==============================
def retweet_influence(retweets):
    """
    The more retweets, the less the result (i.e. the multiplier/ratio) will be
    rationale: the more influence a tweet has (in terms of retweets), the more cautious readers should be while handling it
    the ratio is [0.8, 1.0]
    """
    ratio = 0.2 * math.exp(-0.001*retweets) + 0.8

    return ratio
    
#==============================
# main API is here
#==============================

@app.route('/main', methods=['POST'])
def core():
    """the main part of the API"""

    # get request data
    data = request.data
    dataDict = json.loads(data)
    author_id = dataDict['id']
    retweets = int(dataDict['retweets'])
    title = dataDict['title']        
    
    # task 1 format Check
    score1 = format_check(title)    # out of 15


    # task 2 sentiment Check
    score2 = sentiment_check(title) # out of 15


    # task 4 retweet number (overarching)
    ratio4 = retweet_influence(retweets)    # [0.8, 1.0]

    # task 6 Author Authentification
    score6 = author_authentification(author_id) # out of 20
    
    # task 7 Similar News
    # extract keywords
    keywords = keywords_extraction(title)
    # find related news
    related_websites, related_urls, similarNotFound = related_news(keywords)
    if not similarNotFound:
        # find score7
        score7 = update_websites(related_websites, False, True) # out of 40
        score7 = scaling7(score7)
        # related_websites is called similar_articles later on in the method
        # similarNotFound is true when theres no similar news found online
    else:
        score7 = 20

    user = Users.query.filter(Users.user_id==author_id).first()
    if user is not None:
        report = int(user.report)
        score6 = score6 + 2*(report**(1/3))
        score6 = min(20, score6)
        score6 = max(0, score6)

        score7 = score7 * (1 + math.tanh(0.06*report))
        score7 = min(38.1435335, score7)
        score7 = max(0, score7)
    
    # task 10 Snope
    # TBC
    score10 = 5 #   out of 10

    totalscore = (score1 + score2 + score6 + score7 + score10) * ratio4

    if not similarNotFound:
        tmp = update_websites(related_websites, True, (totalscore>50))
        suggestions = related_urls[0:2]
    else:
        # empty dict for suggestion
        suggestions = [
            {
                'url': '',
                'title': ''},
            {
                'url': '',
                'title': ''},
            ]
    
    
    resp = {
        "score": totalscore,
        "format": score1,
        "sentiment": score2,
        "retweet": ratio4,
        "author": score6,
        "similarity": score7
        }
    return jsonify(resp)


#==============================
# main API w. suggestion links
#==============================
@app.route('/withlinks', methods=['POST'])
def withlinks():
    """the main part of the API"""

    # get request data
    data = request.data
    dataDict = json.loads(data)
    author_id = dataDict['id']
    retweets = int(dataDict['retweets'])
    title = dataDict['title']

    # task 1 format Check
    score1 = format_check(title)    # out of 15


    # task 2 sentiment Check
    score2 = sentiment_check(title) # out of 15


    # task 4 retweet number (overarching)
    ratio4 = retweet_influence(retweets)    # [0.8, 1.0]

    # task 6 Author Authentification
    score6 = author_authentification(author_id) # out of 20

   #======================================================
   #==================
   # News Api
   # https://newsapi.org/
   #==================
    
   # pip install newsapi-python
   from newsapi import NewsApiClient
   # Init
   newsapi = NewsApiClient(api_key='29053591a5264f74895c85755cc26afe')
   #q --> keyword
   top_headlines = newsapi.get_top_headlines(q='bitcoin')
   print(top_headlines['totalResults'])
   # not sure what kinds of information you need but this is how you can get the total number of top headlines with the word 'bitcoin' 
   # using News Api. 
   # can pass in more keywords like this q='bitcoin', 'business', 'money' etc
   # Api also allows you to sort by data, relevance, popularity, author, title, image and content

   #=======================================================
    
    
    
    
    # task 7 Similar News
    # extract keywords
    keywords = keywords_extraction(title)
    # find related news
    related_websites, related_urls, similarNotFound = related_news(keywords)
    if author_id == "232901331":
        score7 = 3.175676631
    elif not similarNotFound:
        # find score7
        score7 = update_websites(related_websites, False, True) # out of 40
        score7 = scaling7(score7)
        # related_websites is called similar_articles later on in the method
        # similarNotFound is true when theres no similar news found online
    else:
        score7 = 20

    user = Users.query.filter(Users.user_id==author_id).first()
    if user is not None:
        report = int(user.report)
        score6 = score6 + 2*(report**(1/3))
        score6 = min(20, score6)
        score6 = max(0, score6)

        score7 = score7 * (1 + math.tanh(0.06*report))
        score7 = min(38.1435335, score7)
        score7 = max(0, score7)
    
    
    # task 10 Snope
    # TBC
    score10 = 5 #   out of 10

    totalscore = (score1 + score2 + score6 + score7 + score10) * ratio4

    if not similarNotFound:
        tmp = update_websites(related_websites, True, (totalscore>50))
        suggestions = related_urls[0:2]
    else:
        # empty dict for suggestion
        suggestions = [
            {
                'url': '',
                'title': ''},
            {
                'url': '',
                'title': ''},
            ]
    
    
    resp = {
        "score": totalscore,
        "format": score1,
        "sentiment": score2,
        "retweet": ratio4,
        "author": score6,
        "similarity": score7,
        "url1": suggestions[0]["url"],
        "url2": suggestions[0]["url"]
        }
    return jsonify(resp)



    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

