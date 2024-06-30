from aiohttp import web
from parsing.routes import parsing_routes


async def init_parsing_sub_app():
    parsing_sub_app = web.Application()
    parsing_sub_app.add_routes(parsing_routes)
    return parsing_sub_app
