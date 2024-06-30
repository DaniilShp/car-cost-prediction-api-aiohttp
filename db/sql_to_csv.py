import pandas as pd
import pymysql
from aiohttp import web
from sqlalchemy import create_engine


class SQLDataLoader:
    def __init__(self):
        self.dataframe = None
        self.local_path = None

    def create_dataframe(self, dbconfig, _sql: str, table_name: str):
        DSN = "mysql+pymysql://{user}:{password}@{host}/{database}".format(**dbconfig)
        engine = create_engine(url=DSN)
        try:
            with engine.connect() as conn:
                self.dataframe = pd.read_sql(_sql, con=conn)
        except pymysql.err.OperationalError:
            print("failed to load dataframe from DB. Try local file or update dbconfig.json")
        #self.local_path = os.path.join("data", f'dataframe_{table_name}.csv')
        #self.dataframe.to_csv(self.local_path, index=False)
        return self.dataframe


def load_dataframe_in_request(request: web.Request):
    table_name = request.match_info['name']
    db_config = request.config_dict['db_config']
    data_loader = SQLDataLoader()
    dataframe = data_loader.create_dataframe(db_config, f"select * from {table_name}", table_name)
    request['x'], request['y'] = dataframe[["production_year", "volume", "power", "mileage"]], dataframe["price"]