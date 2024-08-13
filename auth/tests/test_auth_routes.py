import json
import pytest
import aiohttp

from main import init_app


pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture
async def cli(aiohttp_client):
    app = await init_app()
    return await aiohttp_client(app)


async def test_log_in(cli: aiohttp.web.Application):
    resp = await cli.post('/auth/log_in', data=json.dumps({'login': 'not_admin', 'password': '0000'}))
    assert resp.status == 200


if __name__ == '__main__':
    pytest.main()
