from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys #potential use later?
from selenium.common.exceptions import TimeoutException
#import traceback
import requests
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

from bs4 import BeautifulSoup #some people on web claim lxml to be faster than bs4?
from urllib.request import urlopen

with open('.env', 'r') as credentials:
    for line in credentials:
        exec(line)

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
t = Twitter(auth=oauth)

metadata = ['title', 'subtitle', 'description', 'time', 'location', 'tags', 'source', 'link', 'prize', 'cost'] #universal json
#think about converting time from a string to a time object
#if description is short enough, it will be added to subtitle, and description value would be None
#if prize is null, it need not imply that there are no prizes; one can always visit the hackathon link for more info

#Sources:
#www.hackathon.io
#www.hackathon.com
#www.challengerocket.com
#devpost.com
#eventbrite.ie

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

def parse_challengerocketDotcom(ele):
    data = dict.fromkeys(metadata)
    data['source'] = 'https://www.challengerocket.com'

    try: #to get time
        time_data = ele.find('p', {'class':'submit-time'}).contents
        days = time_data[2].get_text()
        days = days.replace('d', ' d') #converts '6days' to '6 days'
        data['time'] = days + ' ' + time_data[0].get_text() #becomes like '6 days till start' or '6 days submit project'
        data['time'] = data['time'].lower() #looks cleaner in all lowercase
    except:
        pass

    try: #to get prize info
        prize_data = ele.find('p', {'class':'win'}).contents
        data['prize'] = prize_data[2].get_text()
        '''amount here need not be the amount given to the winner - for example,
        it may be the total amount invested for prizes'''
        if data['prize'].lower() == 'other': #other pops up sometimes
            data['prize'] = None
    except:
        pass

    try: #to get location
        atoms = ele.find('ul', {'class':'list-panel-item-menu'}) #location list
        items = [item.get_text() for item in atoms if item != '\n'] #removes all '\n'
        items.reverse() #so as to display city name before country name and so on...
        data['location'] = ', '.join(items)
    except:
        pass

    try: #to get title
        anchor = ele.find('h3', {'class':'title'}).contents[1]
        data['title'] = anchor.get_text()
    except:
        pass

    try: #to get link
        data['link'] = anchor['href']
    except:
        pass

    try: #to get description
        data['description'] = ele.find('p', {'class':'description'}).contents[0].get_text()
    except:
        pass

    return data

def from_challengerocketDotcom(keyword=None):
    if keyword:
        pass #will add keyword support later
    with urlopen('https://www.challengerocket.com/list.html') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    relevant = soup.find('ol', {'class':'full-list grid list is-bg-white js-isotope'}) #finds the element containing hackathons' info
    blocks = relevant.find_all('li', {'class':'grid-item'})
    total = []
    for block in blocks: #an individual block has info of one hackathon
        total.append(parse_challengerocketDotcom(block))
    return total

def parse_devpostDotcom(ele):
    data = dict.fromkeys(metadata)
    data['source'] = "https://devpost.com"
    try: #to get title
        content = ele.find('div', {'class':'content'})
        data['title'] = content.contents[1].get_text().strip()
    except:
        pass

    try: #to get location
        data['location'] = content.find('p', {'class':'challenge-location'}).contents[2].strip()
    except:
        pass

    try: #to get subtitle
        data['subtitle'] = content.find('p', {'class':'challenge-description'}).contents[0].strip()
    except:
        pass

    try: #to get prize amount
        part = ele.find('div', {'class':'prizes clearfix'})
        suffix = part.find('span', {'class':'action'}) # "IN PRIZES" suffix
        amount = part.find('span', {'class':'value'})
        if not amount: #probably non-monetary prizes
            print(suffix)
            data['prize'] = suffix.get_text().strip()
        else:
            data['prize'] = amount.get_text().strip()
    except:
        pass

    try: #to get date
        time_stuff = ele.find('div', {'class':'submission-time clearfix'})
        suffix = time_stuff.find('span', {'class':'action'}) #to see whether we have a date range or a deadline for the time value
        data['time'] = time_stuff.find('span', {'class':'value'}).get_text().strip()
        if suffix:
             data['time'] += " " + suffix.get_text().strip().lower()
    except:
        pass

    try: #to get link for more info
        data['link'] = ele.find('a', {'class':'clearfix'})['href']
    except:
        pass

    return data

def from_devpostDotcom(keyword=None):
    if keyword:
        pass #will add this functionality later
    total = []
    page = requests.get('https://devpost.com/hackathons')
    count = 1
    while '<a class="button radius" data-browse-challenges="load-more" href="#">Load more hackathons</a>' in page.text:
        soup = BeautifulSoup(page.text, 'html.parser')
        relevant = soup.find('div', {'class':'challenge-results'})
        blocks = relevant.find_all('div', {'class':'row', 'data-browse-challenges':'challenge-listing'})
        for block in blocks:
            total.append(parse_devpostDotcom(block))

        count += 1
        page = requests.get('https://devpost.com/hackathons?page=%s' % count)

    return total

def parse_eventbriteDotie(ele):
    data = dict.fromkeys(metadata)
    data["source"] = "https://www.eventbrite.ie"

    try: #to get time
        time_list = ele.find('time', {'class':'list-card__date'}).get_text().strip().split('\n')
        time_list[1] = time_list[1].lstrip()
        data['time'] = ', '.join(time_list) #year ambiguity may arise as the data from the site doesn't mention year
    except:
        pass

    try: #to get title
        data['title'] = ele.find('div', {'class':'list-card__title'}).get_text().strip()
    except:
        pass

    try: #to get location
        data['location'] = ele.find('div', {'class':'list-card__venue'}).get_text().strip()
    except:
        pass

    try: #to get cost
        data['cost'] = ele.find('span', {'class':'list-card__label'}).get_text().strip()
    except:
        pass

    try: #to get tags
        tag_elements = ele.find('div', {'class':'list-card__tags'}).find_all('a')
        if tag_elements:
            data['tags'] = [anchor.get_text().strip().lstrip('#') for anchor in tag_elements] #removes the '#' as well
    except:
        pass

    try: #to get link
        data['link'] = ele.find('a', {'class':' list-card__main js-event-link js-xd-janus-checkpoint-link '})['href']
    except:
        pass

    return data

def from_eventbriteDotie(keyword=None):
    import json

    if keyword:
        pass #will add this functionality later

    page = requests.get('https://www.eventbrite.ie/d/worldwide/hackathon/?crt=regular&page=1&sort=best')
    count = 1
    total = []
    while 1:
        soup = BeautifulSoup(page.text, 'html.parser')
        checker = soup.find('div', {'class':'text-significant text-heading-secondary l-pad-bot-2 js-search-error-container'})
        if checker: #we have exhausted the available info
            break

        relevant = soup.find('div', {'data-automation':'event-list-container'}) #the event list
        blocks = relevant.find_all('div', {'class':'list-card-v2 l-mar-top-2 js-d-poster'}) #the individual events
        print('-'*33)
        print(count)
        for block in blocks:
            data = parse_eventbriteDotie(block)
            total.append(data)
            print(json.dumps(data, indent=4))
        count += 1
        page = requests.get('https://www.eventbrite.ie/d/worldwide/hackathon/?crt=regular&page=%s&sort=best' % count)

    return total
