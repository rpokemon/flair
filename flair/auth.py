import random

import aiohttp
import aiohttp_session
from aiohttp import web

from flair.config import config as CONFIG
from flair.reddit import user_agent


async def generate_uri(request):
    session = await aiohttp_session.get_session(request)
    session['state'] = hex(random.getrandbits(20 * 8))[2:]
    return f'https://www.reddit.com/api/v1/authorize?client_id={CONFIG.REDDIT.APP.CLIENT_ID}&response_type=code&state={session["state"]}\
&redirect_uri={CONFIG.REDDIT.REDIRECT_URI}&duratioon=temporary&scope=identity'


async def validate_login(reddit, request):

    if 'code' not in request.query:
        raise web.HTTPUnauthorized

    async with aiohttp.ClientSession() as session:

        uri = 'https://www.reddit.com/api/v1/access_token'
        auth = aiohttp.BasicAuth(CONFIG.REDDIT.APP.CLIENT_ID, CONFIG.REDDIT.APP.CLIENT_SECRET)
        payload = {
            'grant_type': 'authorization_code',
            'code': request.query['code'],
            'redirect_uri': CONFIG.REDDIT.REDIRECT_URI,
        }

        # Retrive the oAuth token
        async with session.post(uri, auth=auth, data=payload) as response:
            result = await response.json()
            if 'access_token' not in result:
                raise web.HTTPUnauthorized
            token = result['access_token']

        uri = 'https://oauth.reddit.com/api/v1/me'
        headers = {
            'Authorization': 'Bearer ' + token,
            'User-Agent': user_agent
        }

        # Fetch the user's ID
        async with session.get(uri, headers=headers) as response:
            result = await response.json()
            return result['name']
