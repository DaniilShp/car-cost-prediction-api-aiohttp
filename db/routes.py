import json
import sqlalchemy
from aiohttp import web
from pathlib import Path
from decimal import Decimal
from utils import remove_file, write_by_chunks
from db.async_orm_db import (
    create_table_if_not_exists, drop_table_if_exists,
    insert_data, get_table_structure, create_table_from_csv
)

db_routes = web.RouteTableDef()


def serialise_decimal(obj):
    if isinstance(obj, Decimal):
        str(obj)
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


@db_routes.get('')
async def index(request):
    return web.json_response(
        {
            'options': [
                'show_ids', 'show_info_by_id',
                'create_table', 'delete_table',
                'insert_line', 'create_table_by_csv_file'
            ]
        }
    )


@db_routes.get('/get_all_car_ids/{db_table}')
async def show_ids(request):
    name = request.match_info['db_table']
    engine = request.config_dict['alchemy_engine']
    _, tbl = get_table_structure(name)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(tbl.select().with_only_columns(tbl.c.car_id))
    except sqlalchemy.exc.ProgrammingError:
        return web.Response(text="error, incorrect table name")
    return web.json_response(json.dumps([int(row[0]) for row in result]))


@db_routes.get('/get_info_by_id/{db_table}/{car_id:\d+}')
async def show_info_by_id(request):
    name = request.match_info['db_table']
    car_id = int(request.match_info['car_id'])
    engine = request.config_dict['alchemy_engine']
    _, tbl = get_table_structure(name)
    try:
        async with engine.connect() as conn:
            res = await conn.execute(tbl.select().where(tbl.c.car_id == car_id))
            result = res.fetchall()[0]
    except (sqlalchemy.exc.ProgrammingError, IndexError):
        return web.Response(text="error, incorrect table name or car id")
    json_answer = {key: value for key, value in zip(res.keys(), result)}
    return web.json_response(json.dumps(json_answer, default=serialise_decimal))


@db_routes.post('/create_table_{name}')
async def create_table(request):
    name = request.match_info['name']
    engine = request.config_dict['alchemy_engine']
    table_existed = await create_table_if_not_exists(name, engine)
    if table_existed:
        return web.Response(text="exists")
    return web.Response(text="success")


@db_routes.delete('/delete_table_{name}')
async def delete_table(request):
    name = request.match_info['name']
    engine = request.config_dict['alchemy_engine']
    await drop_table_if_exists(name, engine)
    return web.Response(text="success")


@db_routes.put('/insert_line_in_table_{name}')
async def insert_line(request: web.Request):
    name = request.match_info['name']
    engine = request.config_dict['alchemy_engine']
    data = await request.post()
    await insert_data(name, engine, data)
    return web.Response(text="success")


@db_routes.post('/from_csv_create_table_{name}')
async def create_table_by_csv_file(request: web.Request):
    name = request.match_info['name']
    engine = request.config_dict['alchemy_engine']
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename
    tmp_file_location = Path(__file__).parent.joinpath('tmp', filename)
    with open(tmp_file_location, 'wb') as f:
        await write_by_chunks(f, field)
    await create_table_from_csv(name, engine, tmp_file_location)
    await remove_file(tmp_file_location)
    return web.json_response({'message': 'read file and created table'})
