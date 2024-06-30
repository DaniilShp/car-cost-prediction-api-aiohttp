from aiohttp import web
from db.routes import db_routes


async def init_db_sub_app():
    db_sub_app = web.Application()
    db_sub_app.add_routes(db_routes)
    return db_sub_app
