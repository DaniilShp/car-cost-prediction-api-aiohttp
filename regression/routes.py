import pandas as pd
from uuid import uuid4
from typing import Union
from aiohttp import web
from aiohttp_middlewares.annotations import Handler, Urls, Middleware
from aiohttp_middlewares.utils import match_request
from db.sql_to_csv import load_dataframe_in_request
from regression.linear_regression_model import linear_regression_create
from regression.polynomial_regression_model import polynomial_regression_create, predict as polynomial_predict

regression_routes = web.RouteTableDef()


def create_regression_middleware(not_ignore: Union[Urls, None] = None) -> Middleware:
    @web.middleware
    async def middleware(request: web.Request, handler: Handler):
        request_method = request.method
        request_path = request.path
        if not match_request(not_ignore, request_method, request_path):
            response = await handler(request)
            return response
        print('Middleware called')
        load_dataframe_in_request(request)
        response = await handler(request)
        return response

    return middleware


@web.middleware
async def add_referer_middleware(request: web.Request, handler: Handler):
    response = await handler(request)
    request.app['referer'] = str(request.path)
    return response


@regression_routes.get('')
async def info(request):
    return web.json_response(
        {
            'handler': [
                'info', 'get_static_image', 'download_image',
                'create_linear_regression', 'create_polynomial_regression'
            ],
            'path': [
                '/regression', '/regression/static/{path}',
                '/regression/download/{path}',
                '/regression/linear/create_for_table_{name}',
                '/regression/polynomial/create_for_table_{name}'
            ],
            'description': [
                'list of regression module options', 'plots with info about created regression model',
                'link to download plots', 'create linear regression model',
                'create polynomial regression model'
            ]
        }
    )


@regression_routes.get('/static/{path}')
async def get_static_image(request):
    path = request.match_info['path']
    static_dir = request.app['static_dir']
    return web.FileResponse(static_dir.joinpath(path))


@regression_routes.get('/download/{path}')
async def download_image(request):
    path = request.match_info['path']
    static_dir = request.app['static_dir']
    return web.FileResponse(static_dir.joinpath(path), headers={'Content-Disposition': 'attachment'})


@regression_routes.get('/linear/create_for_table_{name}')
async def create_linear_regression(request):
    x, y = request['x'], request['y']
    static_dir = request.app['static_dir']
    barplot_path, scatterplot_path = static_dir.joinpath(str(uuid4()) + '.png'), static_dir.joinpath(
        str(uuid4()) + '.png')
    model, response = linear_regression_create(x, y, barplot_path, scatterplot_path)
    request.app['linear_model'] = model
    return web.json_response(response)


@regression_routes.post('/linear/predict')
async def predict_price_linear_model(request):
    data = await request.json()
    try:
        df = pd.DataFrame(data)
    except ValueError:
        df = pd.DataFrame.from_dict(data, orient='index').T
    pred = request.app['linear_model'].predict(df)
    return web.Response(text=str(pred[0]))


@regression_routes.get('/polynomial/create_for_table_{name}')
async def create_polynomial_regression(request):
    x, y = request['x'], request['y']
    static_dir = request.app['static_dir']
    barplot_path, scatterplot_path = static_dir.joinpath(str(uuid4()) + '.png'), static_dir.joinpath(
        str(uuid4()) + '.png')
    n = int(request.rel_url.query.get('n', '3'))
    model, response = polynomial_regression_create(x, y, barplot_path, scatterplot_path, degree=n)
    request.app['polynomial_model'] = model
    return web.json_response(response)


@regression_routes.post('/polynomial/predict')
async def predict_price_polynomial_model(request):
    data = await request.json()
    try:
        df = pd.DataFrame(data)
    except ValueError:
        df = pd.DataFrame.from_dict(data, orient='index').T
    pred = polynomial_predict(request.app['polynomial_model'], df)
    return web.Response(text=str(pred))
