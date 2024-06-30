import aiomysql.sa
import sqlalchemy.ext.asyncio
from sqlalchemy import MetaData, Table, Column, Integer, String, Numeric, inspect, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from functools import lru_cache


@lru_cache(maxsize=1)
def get_table_structure(table_name: str):
    metadata = MetaData()
    my_table = Table(table_name, metadata,
                     Column('car_id', Integer, primary_key=True),
                     Column('brand_model', String(30)),
                     Column('mileage', Integer),
                     Column('gearbox_type', String(30)),
                     Column('power', Integer),
                     Column('price', Integer),
                     Column('volume', Numeric(precision=2, scale=1)),
                     Column('href', String(80)),
                     Column('production_year', Integer))
    return metadata, my_table


async def create_table_if_not_exists(table_name: str, engine: sqlalchemy.ext.asyncio.AsyncEngine):
    metadata, _ = get_table_structure(table_name)
    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
    if table_name in tables:
        return True  # table existed
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    return False


async def drop_table_if_exists(table_name: str, engine: sqlalchemy.ext.asyncio.AsyncEngine):
    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
    if table_name not in tables:
        return None
    _, tbl = get_table_structure(table_name)
    async with engine.begin() as conn:
        await conn.run_sync(tbl.drop)


async def create_aiomysql_engine(db_config: dict):
    db_config_new = db_config.copy()
    db_config_new.pop('database')
    db_config_new['db'] = db_config['database']
    engine = await aiomysql.sa.create_engine(**db_config_new)
    return engine


def create_alchemy_engine(db_config: dict):
    DSN = "mysql+aiomysql://{user}:{password}@{host}/{database}".format(**db_config)
    engine = create_async_engine(url=DSN)
    return engine


async def mysql_context(app):
    app['alchemy_engine'] = create_alchemy_engine(app['db_config'])
    # async_engine = await create_aiomysql_engine(app['db_config'])
    # app['aiomysql_engine'] = async_engine

    yield

    await app['alchemy_engine'].dispose()
    # app['aiomysql_engine'].close()
    # await app['aiomysql_engine'].wait_closed()
    # await asyncio.sleep(1)


async def select_data(engine: sqlalchemy.ext.asyncio.AsyncEngine, sql_query):
    query_executable = text(sql_query)
    async with engine.connect() as conn:
        await conn.execute(query_executable)


async def insert_data(table_name, engine: sqlalchemy.ext.asyncio.AsyncEngine, data):
    _, tbl = get_table_structure(table_name)
    async with engine.begin() as conn:
        await conn.execute(tbl.insert().values(**data))


async def create_table_from_csv(table_name, engine: sqlalchemy.ext.asyncio.AsyncEngine, csv_file):
    import csv
    if await create_table_if_not_exists(table_name, engine):
        print('existed')
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        keys = next(reader)
        _, tbl = get_table_structure(table_name)
        async with AsyncSession(engine) as session:
            async with session.begin():
                for values_line in reader:
                    data = {key: value for key, value in zip(keys, values_line)}
                    await session.execute(tbl.insert().values(**data))
                await session.commit()
