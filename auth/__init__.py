import structlog
from sqlalchemy import inspect

import settings
from db.async_orm_db import create_alchemy_engine
from .users import User as UserTable
from .users import create_user_table


async def init_user_table():
    db_config = settings.get_db_config()
    engine = create_alchemy_engine(db_config)
    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
    if UserTable.name in tables:
        return  # table already exists
    await create_user_table(engine)
    logger = structlog.get_logger()
    logger.info("User table created")
