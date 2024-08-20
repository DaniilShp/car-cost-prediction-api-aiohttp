import os
import dotenv
import structlog

dotenv.load_dotenv(dotenv_path=".env")

listen = os.environ.get('LISTEN')
debug_mode = os.environ.get('DEBUG_MODE')
log_level = os.environ.get('LOG_LEVEL')
redis_dsn = os.environ.get('REDIS_DSN')


def get_db_config():
    dbconfig = {
        'host': os.environ.get('MYSQl_HOST'),
        'user': os.environ.get('MYSQL_USER'),
        'password': os.environ.get('MYSQL_PASSWORD'),
        'database': os.environ.get('MYSQL_DATABASE')
    }
    return dbconfig


logger = structlog.get_logger()
logger.debug("load settings")
