import json
import pytest
import aiohttp
import main

pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture
async def cli(aiohttp_client):
    app = await main.init_app()
    return await aiohttp_client(app)


async def test_create_linear_regression_and_predict_price(cli: aiohttp.web.Application):
    resp = await cli.get('/regression/linear/create_for_table_toyota_cars')
    assert resp.status == 200
    text = await resp.text()
    print(text)
    assert text is not None
    data = {'production_year': 2020, 'volume': 3.5, 'power': 250, 'mileage': 12000}
    resp = await cli.post('/regression/linear/predict', data=json.dumps(data))
    assert resp.status == 200
    text = await resp.text()
    assert text is not None
    print(text)


async def test_create_polynomial_regression_and_predict_price(cli: aiohttp.web.Application):
    resp = await cli.get('/regression/polynomial/create_for_table_toyota_cars')
    assert resp.status == 200
    text = await resp.text()
    print(text)
    assert text is not None
    data = [{"production_year": 2020, "volume": 3.5, 'power': 250, 'mileage': 12000},
            {'production_year': 2020, 'volume': 3.5, 'power': 250, 'mileage': 120000}]
    resp = await cli.post('/regression/polynomial/predict', data=json.dumps(data))
    assert resp.status == 200
    text = await resp.text()
    assert text is not None
    print(text)


if __name__ == '__main__':
    pass
