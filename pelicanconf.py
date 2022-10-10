from datetime import datetime

AUTHOR = 'Josh Rzemien'
SITENAME = 'Josh Rzemien'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'America/Detroit'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

STATIC_PATHS = ['pdf']
# Blogroll
LINKS = (('Resume', '/pdf/Josh_Rzemien_Resume.pdf'),)

# Social widget
SOCIAL = (('linkedin', 'https://www.linkedin.com/in/joshuarzemien/'),
          ('github', 'https://github.com/joshrzemien'),)


COPYRIGHT_YEAR = datetime.now().year

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True