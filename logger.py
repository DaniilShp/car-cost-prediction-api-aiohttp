import time
import shortuuid
import structlog
import logging
from aiohttp import web

import settings

TRACE_ID = 'trace_id'
DURATION = 'duration_time'


def init_logger():
    debug_mode = int(settings.debug_mode)
    logging.basicConfig(format="%(message)s", level=logging.ERROR)

    if debug_mode:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(sort_keys=False)
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )


@web.middleware
async def set_trace_id(request: web.Request, handler):
    logger = structlog.get_logger()
    trace_id = request.headers.get(TRACE_ID)
    if not trace_id:
        trace_id = shortuuid.uuid()
        logger.warn("Generated trace_id", trace_id=trace_id)
    structlog.contextvars.bind_contextvars(trace_id=trace_id)
    response = await handler(request)
    #response.headers[TRACE_ID] = trace_id
    return response


@web.middleware
async def request_log(request: web.Request, handler):
    logger = structlog.get_logger()
    logger.info(
        "Request",
        method=request.method,
        path=request.path,
    )
    try:
        response: web.Response = await handler(request)
    except Exception as exc:
        logger.exception(exc)
        raise
    logger.debug("Debug response", data=response.text)
    logger.info(
        "Response",
        status_code=response.status,
        content_length=response.content_length,
        exec_time=response.headers.get(DURATION)
    )
    return response


@web.middleware
async def duration_time(request: web.Request, handler):
    request['start_time'] = time.time()
    response = await handler(request)
    duration = round((time.time() - request["start_time"]), 3)
    response.headers[DURATION] = str(duration) + "s."
    return response


def get_logger_middlewares():
    return (
        set_trace_id,
        request_log,
        duration_time
    )
