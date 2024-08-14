from aiohttp import web
from auth.routes import auth_routes


async def init_auth_sub_app():
    auth_sub_app = web.Application()
    auth_sub_app.add_routes(auth_routes)
    return auth_sub_app
