import asyncio
import time
import aiohttp_debugtoolbar
import logging
import base64

import structlog
from aiohttp import web
from aiohttp_swagger import *
from aiohttp_middlewares import timeout_middleware, error_middleware
from cryptography import fernet
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

import routes
import settings
from logger import get_logger_middlewares, init_logger
from utils import directory_cleanup_middleware
from parsing.main import init_parsing_sub_app
from regression.main import init_regression_sub_app, static_dir
from db.main import init_db_sub_app
from auth.main import init_auth_sub_app
from db.async_orm_db import mysql_context


middlewares_list = (
    error_middleware(),
    timeout_middleware(30),
    directory_cleanup_middleware(static_dir, 10, 10),
    *get_logger_middlewares()
)


async def init_app():
    init_logger()
    parsing_sub_app = await init_parsing_sub_app()
    regression_sub_app = await init_regression_sub_app()
    db_sub_app = await init_db_sub_app()
    auth_sub_app = await init_auth_sub_app()
    app = web.Application(middlewares=middlewares_list)
    aiohttp_debugtoolbar.setup(app)
    setup_swagger(app)
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))
    app.add_routes(routes.routes)
    app['db_config'] = settings.get_db_config()
    app['cleanup_time_check'] = time.time()
    app.cleanup_ctx.append(mysql_context)
    app.add_subapp(prefix='/parsing/', subapp=parsing_sub_app)
    app.add_subapp(prefix='/regression/', subapp=regression_sub_app)
    app.add_subapp(prefix='/db/', subapp=db_sub_app)
    app.add_subapp(prefix='/auth/', subapp=auth_sub_app)
    return app


def main():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    host, port = settings.listen.split(':')
    port = int(port)
    web.run_app(app, access_log=None, host=host, port=port, access_log_format='%a %t "%r" %s %Tfs.')


if __name__ == '__main__':
    main()
