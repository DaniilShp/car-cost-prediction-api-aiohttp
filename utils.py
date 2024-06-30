import asyncio
import os
import time
from typing import Union, BinaryIO

from aiohttp import web, BodyPartReader, MultipartReader


def directory_cleanup_middleware(directory, check_interval, file_lifetime):
    @web.middleware
    async def middleware(request: web.Request, handler):
        if time.time() - request.app['cleanup_time_check'] > check_interval:
            request.app['cleanup_time_check'] = time.time()
            await cleanup_directory(directory, file_lifetime)
        return await handler(request)
    return middleware


async def remove_file(file_path):
    try:
        await asyncio.to_thread(os.remove, file_path)
        print(f"File {file_path} removed successfully")
    except FileNotFoundError:
        print(f"File {file_path} not found")


async def cleanup_directory(directory, file_lifetime):
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            creation_time = os.path.getctime(file_path)
            if current_time - creation_time > file_lifetime:
                await remove_file(file_path)


async def write_by_chunks(file: BinaryIO, field: Union[MultipartReader, BodyPartReader]):
    """fully write file by given file descriptor and chunks source"""
    while True:
        chunk = await field.read_chunk()
        if not chunk:
            break
        file.write(chunk)
