import structlog
from celery import Celery
from sqlalchemy.exc import IntegrityError

import settings
from db.sync_orm_db import create_pymysql_engine, insert_data
from parsing.drom_parser import SyncDromParser

db_config = settings.get_db_config()
celery: Celery = Celery('hello', broker=settings.redis_dsn)
engine = create_pymysql_engine(db_config)


def _parse_page(parse_config: dict, page: int):
    _parser = SyncDromParser()
    _parser.parse(
        f"{parse_config['home_url']}/{parse_config['car_brand']}/page{page}/{parse_config['settings_url']}"
    )
    if _parser.resulting_dicts is None:
        return None
    return _parser.resulting_dicts


@celery.task()
def parse_and_add_data(parse_config: dict, page: int):
    result = _parse_page(parse_config, page)
    for line in result:
        try:
            insert_data(parse_config['db_table'], engine, line)
        except IntegrityError as exc:
            print(exc)
