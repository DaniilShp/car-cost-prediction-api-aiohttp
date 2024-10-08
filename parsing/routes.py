from aiohttp import web

from auth.utils import login_required
from parsing.delayed_tasks import parse_and_add_data


parsing_routes = web.RouteTableDef()


@parsing_routes.get('')
async def index(request):
    return web.json_response(
        {
            'options': ['add_data_in_db', 'add_multidata_in_db']
        },
    )


@parsing_routes.post('/parse_page/{num:\d+}')
@login_required
async def add_data_in_db(request):
    page_num = request.match_info['num']
    parse_config = await request.json()
    parse_and_add_data.delay(parse_config, page_num)
    return web.json_response({"msg": "parsing have been started"})


@parsing_routes.post('/parse_page/{num_start:\d+}-{num_end:\d+}')
@login_required
async def add_multidata_in_db(request):
    page_start = request.match_info['num_start']
    page_end = request.match_info['num_end']
    parse_config = await request.json()
    for page_num in range(int(page_start), int(page_end) + 1):
        parse_and_add_data.delay(parse_config, page_num)
    return web.json_response({"msg": "parsing have been started"})
