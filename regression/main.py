import re

from aiohttp import web
from pathlib import Path
from regression.routes import regression_routes, create_regression_middleware, add_referer_middleware


not_ignore_urls = {
    re.compile(r'^/regression/linear/create_for_table_.*$'): 'GET',
    re.compile(r'^/regression/polynomial/create_for_table_.*$'): 'GET'
}

static_dir = Path(__file__).parent.joinpath('static')


async def init_regression_sub_app():
    regression_sub_app = web.Application(middlewares=[create_regression_middleware(not_ignore=not_ignore_urls), add_referer_middleware])
    regression_sub_app['referer'] = None
    regression_sub_app['static_dir'] = static_dir
    regression_sub_app.add_routes(regression_routes)
    return regression_sub_app
