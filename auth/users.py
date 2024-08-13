from passlib.hash import sha256_crypt
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import MetaData, Table, Column, Integer, String, select

metadata = MetaData()
User = Table(
    'users', metadata,
    Column('login', String(30), primary_key=True, index=True),
    Column('password', String(66)),
    Column('privileges', Integer)
)


async def create_user_table(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def register_user(engine: AsyncEngine, new_user_data: dict):
    async with engine.begin() as conn:
        new_user_data['password'] = sha256_crypt.hash(new_user_data['password'])
        await conn.execute(User.insert().values(**new_user_data))


async def check_password(engine, login, password):
    async with engine.begin() as conn:
        result = await conn.execute(
            select(User.c.user_id, User.c.login, User.c.password, User.c.privileges).where(
                User.c.login == str(login)
            )
        )
        row = result.fetchone()
        if row:
            if sha256_crypt.verify(password, row[1]):
                return int(row[2])
