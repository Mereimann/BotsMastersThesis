import tweepy
import time
import logging

logging.basicConfig(filename="likeBot",filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)

#Connect the Bot to the corresponding twitter account
def authenticate():
    auth = tweepy.OAuthHandler("", "") #Add keys
    auth.set_access_token("", "") #Add tokens

    api = tweepy.API(auth, wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except Exception as e:
        logging.error("Error creating API 1", exc_info=True)
        raise e
    logging.info("API 1 created")

    return api

#Get a list of the ids of the tweets you want to favorite
def get_likes(api):
    like_ids = []
    try:
        #Look for the 40 last tweets in your timeline
        timeline = api.home_timeline(count=40)
        for obj in timeline:
            #Define which tweets on your timeline you want to like (here: more than two likes, in english, not yet liked, and not possibly sensitive)
            if obj.favorite_count > 2 and obj.lang == "en" and not obj.favorited and not obj.possibly_sensitive and obj.id not in like_ids:
                like_ids.append(obj.id)
    except Exception as e:
        logging.error("Could not get like_ids")
        raise e
    return like_ids

#Every 6 hours check if a tweet in your timeline fullfills the favorite requirements and favorite them
def main():
    api = authenticate()

    while True:
        list_likes = get_likes(api)
        for id in list_likes:
            try:
                api.create_favorite(id)
            except Exception as e:
                text = "API could not favorite" + str(id)
                logging.error(text)
                raise e
        time.sleep(21600)


if __name__ == '__main__':
    main()
