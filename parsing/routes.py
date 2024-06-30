from aiohttp import web
from parsing.drom_parser import parse_page
from db.async_orm_db import insert_data
from pymysql.err import IntegrityError

parsing_routes = web.RouteTableDef()


@parsing_routes.get('')
async def index(request):
    return web.json_response(
        {
            'options': ['add_data_in_db', 'add_multidata_in_db']
        },
    )


@parsing_routes.post('/parse_page/{num:\d+}')
async def add_data_in_db(request):
    page_num = request.match_info['num']
    parse_config = await request.post()
    result = await parse_page(request.config_dict['db_config'], parse_config, int(page_num))
    for line in result:
        try:
            await insert_data(parse_config['db_table'], request.config_dict['alchemy_engine'], line)
        except IntegrityError as exc:
            print(exc)
    return web.json_response(result)


@parsing_routes.post('/parse_page/{num_start:\d+}-{num_end:\d+}')
async def add_multidata_in_db(request):
    page_start = request.match_info['num_start']
    page_end = request.match_info['num_end']
    parse_config = await request.post()
    all_results = []
    for page_num in range(int(page_start), int(page_end) + 1):
        result = await parse_page(request.config_dict['db_config'], parse_config, page_num)
        all_results.append(result)
        for line in result:
            try:
                await insert_data(parse_config['db_table'], request.config_dict['alchemy_engine'], line)
            except IntegrityError as exc:
                print(exc)
    return web.json_response(all_results)
