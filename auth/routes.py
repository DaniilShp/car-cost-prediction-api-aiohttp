from aiohttp import web
from aiohttp_session import get_session, new_session
from auth.utils import login_required
from auth.users import register_user, check_password

auth_routes = web.RouteTableDef()


@auth_routes.get('')
async def index(request):
    return web.json_response(
        {
            'options': ['register', 'login', 'logout']
        },
    )


@auth_routes.post('/register')
async def register(request: web.Request):
    engine = request.config_dict['alchemy_engine']
    user_data = await request.json()
    await register_user(engine, user_data)
    return web.json_response({'message': 'registered'})


@auth_routes.post('/login')
async def login(request: web.Request):
    engine = request.config_dict['alchemy_engine']
    session = await get_session(request)
    user_data = await request.json()
    l, p = user_data['login'], user_data['password']
    privileges = await check_password(engine, l, p)
    if privileges is None:
        return web.json_response({"message": "incorrect login or password"})
    payload = {'login': l, 'password': p, 'privileges': privileges}
    session['user_data'] = payload
    return web.json_response({'message': 'success'})


@auth_routes.get('/logout')
@login_required
async def logout(request: web.Request):
    session = await get_session(request)
    session.clear()
    return web.json_response({'message': 'logout'})
