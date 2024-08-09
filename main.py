import asyncio
import time
import aiohttp_debugtoolbar
import logging
from aiohttp import web
from aiohttp_swagger import *
from aiohttp_middlewares import timeout_middleware, error_middleware
from settings import get_db_config
import routes
from utils import directory_cleanup_middleware
from parsing.main import init_parsing_sub_app
from regression.main import init_regression_sub_app, static_dir
from db.main import init_db_sub_app
from db.async_orm_db import mysql_context


middlewares_list = [
    error_middleware(),
    timeout_middleware(30),
    directory_cleanup_middleware(static_dir, 10, 10)
]


async def init_app():
    logging.basicConfig(level=logging.INFO)
    parsing_sub_app = await init_parsing_sub_app()
    regression_sub_app = await init_regression_sub_app()
    db_sub_app = await init_db_sub_app()
    app = web.Application(middlewares=middlewares_list)
    aiohttp_debugtoolbar.setup(app)
    setup_swagger(app)
    app.add_routes(routes.routes)
    app['db_config'] = get_db_config()
    app['cleanup_time_check'] = time.time()
    app.cleanup_ctx.append(mysql_context)
    app.add_subapp(prefix='/parsing/', subapp=parsing_sub_app)
    app.add_subapp(prefix='/regression/', subapp=regression_sub_app)
    app.add_subapp(prefix='/db/', subapp=db_sub_app)
    return app


def main():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, host='127.0.0.1', port=8081, access_log_format='%a %t "%r" %s %Tfs.')


if __name__ == '__main__':
    main()
