import tweepy
import requests
import time
import logging
from datetime import datetime
import random
import os
import json

logging.basicConfig(filename="Bot1_2logger",filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)

# Times between which can be tweeted
min_time = datetime.strptime('9:00:00', '%H:%M:%f').time()
max_time = datetime.strptime('19:30:00', '%H:%M:%f').time()


#Connect the Bot to the twitter account
def authenticate():
    auth = tweepy.OAuthHandler("", "") # Add keys
    auth.set_access_token("", "") # Add tokens

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
        with open('articles_2.json', 'w') as outfile:
            json.dump(articles.json(), outfile)
    except Exception as e:
        logging.error("Error getting articles", exc_info=True)
        raise e

#Test if the current first link was already tweeted. If yes returns True, else returns False.
def was_posted_last(link):
    #Look up the last link, which was posted
    if not os.path.exists('lastLinks_2.txt'):
        with open('lastLinks_2.txt', 'w'): pass
    with open('lastLinks_2.txt', 'r') as myfile:
        data = myfile.read()
    if link == data:
        return True
    else:
        return False

#Tweet selected news (headline and link)
def create_post(api):
    with open('articles_2.json', 'r') as outfile_text:
        outfile = json.load(outfile_text)
        headline = outfile["results"][0]["title"]
        link = outfile["results"][0]["url"]

        #Avoids twwting the same two news in a row
        if not was_posted_last(link):
            tweet = headline +"\n"+ link
            api.update_status(tweet)
            logging.info("Tweetet first result (timed)")
            with open('lastLinks_2.txt', 'w') as myfile:
                myfile.write(link)
        else:
            headline = outfile["results"][1]["title"]
            link = outfile["results"][1]["url"]
            tweet = headline +"\n"+ link
            api.update_status(tweet)
            logging.info("Tweeted second result (timed)")
            with open('lastLinks_2.txt', 'w') as myfile:
                myfile.write(link)


#sleep (random amount), tweet if right time (between min_time and max_time)
def main():
    api = authenticate()
    while True:
        try:
            # Sleep 1 min to 8 hours
            random_addition = random.randint(60,28800)
            time.sleep(random_addition)
            current_time = datetime.now().time()
            right_time = min_time < current_time < max_time
            #If it is twwet time after sleeping tweets
            if right_time:
                get_data()
                create_post(api)
            elif not right_time:
                # Sleep for the nighttime. Sometimes sleeps longer than the min_time, but that's okay.
                # Reduces the amounts of tries over night.
                time.sleep(14400)
        except Exception as e:
            msg = "Error: " + str(e)
            logging.error(msg, exc_info=True)
            raise e


if __name__ == '__main__':
    main()
