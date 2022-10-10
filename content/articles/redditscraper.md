Title: Using PRAW and PSAW to gather data about Reddit reposts and automate complaining about them
Date: 2022-05-03 08:00
Modified: 2022-05-03 08:00
Category: Projects
Tags: praw, python, psaw, reddit, regex
Slug: reddit-repost-bot

## The Idea
If you are like me, you occasionally browse Reddit's /r/videos and come across a video that you swear you have seen posted on the subreddit dozens of times. You may then ask yourself, why would you post this? Well, I can't answer that. We can, however, determine how many times it has been posted and inform the user about their egregious error.

## The Tools
For this project, I used the following tools:
- pandas, to interact with the data
- python reddit api wrapper, to monitor submissions in real time and post replies
- pushshift.io api wrapper, to pull historical data about subreddit submissions from pushshift.io
- regex, to isolate the youtube video id from the submission url (many of these were god awful abominations)

## The Code
Start with my imports and connecting to the API. Set search criteria. For this, I set the karma limit to 50 in order to limit the amount of data, bad posts, spam, etc. Realistically, a decent amount of reposts probably do have under 50 karma, but for now I will keep the limit. The final line here takes quite a while and returned over 170k results. 
```python
import pandas as pd
from psaw import PushshiftAPI

api = PushshiftAPI()
api_request_generator = api.search_submissions(subreddit='videos', score = ">50")
submissions = pd.DataFrame([submission.d_ for submission in api_request_generator])
```

The vast majority of posts to the subreddit are youtube links, so for now I am just focusing on those and ignoring all other urls. Youtube video urls are *supposed* to be simple. For a variety of reasons, the url text that the average redditor ends up copy and pasting into the link field on a reddit submission has tons of garbage in it. Because I am looking for reposts, these differences could potentially cause fewer reposts to appear in the results. If I can filter out all unwanted parts of the url, I will be left with the id. Regex is a great tool for this. I was able to find a semi complete solution for this on Stack Overflow, but it did require a few tweaks to support all of the potential variants that I encountered in the data. I used https://regex101.com/ to verify that all of my urls were being processed correctly.
```python
regex = r'^(?:https?:)?(?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]{7,15})(?:[\?&][a-zA-Z0-9\_-]+=[a-zA-Z0-9\_-]+)*(?:[&\/\#].*)?$'

repl = lambda m: m.group(1)
submissions['youtube_id'] = submissions['url'].str.replace(regex, repl)
```

The Reddit API has a ton of fields that I am not interested in, so I selected only the useful data. 
```python
data = submissions[['title','author','full_link','url','youtube_id','created_utc','num_comments','num_crossposts']]
```

Finally, I added a column for the number of times each youtube id is found in the data and convert the unix timestamp to a more readable format. That is all I needed for now, so I saved it to a csv.
```python
data['num_reposts'] = data['youtube_id'].map(data['youtube_id'].value_counts().to_dict())
data['created_date'] = pd.to_datetime(data['created_utc'], utc=True, unit='s')
data.to_csv('data.csv')
```

Now that I have the historical data, I can reference it whenever someone submits something to the subreddit and determine if it is a repost. This is pretty simple in PRAW. Start with the imports and starting PRAW and pointing it to the correct subreddit.
```python
import praw
import pandas as pd
import re
import csv

reddit = praw.Reddit(
    client_id="clientid",
    client_secret="secret",
    user_agent="agent",
    username="username",
    password="password"
)

subreddit = reddit.subreddit('videos')
```

I want to be sure that I don't enable replies until I am ready so that I don't accidentally post a bunch of spam comments and get banned. Next I want to load a csv that contains all of the post ids that the bot has already processed. This is another spam prevention method. Next, I read the data from the previous step into a dataframe and define the same regex. 
```python
replies_enabled = False

with open('processed.csv') as f:
    reader = csv.reader(f)
    processed = []
    for row in reader:
        for item in row:
            processed.append(item)

df = pd.read_csv('data.csv')
regex = r'^(?:https?:)?(?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]{7,15})(?:[\?&][a-zA-Z0-9\_-]+=[a-zA-Z0-9\_-]+)*(?:[&\/\#].*)?$'
```

This is the main part of the bot. Praw will iterate through current submissions and monitor for future submissions. If the submission has not already been processed, I apply the regex to the submitted url to get the youtube_id. Then I look up the youtube_id in the original dataset, returning only the value of num_reposts. Regardless of that result, the post id is added to the csv. If the number of reposts is greater than 2, I print a small summary of the post and post a reply to the submission. 
```python
for submission in subreddit.stream.submissions():
    if submission.id not in processed:
        submission_youtube_id = re.sub(regex, r'\1',submission.url)
        try:
            num_reposts = df['num_reposts'].loc[df['new_url'].str.contains(submission_youtube_id)].iloc[0]
        except:
            num_reposts = 0
        with open('processed.csv','a') as fd:
            fd.write(','+submission.id)
        if num_reposts > 2:
            print('repost alert',submission.id, submission.title, submission.url, submission_youtube_id, submission.permalink, num_reposts)
            if replies_enabled:
                submission.reply('Seen this video before? This video has been submitted to /r/videos at least '+str(num_reposts)+' times.')
```

## The Outcome
I spun up an ubuntu VM on my home server and deployed the bot. Honestly, I fully expect it to get banned from the subreddit after a few comments. This was a small/quick/fun project that gave me a chance to check out the basic features of PRAW/PSAW. They were both extremely easy to get started with. I will definitely be returning to these tools in future projects. I am also really happy with how well the regex worked on such a large dataset. The amount of data that the reddit API gives you opens up a lot of possibilites for these types of bots. You could easily adapt this bot into a karma farming repost bot. I think there are also quite a few ways that I could reduce the likelihood that my account gets banned, but it wouldn't be worth it at this point.