from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

with open('.env', 'r') as credentials:
    for line in credentials:
        exec(line)

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
t = Twitter(auth=oauth)

def print_tweet(tweet):
    print(tweet["user"]["name"])
    print(tweet["user"]["screen_name"])
    print(tweet["created_at"])
    print(tweet["text"])
    hashtags = []
    hs = tweet["entities"]["hashtags"]
    for h in hs:
        hashtags.append(h["text"])
    print(hashtags)

tweets = t.search.tweets(q="hackathon", result_type="recent",count=199)["statuses"]
for tweet in tweets:
    print_tweet(tweet)
    print()
