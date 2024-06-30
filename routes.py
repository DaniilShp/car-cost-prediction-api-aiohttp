from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/')
async def info(request):
    return web.json_response([{'options': 'db'}, {'options': 'parsing'}, {'options': 'regression'}])
