import httpx
import random

def getProxy():
    port = random.randint(9000, 9300)
    return {
        'server': f'http://proxy.soax.com:{port}',
        'username': 'h9qINUrIK8Tq3R7f',
        'password': 'mobile;tw;;;'
    }

def soax():
    port = random.randint(9000, 9300)
    return {
        f'http://': f'http://h9qINUrIK8Tq3R7f:mobile;tw;;;@proxy.soax.com:{port}',
        f'https://': f'http://h9qINUrIK8Tq3R7f:mobile;tw;;;@proxy.soax.com:{port}'
    }

async def goto(url, method='get', headers=None, json=None, proxy=False, http2=False):
    proxies = None
    if proxy:
        proxies = soax()
    async with httpx.AsyncClient(http2=http2, proxies=proxies) as client:
        return await client.request(url=url, method=method, headers=headers, json=json, timeout=30)