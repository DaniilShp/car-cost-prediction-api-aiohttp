from celery import Celery
from sqlalchemy.exc import IntegrityError
from db.sync_orm_db import create_pymysql_engine, insert_data
from parsing.drom_parser import SyncDromParser
from settings import get_db_config

db_config = get_db_config()
celery: Celery = Celery('hello', broker="redis://localhost:6379/0")
engine = create_pymysql_engine(db_config)


def _parse_page(parse_config: dict, page: int):
    _parser = SyncDromParser()
    _parser.parse(
        f"{parse_config['home_url']}/{parse_config['car_brand']}/page{page}/{parse_config['settings_url']}"
    )
    print(page)
    if _parser.resulting_dicts is None:
        return None
    return _parser.resulting_dicts


@celery.task()
def parse_and_add_data(parse_config: dict, page: int):
    result = _parse_page(parse_config, page)
    print(result)
    for line in result:
        try:
            insert_data(parse_config['db_table'], engine, line)
        except IntegrityError as exc:
            print(exc)


