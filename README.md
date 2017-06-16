# hackathons-scrape
Scraping List of Hackathons all over the World

For a quick demo:

```
import json, scrapeHack
events = scrapeHack.from_hackathonDotio()
```
`from_hackathonDotcom()`, `from_challengerocketDotcom()` and `from_devpostDotcom()` can also be used

To print prettily:
```
print(json.dumps(events, indent=4))
```
Sample output:
```
[
    {
        "title": "Hackathon Lowpital 16 - 18 juin",
        "subtitle": null,
        "description": "Developers, designers, coders in the Paris area!  Are you interested in using technology to improve hospitals? Come and participate in Lowpital -- a low-tech hackathon.  Your challenge will be to create a simple, innovative solution that can incrementally improve the way hospitals operate.",
        "time": "16 Jun 2017",
        "location": "Paris, France",
        "tags": [
            "Health"
        ],
        "source": "http://www.hackathon.com",
        "link": "http://www.hackathon.com/event/hackathon-lowpital-16---18-juin-33850433558",
        "prize": null
    },
    {
        "title": "Hackathon vivatech - salon vivatechnology",
        "subtitle": null,
        "description": "Game changers, students, entrepreneurs, developers, hackers!  If you're an InsureTechie, or into AR/VR and AI. Or maybe you're a UX designer, a coder, or an idea generator!  Whatever you are, you're invited to participate in the Vivatech Hackathon.  It's a 25-hour marathon of product development, where the best ideas will emerge as a new product or service. Compete in one of four tracks for a chance to win a big cash prize.",
        "time": "16 Jun 2017",
        "location": "Paris, France",
        "tags": [
            "Fintech",
            "Industry",
            "Robotics",
            "Video Games"
        ],
        "source": "http://www.hackathon.com",
        "link": "http://www.hackathon.com/event/hackathon-vivatech---salon-vivatechnology-34594343613",
        "prize": null
    },
    {
        "title": "Hack & Shop - Hackathon Casino",
        "subtitle": null,
        "description": "Coders, designers, hackers in and around Paris!  Are you interested in retail apps?  Groupe Casino invites you to participate in their first Hack & Shop hackathon. You'll be challenged to design innovative new apps that recreate the shopping experience for consumers of all ages!  The sky's the limit -- you can look at any aspect of the consumer's shopping experience before, during, or after their visit to the store or website.",
        "time": "23 Jun 2017",
        "location": "Paris, France",
        "tags": [
            "IoT",
            "Retail",
            "Robotics",
            "Android",
            "IOS"
        ],
        "source": "http://www.hackathon.com",
        "link": "http://www.hackathon.com/event/hack-shop---hackathon-casino-33587759894",
        "prize": null
    }
]
```
