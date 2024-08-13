import base64
from aiohttp import web
from cryptography import fernet
from auth.routes import auth_routes
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage


async def init_auth_sub_app():
    auth_sub_app = web.Application()
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(auth_sub_app, EncryptedCookieStorage(secret_key))
    auth_sub_app.add_routes(auth_routes)
    return auth_sub_app
