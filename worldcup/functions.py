import tweepy
from . import twitter_creds
import json
import re
class Tweet(object):
    def __init__(self, create, user, text, link):
        self.create = create
        self.user = user
        self.text = text
        self.link = link
        
    def __str__():
        return "created_at: " + str(tweet['created_at']) + " - " + "user: " + str(tweet['user']['screen_name'] + "\n" +"Tweet:" + str(tweet['text']))

def get_tweets(team):
    regex = re.compile("(?P<url>https?://[^\s]+)")
    auth = tweepy.OAuthHandler(twitter_creds.consumer_key, twitter_creds.consumer_secret)
    auth.set_access_token(twitter_creds.access_token, twitter_creds.access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    tweetList = []
    item = api.search("peru world cup", count = 36)
    item = item['statuses']
    for i in item:
        url = regex.search(i['text'])

        if url == None:
            tweetList.append(Tweet(i['created_at'], i['user']['screen_name'], i['text'], None))
        else:
             tweetList.append(Tweet(i['created_at'], i['user']['screen_name'], i['text'], url.group('url')))

    return tweetList
