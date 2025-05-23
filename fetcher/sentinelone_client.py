from aiohttp import ClientSession
from .config import AUTH_HEADER

async def fetch_json(method: str, url: str, *, params=None, json=None, HEADER=AUTH_HEADER):
    async with ClientSession() as session:
        async with session.request(method, url, headers=HEADER, params=params, json=json) as resp:
            data = await resp.json()
            return resp.status, data
