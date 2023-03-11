
import twitter
import sys 
import time
from functools import partial
from six import string_types
from datetime import datetime
from datetime import timedelta
from functools import partial
from sys import maxsize as max_integer
from collections import Counter
import networkx as netx 
import matplotlib.pyplot as plot
from operator import itemgetter

#--------------< Verifying the credentials for the Twitter Developer account >-----------------
class Authorization:
    @staticmethod
    def twitter_login():
        try:
            CONSUMER_KEY = 'TZ7i40WeANa0gWBpytGsjc7se'
            CONSUMER_SECRET = 'NRWRlNs01IWFl8xfP6Xsct3gdb8lkOI2kBCNuVMkby47OMeD48'
            OAUTH_TOKEN = '2474122806-dWEoJhdMtwoPwFIvnZGQQk2qw5XQScTIjQ6Y92T'
            OAUTH_TOKEN_SECRET = '2sLvxi1Zn6MhQr1VJVU8x6Dvjm2EMFIALHXM5vqnZxxCf'

            auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

            twitter_api = twitter.Twitter(auth=auth)

            return twitter_api
        except twitter.api.TwitterHTTPError as e:
            print(f"There was a problem connecting to Twitter: {e}")
        except Exception as e:
            print(f"There was a problem in authorizing the Twitter account: {e}")


#--------------< Handline Twitter HTTP Errors >-----------------
class errorHandlers:
    @staticmethod
    def handle_errors(e, wait_period=2, sleep_when_rate_limited=True):
        if wait_period > 3600: # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e

        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None

        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None

        elif e.e.code in (429,420):
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 5 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60*5 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e # Caller must handle the rate limiting issue

        elif e.e.code in (500,502,503,504):
            print('Encountered {0} Error. Retrying in {1} seconds'.format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e
class twitter_data:
    
    #--------------< Constructor to set the twitter_api >-----------------
    def __init__(self, set_twitter_api):
        self.twitter_api = set_twitter_api
        
    #--------------< get the followers IDs >-----------------
    def get_friends_followers_ids(self, screen_name=None, user_id=None,
                                  friends_limit=max_integer, followers_limit=max_integer):

        # Must have either screen_name or user_id (logical xor)
        assert (screen_name != None) != (user_id != None),     "Must have screen_name or user_id, but not both"

        # See http://bit.ly/2GcjKJP and http://bit.ly/2rFz90N for details
        # on API parameters

        get_friends_ids = partial(self.make_twitter_request , self.twitter_api.friends.ids, 
                                  count=5000)
        get_followers_ids = partial(self.make_twitter_request, self.twitter_api.followers.ids, 
                                    count=5000)

        friends_ids, followers_ids = [], []

        for self.twitter_api_func, limit, ids, label in [
                        [get_friends_ids, friends_limit, friends_ids, "friends"], 
                        [get_followers_ids, followers_limit, followers_ids, "followers"]
                    ]:

            if limit == 0: continue

            cursor = -1
            while cursor != 0:

                # Use make_twitter_request via the partially bound callable...
                if screen_name: 
                    response = self.twitter_api_func(screen_name=screen_name, cursor=cursor)
                else: # user_id
                    response = self.twitter_api_func(user_id=user_id, cursor=cursor)

                if response is not None:
                    ids += response['ids']
                    cursor = response['next_cursor']

                # XXX: You may want to store data during each iteration to provide an 
                # an additional layer of protection from exceptional circumstances

                if len(ids) >= limit or response is None:
                    break

        # Do something useful with the IDs, like store them to disk...
        return friends_ids[:friends_limit], followers_ids[:followers_limit]
    
    def make_twitter_request(self,twitter_api_func,max_errors=10,*args, **kw):
        wait_period = 2
        error_count =0

        while True:
            try:
                return twitter_api_func(*args, **kw)
            except twitter.api.TwitterHTTPError as e:
                error_count = 0
                wait_period = errorHandlers.handle_errors(e,wait_period)
                if wait_period is None:
                    return

            except URLError as e:
                error_count +=1
                print >> sys.stderr, 'URLError encountered. Continuing.'
                if error_count > max_errors:
                    print >> sys.stderr, 'Too many errors...bailing out.'
                    raise

            except BadStatusLine as e:
                error_count +=1
                print >> sys.stderr, 'BadStatusLine encountered. Continuing.'
                if error_count > max_errors:
                    print >> sys.stderr, 'Too many consecutive errors...bailing out.'
                    raise
    

def main():
    try:
        print("Showing First Requirement : ")
        print("-------------------------------------------------------------------")
        print("Using self username on Twitter")
        screen_name="mourya1028"
        print("UserName selected : " , screen_name)

        authorization = Authorization();
        twitterObj = twitter_data(authorization.twitter_login())
        friends_ids, followers_ids = twitterObj.get_friends_followers_ids(
                                                           screen_name, 
                                                           friends_limit=50, 
                                                           followers_limit=50)
        print("\n\nShowing Second Requirement : ")
        print("-------------------------------------------------------------------")
        print("Fetching friends and followers list of selected user")
        print("Selected Friends list selected is : ")
        print(friends_ids)
        print("Selected Followers list selected is : ")
        print(followers_ids)
    
        print("\n\nShowing Third Requirement : ")
    except twitter.api.TwitterHTTPError as e:
        print("Error occured while running the program. Please run again after sometime")

if __name__ == "__main__":
    main()