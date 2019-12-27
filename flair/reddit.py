import sys

import aiohttp
import praw

from flair.config import config as CONFIG


user_agent = 'rPokemonFlair (https://rpkmn.center/flair v1.0.0) Python/{0[0]}.{0[1]} aiohttp/{1} praw/{2} by the r/pokemon moderators'
user_agent = user_agent.format(
    sys.version_info, aiohttp.__version__, praw.__version__)

# Create the reddit instance
reddit = praw.Reddit(
    client_id=CONFIG.REDDIT.SCRIPT.CLIENT_ID,
    client_secret=CONFIG.REDDIT.SCRIPT.CLIENT_SECRET,
    user_agent=user_agent,
    username=CONFIG.REDDIT.USERNAME,
    password=CONFIG.REDDIT.PASSWORD,
)
