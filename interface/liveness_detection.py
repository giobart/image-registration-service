import aiohttp
import asyncio
from config import *
from aiohttp import ClientSession


async def liveness_detection_check(frames):
    try:
        response = await ClientSession().request(method='POST', url=LIVENESS_SERVICE_URL+"/liveness_check", json={'frames': frames})
        response.raise_for_status()
    except Exception as err:
        print(f"An error ocurred: {err}")
    response_json = await response.json()
    return bool(response_json['result'])


