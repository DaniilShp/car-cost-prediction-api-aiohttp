import os
import sys
import pytest
import aiohttp
from main import init_app


pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture
async def cli(aiohttp_client):
    app = await init_app()
    return await aiohttp_client(app)


async def test_create_table(cli: aiohttp.web.Application):
    resp = await cli.post('/db/create_table_test_cars')
    assert resp.status == 200


async def test_get_info_by_id(cli: aiohttp.web.Application):
    resp = await cli.get('/db/get_info_by_id/test_cars/22')
    assert resp.status == 200
    text = await resp.text()
    assert text is not None
    print(text)


async def test_insert_line(cli: aiohttp.web.Application):
    sample_data = {
        'car_id': 22, 'href': 'none', 'brand_model': 'bugatti chiron',
        'production_year': 2014, 'price': 1000, 'volume': 1.9, 'power': 1200,
        'gearbox_type': 'АКПП', 'mileage': 100
    }
    resp = await cli.put('/db/insert_line_in_table_test_cars', data=sample_data)
    assert resp.status == 200


async def test_show_car_ids(cli: aiohttp.web.Application):
    resp = await cli.get('/db/get_all_car_ids/test_cars')
    assert resp.status == 200
    text = await resp.text()
    assert text is not None
    print(text)


async def test_delete_table(cli: aiohttp.web.Application):
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd()))))
    resp = await cli.delete('/db/delete_table_test_cars')
    assert resp.status == 200


async def test_create_table_by_csv(cli: aiohttp.web.Application):
    url = '/db/from_csv_create_table_test_cars'
    file_path = 'C:\\Users\\Danil\\PycharmProjects\\car_cost_prediction_api\\db\\tests\\dataframe_toyota_cars.csv'
    file = {
        'file': open(file_path, 'rb'),
    }
    resp = await cli.post(url, data=file)
    assert resp.status == 200
    await test_delete_table(cli)


if __name__ == '__main__':
    pass
