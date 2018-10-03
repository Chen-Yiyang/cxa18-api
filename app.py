from flask import Flask, request, request, url_for, session, jsonify, make_response, abort
import requests, json
import similarweb
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Float
import os, sys, math

from task12 import *
from task4 import *
from task6 import *
from task7 import *
from scale7 import *


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
# task 7 Similar news
#==============================
# import methods for keyword extration, similar news article search & global rank

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
# main API is here
#==============================
@app.route('/linkandtitle', methods=['POST'])
def links_titles():
    """the main part of the API"""

    # get request data
    data = request.data
    dataDict = json.loads(data)
    author_id = dataDict['id']
    retweets = int(dataDict['retweets'])
    title = dataDict['title']

    # get the keywords of the text, from functions imported from task12
    keywords = scrap_entities(title)

    # task 1 format Check
    score1 = format_check(keywords)    # out of 15

    # task 2 sentiment Check
    score2 = sentiment_check(title) # out of 15

    # task 4 retweet number (overarching)
    ratio4 = retweet_influence(retweets)    # [0.8, 1.0]

    # task 6 Author Authentification
    score6 = author_authentification(author_id) # out of 20

    
    # task 7 Similar News
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

##    if similarNotFound:
##        suggestions = [
##            {
##                'url': '',
##                'title': ''},
##            {
##                'url': '',
##                'title': ''},
##            ]
##    elif len(related_urls) == 1:
##        
##        suggestions = []
##        suggestions.append(related_rul[0])
##        suggestions.append({
##                'url': '',
##                'title': ''}
##             )
##    else:
##        tmp = update_websites(related_websites, True, (totalscore>50))
##        suggestions = related_urls[0:1]
    
    if not similarNotFound:
        suggestions = [
            {
                'url': '',
                'title': ''},
            {
                'url': '',
                'title': ''},
            ]
    else:
        tmp = update_websites(related_websites, True, (totalscore>50))
        suggestions = related_urls[0:1]

        
        
    
    
    resp = {
        "score": totalscore,
        "format": score1,
        "sentiment": score2,
        "retweet": ratio4,
        "author": score6,
        "similarity": score7,
        "url1": suggestions[0]["url"],
        "title1":suggestions[0]['title'],
        "url2": suggestions[1]["url"],
        "title2":suggestions[1]['title']
        }
    return jsonify(resp)

    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

