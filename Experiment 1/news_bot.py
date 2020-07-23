import tweepy
import requests
import time
import logging
import os
import json

logging.basicConfig(filename="Bot1_1logger",filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)

#12 hours
sleeptime = 43200

#Connect the Bot to the twitter account
def authenticate():
    auth = tweepy.OAuthHandler("", "") # Add you Keys
    auth.set_access_token("", "") # Add your tokens

    api = tweepy.API(auth, wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except Exception as e:
        logging.error("Error creating API", exc_info=True)
        raise e
    logging.info("API created")

    return api

#Get all headlines and links from the topstories (science) of the NYT
def get_data():
    try:
        articles = requests.get('https://api.nytimes.com/svc/topstories/v2/science.json?api-key=') # Add API key
        with open('articles_1.json', 'w') as outfile:
            json.dump(articles.json(), outfile)
    except Exception as e:
        logging.error("Error getting articles", exc_info=True)
        raise e


#Test if the current first link was already tweeted. If yes returns True, else returns False.
def was_posted_last(link):
    #Look up the last link, which was posted
    if not os.path.exists('lastLinks_1.txt'):
        with open('lastLinks_1.txt', 'w'): pass
    with open('lastLinks_1.txt', 'r') as myfile:
        data = myfile.read()
    if link == data:
        return True
    else:
        return False

#Tweet selected newsheadline and link
def create_post(api):
    with open('articles_1.json', 'r') as outfile_text:
        outfile = json.load(outfile_text)
        headline = outfile["results"][0]["title"]
        link = outfile["results"][0]["url"]

        # Avoids to post the same link twice in a row by checking the last posted link
        if not was_posted_last(link):
            tweet = headline +"\n"+ link
            api.update_status(tweet)
            logging.info("Tweetet first result")
            with open('lastLinks_1.txt', 'w') as myfile:
                myfile.write(link)
        else:
            headline = outfile["results"][1]["title"]
            link = outfile["results"][1]["url"]
            tweet = headline +"\n"+ link
            api.update_status(tweet)
            logging.info("Tweeted second result")
            with open('lastLinks_1.txt', 'w') as myfile:
                myfile.write(link)


#tweet, sleep, repeat
def main():
    api = authenticate()
    while True:
        try:
            get_data()
            create_post(api)
        except Exception as e:
            msg = "Error: " + str(e)
            logging.error(msg, exc_info=True)
            raise e
        time.sleep(sleeptime)

if __name__ == '__main__':
    main()
