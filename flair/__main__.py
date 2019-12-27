import asyncio
import logging

from donphan import create_pool, create_tables, create_views

from flair.config import config as CONFIG
from flair import web


log = logging.getLogger(__name__)
log.setLevel(logging.getLevelName(CONFIG.LOGGING_LEVEL))

handler = logging.FileHandler(filename=f'{CONFIG.APP_NAME}.log')
handler.setFormatter(logging.Formatter(
    '{asctime} - {levelname} - {message}', style='{'))

log.addHandler(handler)
log.addHandler(logging.StreamHandler())

if __name__ == '__main__':
    log.info('Instance starting...')
    run = asyncio.get_event_loop().run_until_complete

    log.info('Setting up Database...')
    run(create_pool(CONFIG.DONPHAN.DSN, server_settings={
        'application_name': CONFIG.DONPHAN.APPLICATION_NAME}
    ))
    run(create_tables(drop_if_exists=CONFIG.DONPHAN.DELETE_TABLES_ON_STARTUP))
    run(create_views(drop_if_exists=CONFIG.DONPHAN.DELETE_VIEWS_ON_STARTUP))

    # Start the web server
    log.info('Setting up Web Server...')
    web.app.add_routes(web.routes)
    web.run_app(web.app, host=CONFIG.WEB.HOST, port=CONFIG.WEB.PORT)
