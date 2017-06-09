from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys #potential use later?
#import traceback
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

from bs4 import BeautifulSoup
from urllib.request import urlopen

with open('.env', 'r') as credentials:
    for line in credentials:
        exec(line)

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
t = Twitter(auth=oauth)

'''
universal json

title
subtitle
date/time remaining
loc
language
theme
source
link
'''

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

def from_twitter():
    tweets = t.statuses.user_timeline(screen_name="HackathonWatch")
    for tweet in tweets:
        print(tweet["text"])
        print()

def from_hackathonDotCom(keyword):
    finder = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
    finder.set_window_size(1120, 500) #workaround a bug
    finder.get('www.hackathon.com')

    try:
        search = WebDriverWait(finder, 10).until(EC.element_to_be_clickable((By.ID, "search")))
        search.click()
        search.send_keys(keyword)
        search.submit()
        #to be continued, halted because of an error
    except:
        pass

def parse_hackathonDotio(ele):
    data = {'source': 'http://www.hackathon.io'}
    try:
        data['time'] = ele.find('div', {'class': 'two columns time'}).contents[2].strip()
    except:
        data['time'] = None
    try:
        data['link'] = data['source'] + ele.find('h4').contents[0]['href']
    except:
        data['link']= None
    try:
        data['title'] = ele.find('h4').contents[0].contents[0].strip()
    except:
        data['title'] = None
    try:
        data['subtitle'] = ele.find('h5').contents[0].contents[0].strip()
    except:
        data['subtitle'] = None
    try:
        data['location'] = ele.find('div', {'class':'two columns location'}).contents[1].contents[1].strip()
    except:
        data['location'] = None

    data['lang'] = None #maybe language available in future
    data['theme'] = None
    return data

def from_hackathonDotio(): #keyword functionality later
    with urlopen('http://www.hackathon.io') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    every = soup.find_all('div', {'class': 'event-teaser'})
    total = []
    for ele in every:
        total.append(parse_hackathonDotio(ele))

    return total
