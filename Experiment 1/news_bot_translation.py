import tweepy
import requests
import time
import logging
import urllib.request
import json
import urllib.parse
import re
import os

logging.basicConfig(filename="Bot1_3logger",filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)

#12 hours
sleeptime = 43200

#Connect the Bot to the twitter account
def authenticate():
    auth = tweepy.OAuthHandler("", "") #Add keys
    auth.set_access_token("", "") #Add tokens

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
        articles = requests.get('https://api.nytimes.com/svc/topstories/v2/science.json?api-key=') #Add API key
        with open('articles_3.json', 'w') as outfile:
            json.dump(articles.json(), outfile)
    except Exception as e:
        logging.error("Error getting articles", exc_info=True)
        raise e

#Test if the current first link was already tweeted. If yes returns True, else returns False.
def was_posted_last(link):
    #Look up the last link, which was posted
    if not os.path.exists('lastLinks_3.txt'):
        with open('lastLinks_3.txt', 'w'): pass
    with open('lastLinks_3.txt', 'r') as myfile:
        data = myfile.read()
    if link == data:
        return True
    else:
        return False

#Tweet selected news (translated headline and link)
def create_post(api):
    with open('articles_3.json', 'r') as outfile_text:
        outfile = json.load(outfile_text)
        headline = outfile["results"][0]["title"]
        link = outfile["results"][0]["url"]
        if not was_posted_last(link):
            tr_headline = get_translation(headline)
            tweet = tr_headline +"\n"+ link
            api.update_status(tweet)
            logging.info("Tweetet first result")
            with open('lastLinks_3.txt', 'w') as myfile:
                myfile.write(link)
        else:
            headline = outfile["results"][1]["title"]
            link = outfile["results"][1]["url"]
            tr_headline = get_translation(headline)
            tweet = tr_headline +"\n"+ link
            api.update_status(tweet)
            logging.info("Tweeted second result")
            with open('lastLinks_3.txt', 'w') as myfile:
                myfile.write(link)

#Get translation returns some strange backslash things, trying to fix it
def get_data_format(data):
    data = data.replace("\\\\ \\", "\\")
    data = data.replace("\\\\\\", "\\")
    begin_index = -1
    end_index = -1
    ignore = False
    for i in range(0, len(data)):
        if ignore:
            ignore = False
            continue
        if data[i] == '\\':
            ignore = True
            continue
        if data[i] == '"':
            if begin_index < 0:
                begin_index = i
            else:
                end_index = i
                return data[begin_index + 1:end_index]
    return ""


def get_response(url):
    operUrl = urllib.request.urlopen(url)
    if(operUrl.getcode()==200):
        data = operUrl.read()
    else:
        err = "Error receiving data", operUrl.getcode()
        logging.error(err)
    return get_data_format(data.decode("utf-8"))

#Translate the headline from english->german->french->english. Translates only one sentence.
def get_translation(source_text):

    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + "en" + "&tl=" + "de" + "&dt=t&q=" + urllib.parse.quote(source_text);
    result1 = get_response(url)

    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + "de" + "&tl=" + "fr" + "&dt=t&q=" + urllib.parse.quote(result1);
    result2 = get_response(url)

    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + "fr" + "&tl=" + "en" + "&dt=t&q=" + urllib.parse.quote(result2);
    result = get_response(url)
    if "\\" in result:
        return source_text
    return result

#tweets every 12 hours (sleeptime) a new translated headline and the link
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
