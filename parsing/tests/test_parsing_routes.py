import pytest
import aiohttp
import main

pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture
async def cli(aiohttp_client):
    app = await main.init_app()
    return await aiohttp_client(app)


@pytest.fixture
async def db(cli: aiohttp.web.Application):
    db_name = 'test_cars'
    await cli.post(f'/db/create_table_{db_name}')
    yield
    await cli.delete(f'/db/delete_table_{db_name}')


async def test_page_parse_handler(cli: aiohttp.web.Application, db):
    data = {
        "car_brand": "toyota/camry",
        "db_table": "test_cars",
        "home_url": "https://auto.drom.ru",
        "settings_url": "?minyear=2010&maxyear=2020&mv=0.7&ph=1&pts=2&damaged=2&minpower=1&minprobeg=1"
    }
    resp = await cli.post('/parsing/parse_page/1', data=data)
    assert resp.status == 200
    text = await resp.text()
    print(text)
    assert text is not None


async def test_multipage_parse_handler(cli: aiohttp.web.Application, db):
    data = {
        "car_brand": "toyota/camry",
        "db_table": "test_cars",
        "home_url": "https://auto.drom.ru",
        "settings_url": "?minyear=2010&maxyear=2020&mv=0.7&ph=1&pts=2&damaged=2&minpower=1&minprobeg=1"
    }
    resp = await cli.post('/parsing/parse_page/5-7', data=data)
    assert resp.status == 200
    text = await resp.text()
    print(text)
    assert text is not None


if __name__ == '__main__':
    pass
