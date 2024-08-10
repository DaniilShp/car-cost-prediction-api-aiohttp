from sqlalchemy import create_engine, Engine
from db.async_orm_db import get_table_structure


def create_pymysql_engine(db_config):
    DSN = "mysql+pymysql://{user}:{password}@{host}/{database}".format(**db_config)
    engine = create_engine(url=DSN)
    return engine


def insert_data(table_name, engine: Engine, data):
    _, tbl = get_table_structure(table_name)
    with engine.begin() as conn:
        conn.execute(tbl.insert().values(**data))
