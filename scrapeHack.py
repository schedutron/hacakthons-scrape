from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys #potential use later?
#import traceback
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

from bs4 import BeautifulSoup #some people on web claim lxml to be faster than bs4?
from urllib.request import urlopen

with open('.env', 'r') as credentials:
    for line in credentials:
        exec(line)

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
t = Twitter(auth=oauth)

metadata = ['title', 'subtitle', 'description', 'time', 'location', 'tags', 'source', 'link'] #universal json
#think about converting time from a string to a time object

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

def parse_hackathonDotcom(ele):
    data = dict.fromkeys(metadata)
    #data from this source contains image as well, but presently images aren't supported here. Maybe later they will be.
    data['source'] = 'http://www.hackathon.com'

    try:
        location_p = ele.find('p', {'class':'hackathon-location'}) #contains location links
        atoms = location_p.find_all('a')
        location = atoms[0].contents[0].strip() + ', ' + atoms[1].contents[0].strip()
        data['location'] = location
    except:
        pass

    try:
        title = ele.find('p', {'class':'hackathon-name'}).find('a') #scrapes out title
        data['title'] = title.contents[0].strip()
    except:
        pass

    try:
        data['link'] = data['source'] + title['href'] #scrapes out link about hackathon, link which is href of title
    except:
        pass

    try:
        data['description'] = ele.find('p', {'class':'hackathon-desc hidden-xs'}).contents[0].strip() #scrapes out hackathon description
        #description perhaps not clean! contains \n and stuff (probably unicode stuff)
    except:
        pass

    try: #this block scrapes time of hackathon
        time_data = ele.find('div', {'class':'hackathon-date-month-year'}).contents
        month_year = time_data[0].replace(u'\xa0', ' ') #month and year
        date = time_data[1].get_text() #the date; get_text() can often be used in place of contents[0]
        data['time'] = date+' '+month_year #combines date, month year
    except:
        pass

    try: #this block scrapes tags (if available)
        tags = ele.find('p', {'class':'hidden-xs hackathon-tags'}).contents #get the tags
        data['tags'] = [tag.contents[0].get_text() for tag in tags]
    except:
        pass

    return data

def from_hackathonDotcom(keyword=None):
    if keyword:
        pass #will add later

    with urlopen('http://www.hackathon.com') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    '''
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
        pass'''
    total = []
    block = soup.find('div', {'class':'main-content'})
    cities = block.find_all('a')
    for city in cities:
        link = 'http://www.hackathon.com' + city['href']
        with urlopen(link) as city_page:
            city_html = city_page.read()
        city_soup = BeautifulSoup(city_html, 'html.parser')
        city_hacks = city_soup.find_all('div', {'class':'row hackthon-list-item'}) #hackathons in the city
        for city_hack in city_hacks:
            total.append(parse_hackathonDotcom(city_hack))
    return total

def parse_hackathonDotio(ele):
    data = dict.fromkeys(metadata)
    data['source'] = 'http://www.hackathon.io'
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

    '''
    data['lang'] = None #maybe language available in future
    data['theme'] = None
    '''
    data['tags'] = None #tags used in place of lang, theme etc.
    return data

def from_hackathonDotio(keyword=None):
    if keyword: pass #keyword functionality later
    with urlopen('http://www.hackathon.io') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    every = soup.find_all('div', {'class': 'event-teaser'})
    total = []
    for ele in every:
        total.append(parse_hackathonDotio(ele))

    return total
