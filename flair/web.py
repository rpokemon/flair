from aiohttp import web
import jinja2
import aiohttp_jinja2
import aiohttp_session
import aiohttp_security

from prawcore.exceptions import NotFound

from flair.auth import generate_uri, validate_login
from flair.config import config as CONFIG
from flair.database import UserBallFlairs
from flair.storage import PostgresStorage
from flair.reddit import reddit


async def get_data(request):

    data_proxy = await request.post()
    data = data_proxy.copy()

    arrays = set(key[:-2] for key in data if key.endswith('[]'))

    for array in arrays:
        data[array] = list()
        while array + '[]' in data:
            data[array].append(data.pop(array + '[]'))

    return data


class Reddit_AuthorizationPolicy(aiohttp_security.AbstractAuthorizationPolicy):

    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        try:
            redditor = reddit.redditor(identity)
            redditor.id
            return redditor
        except NotFound:
            return None

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """

        redditor = await self.authorized_userid(identity)
        subreddit = reddit.subreddit(CONFIG.SUBREDDIT)

        if permission == 'subreddit_mod':
            return redditor in subreddit.moderator()


# Shortcuts
check_authorized = aiohttp_security.check_authorized
check_permission = aiohttp_security.check_permission
get_user = aiohttp_security.authorized_userid
get_session = aiohttp_session.get_session
run_app = web.run_app

# Setup base app configuration
app = web.Application()

# Setup session
storage = PostgresStorage()
aiohttp_session.setup(app, storage)

# Setup security
policy = aiohttp_security.SessionIdentityPolicy()
aiohttp_security.setup(app, policy, Reddit_AuthorizationPolicy())

# Setup routes
routes = web.RouteTableDef()
routes.static('/flair/static', 'flair/static', show_index=True)
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(
    CONFIG.WEB.TEMPLATE_DIR))


@routes.get('/flair')
@aiohttp_jinja2.template('index.jinja2')
async def index(request):
    try:
        redditor = await check_authorized(request)
        return {'CONFIG': CONFIG, 'redditor': redditor, 'flairs': []}
    except web.HTTPUnauthorized:
        auth_uri = await generate_uri(request)
        raise web.HTTPFound(auth_uri)


@routes.get('/flair/login')
async def auth_login(request):

    # Check state
    session = await get_session(request)
    if request.query.get('state', False) != session.get('state'):
        raise web.HTTPBadRequest()

    # Validate user ID
    user_id = await validate_login(reddit, request)

    # TODO: Redirect to last page

    redirect_response = web.HTTPFound('/flair')
    await aiohttp_security.remember(request, redirect_response, user_id)
    raise redirect_response


@routes.get('/flair/logout')
async def auth_logout(request):
    # Log user out
    redirect_response = web.HTTPFound('https://pokemon.reddit.com')
    await aiohttp_security.forget(request, redirect_response)
    raise redirect_response


@routes.post('/flair/set')
async def set_flair(request):
    redditor = await check_authorized(request)
    data = await get_data(request)

    print(data)

    keys = ('subreddits', 'text', 'css_class')
    if not all(key in keys for key in data):
        raise web.HTTPBadRequest()

    if len(data['text']) > 64:
        raise web.HTTPBadRequest()

    if not UserBallFlairs.is_valid_flair(data['css_class']):
        raise web.HTTPBadRequest()

    # Set ballflair if user has one
    ballflair = UserBallFlairs.get_ballflair(redditor)
    if ballflair is not None:
        data['css_class'] += ' ' + ballflair

    for subreddit in data.pop('subreddits'):
        reddit.subreddit(subreddit).flair.set(redditor, **data)

    return web.HTTPFound('https://pokemon.reddit.com')
