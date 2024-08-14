from aiohttp import web
from aiohttp_session import get_session
from typing import Any, Awaitable, Callable, Optional

from auth.users import check_password

_Handler = Callable[
    [web.Request, Optional[list], Optional[dict]],
    Awaitable[web.StreamResponse]
]


def login_required(handler_func: _Handler) -> _Handler | web.json_response:
    async def wrapped(
            request: web.Request, *args: Any, **kwargs: Any
    ) -> web.StreamResponse:
        session = await get_session(request)
        if session.empty:
            return web.json_response({'msg': 'not authorized'})
        engine = request.config_dict['alchemy_engine']
        if not check_password(engine, session['user_data']['login'], session['user_data']['password']):
            raise web.HTTPFound('/log_out')
        return await handler_func(request, *args, **kwargs)

    return wrapped


def privileges_required(handler_func: _Handler, rights_class: int = 0) -> _Handler:
    async def wrapped(
            request: web.Request, *args: Any, **kwargs: Any
    ) -> web.StreamResponse:
        session = await get_session(request)
        if "user_data" not in session:
            raise web.HTTPFound('/auth')
        if session['user_data']['privileges'] < rights_class:
            # some redirect
            pass
        return await handler_func(request, *args, **kwargs)

    return wrapped
