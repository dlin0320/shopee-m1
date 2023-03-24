import asyncio
from playwright.async_api import async_playwright, Response
from shopee.shopee import SearchPayload, SearchResult
from shopee.shopee import Shopee as s
from utilities.proxy import goto
from typing import List
import logging

DEFAULT_TIMEOUT = 6000
# //div[@class="src-components-modals-upgrade-shopads---footer--1VgFZ"]/button
# //div[@class="mass-edit-tip"]/button
# //div[@class="shopee-popper shopee-popover__popper shopee-popover__popper--light with-arrow custom-popover-class btn-popper-class"]/div/div/div/button

# PW actions
async def shopeeLogin(os: str, dir: str):
    # TODO get SPC_CDS and add refresh mechanism
    async with async_playwright() as pw:
        try:
            user_data_dir = dir
            if os.__contains__('mac'):
                browser = await pw.chromium.launch_persistent_context(user_data_dir, headless=False, channel='chrome')
            elif os.__contains__('windows'):
                browser = await pw.chromium.launch_persistent_context(user_data_dir, headless=False)
            else:
                raise Exception('bad os')
            page = browser.pages[0]
            await page.goto(s.portal)
            for _ in range(100):
                id = None
                try:
                    id = await (await page.wait_for_selector('//span[@class="subaccount-name"]', timeout=3000)).inner_text()
                    if id != None:
                        break
                except Exception as e:
                    try:
                        id = await (await page.wait_for_selector('//span[@class="account-name"]', timeout=3000)).inner_text()
                        if id != None:
                            break
                    except Exception as e:
                        continue
            p = await page.reload()
            cookie = (await p.request.all_headers())['cookie']
            agent = (await p.request.all_headers())['user-agent'] 
            return True, id, cookie, agent
        except Exception as e:
            logging.error(e.__class__, exc_info=True)
            return False, None, None, None

async def changePrice(os: str, dir: str, id: str, payloads: List[SearchPayload], pause=200):
    async with async_playwright() as pw:
        try:
            user_data_dir = dir
            if os.__contains__('mac'):
                browser = await pw.chromium.launch_persistent_context(user_data_dir, channel='chrome')
            elif os.__contains__('windows'):
                browser = await pw.chromium.launch_persistent_context(user_data_dir)
            else:
                raise Exception('bad os')
            page = browser.pages[0]
            page.set_default_timeout(DEFAULT_TIMEOUT * 6)
            await page.goto(s.ads(id))
            item = await page.wait_for_selector('//div[@class="ellipsis-content single"]')
            popup = page.locator('//div[@class="src-components-modals-upgrade-shopads---footer--1VgFZ"]/button')
            if await popup.is_visible():
                await popup.click()
            await page.wait_for_timeout(pause)
            await item.click()
            await page.wait_for_selector('//div[@class="campaign-info"]')
            rows = []
            prices = []
            for payload in payloads:
                pagination = page.locator('//span[@class="shopee-pagination-sizes__content"]')
                await pagination.scroll_into_view_if_needed()
                await page.wait_for_timeout(pause)
                await pagination.click()
                fifty = page.locator('//li[@class="shopee-dropdown-item"]', has=page.locator('span', has_text='50'))
                await fifty.click()
                await page.wait_for_timeout(pause)
                row = page.locator('tr', has=page.locator(f'//div[@class="item-delete {payload.name}"]'))
                await row.scroll_into_view_if_needed()
                await page.wait_for_timeout(pause)
                await row.locator('//span[@class="text"]', has_text='NT$').click()
                await page.wait_for_timeout(pause)
                box = page.locator('.bid-price-edit-popper:visible')
                input = box.get_by_placeholder('0.00')
                await input.scroll_into_view_if_needed()
                await page.wait_for_timeout(pause)
                await input.fill(payload.price)
                confirm = box.locator('//span', has_text='確認')
                await confirm.scroll_into_view_if_needed()
                await page.wait_for_timeout(pause)
                await confirm.click()
                await page.wait_for_timeout(pause * 3)
                price = float((await row.locator('//span[@class="text"]', has_text='NT$').inner_text()).replace('NT$', ''))
                if price == float(payload.price):
                    rows.append(payload.row)
                    prices.append(payload.price)
            return rows, prices
        except Exception as e:
            logging.error(e.__class__, exc_info=True)
            return [], []

# async def gotoPage(os, url):
#     async with async_playwright() as pw:
#         try:
#             user_data_dir = f'{App.getDir()}/profiles/{profile}'
#             if os.__contains__('mac'):
#                 browser = await pw.chromium.launch_persistent_context(user_data_dir, headless=False, channel='chrome')
#             elif os.__contains__('windows'):
#                 browser = await pw.chromium.launch_persistent_context(user_data_dir, headless=False)
#             else:
#                 raise Exception('bad os')
#             page = browser.pages[0]
#             await page.goto(url)
#             await page.wait_for_timeout(DEFAULT_TIMEOUT * 30)
#         except Exception as e:
#             logging.error(e.__class__, exc_info=True)

# async def addProfile(os, profile):
#     async with async_playwright() as pw:
#         try:
#             user_data_dir = f'profiles/{profile}'
#             if os.__contains__('mac'):
#                 browser = await pw.chromium.launch_persistent_context(user_data_dir, channel='chrome', headless=False)
#             elif os.__contains__('windows'):
#                 browser = await pw.chromium.launch_persistent_context(user_data_dir)
#             else:
#                 raise Exception('bad os') 
#             page = browser.pages[0]
#             page.set_default_timeout(DEFAULT_TIMEOUT * 3)
#             p = await page.goto(s.seller)
#             # p.request.all_headers
#             for _ in range(10):
#                 id = None
#                 try:
#                     id = await (await page.wait_for_selector('//span[@class="subaccount-name"]', timeout=3000)).inner_text()
#                     if id != None:
#                         break
#                 except Exception as e:
#                     try:
#                         id = await (await page.wait_for_selector('//span[@class="account-name"]', timeout=3000)).inner_text()
#                         if id != None:
#                             break
#                     except Exception as e:
#                         continue
#                 # await page.wait_for_timeout(69)
#             print(await p.request.all_headers())
#             cookie = (await p.request.all_headers())['cookie']
#             agent = (await p.request.all_headers())['user-agent'] 
#             return True, id, cookie, agent
#         except Exception as e:
#             logging.error(e.__class__, exc_info=True)
#             return False, None, None, None

# async def processMultiple(resp, payloads, results):
#     if resp.url.__contains__(s.search):
#         try:
#             _, _, third = resp.url.partition('keyword=')
#             name, _, _ = third.partition('&')
#             id, row = payloads[name]
#             ads = 0
#             hypes = 0
#             ad = '無'
#             hype = '無'
#             items = (await resp.json())['items']
#             for item in items:
#                 if item['adsid'] != None:
#                     ads += 1
#                     if item['itemid'] == id:
#                         ad = ads
#                 else:
#                     hypes += 1
#                     if item['itemid'] == id:
#                         hype = hypes
#             results.append(SearchResult(ad, hype, row))
#         except Exception as e:
#             logging.error(e.__class__, exc_info=True)
#             print('access denied', resp.status)
#             results.append(SearchResult('', '', row))
    
async def processResponse(resp: Response, payload: SearchPayload, results: List[SearchResult]):
    if resp.url.__contains__(s.search):
        try:
            ads = 0
            hypes = 0
            ad = '無'
            hype = '無'
            items = (await resp.json())['items']
            for item in items:
                if item['adsid'] != None:
                    ads += 1
                    if str(item['itemid']) == str(payload.id):
                        ad = ads
                else:
                    hypes += 1
                    if str(item['itemid']) == str(payload.id):
                        hype = hypes
            results.append(SearchResult(ad, hype, payload.row))
        except Exception as e:
            logging.error(e.__class__, exc_info=True)
            results.append(SearchResult('', '', payload.row))

async def search(os: str, payload: SearchPayload):
    async with async_playwright() as pw:
        try:
            if os.__contains__('mac'):
                browser = await pw.chromium.launch(channel='chrome')
            elif os.__contains__('windows'):
                browser = await pw.chromium.launch()
            else:
                raise Exception('bad os')
            results = []
            page = await browser.new_page()
            page.set_default_timeout(100000)
            page.on('response', lambda resp: asyncio.ensure_future(processResponse(resp, payload, results))) 
            await page.goto(s.searchWeb(payload.name))
            for _ in range(420):
                if len(results) == 1:
                    break
                await page.wait_for_timeout(69)
            return results.pop()
        except Exception as e:
            logging.error(e.__class__, exc_info=True)
            return None

# async def searchMultiple(os, payloads):
#     async with async_playwright() as pw:
#         try:
#             _payloads = dict()
#             results = []
#             if os.__contains__('mac'):
#                 browser = await pw.chromium.launch(channel='chrome')
#             elif os.__contains__('windows'):
#                 browser = await pw.chromium.launch()
#             else:
#                 raise Exception('bad os')
#             page = await browser.new_page()
#             page.set_default_timeout(100000)
#             page.on('response', lambda resp: asyncio.ensure_future(processMultiple(resp, _payloads, results)))
#             for index, payload in enumerate(payloads):
#                 _payloads[quote(payload.name)] = (payload.id, payload.row)
#                 await page.goto(s.searchWeb(payload.name))
#                 for _ in range(100):
#                     if len(results) == index+1:
#                         break
#                     await page.wait_for_timeout(69)
#             return results
#         except Exception as e:
#             logging.error(e.__class__, exc_info=True) 
#             return []

# API calls
async def getAdvertisements(cookie: str, agent: str):
    limit = 50
    advertisements = []
    try:
        res = await goto(url=s.products(), headers={ 'cookie': cookie, 'user-agent': agent })
        count = res.json()['data']['total_count']
        list = res.json()['data']['campaign_ads_list']
        for l in list:
            # status == 1 is ongoing campaing, match_type == 1 是廣泛
            if l['campaign']['status'] == 1:
                for a in l['advertisements']:
                    itemId = l['product']['itemid']
                    # ad = Advertisement(itemId, [])
                    for k in a['extinfo']['keywords']:
                        if str(k['status']) == '1':
                            if float(k['price']) <= 1.2 and str(k['match_type']) == '1':
                                continue
                            # ad.keywords.append(Keyword(name=k['keyword'], price=k['price']))
                            ad = (str(itemId), str(k['keyword']), str(k['price']))
                            advertisements.append(ad)
        for offset in range(limit, count, limit):
            res = await goto(url=s.products(offset=offset), headers={ 'cookie': cookie, 'user-agent': agent })
            list = res.json()['data']['campaign_ads_list']
            for l in list:
                if l['campaign']['type'] == 'keyword' and l['campaign']['status'] == 1 and l['campaign']['state'] != 'ended':
                    for a in l['advertisements']:
                        itemId = l['product']['itemid']
                        # ad = Advertisement(itemId, [])
                        for k in a['extinfo']['keywords']:
                            if str(k['status']) == '1':
                                if float(k['price']) <= 1.2 and str(k['match_type']) == '1':
                                    continue
                                # ad.keywords.append(Keyword(name=k['keyword'], price=k['price']))
                                ad = (str(itemId), str(k['keyword']), str(k['price']))
                                advertisements.append(ad)
        # return True, advertisements
    except Exception as e:
        logging.error(e.__class__, exc_info=True)
        # return False, None
    finally:
        return advertisements

async def getDetails(cookie: str, agent: str, itemId: str, span=7):
    details = {}
    try:
        res = await goto(url=s.details(itemId, span-1), headers={ 'cookie': cookie, 'user-agent': agent })
        items = res.json()['data']
        for item in items:
            name = item.get('keyword', '')
            if name != '':
                roas = item.get('direct_roi', '')
                cost = item.get('cost', '')
                sales = item.get('direct_gmv', '')
                details[name] = []
                if roas != '':
                    roas = round(float(roas), 2)
                details[name].append(roas)
                details[name].append(cost)
                details[name].append(sales)
        return details
    except Exception as e:
        logging.error(e.__class__, exc_info=True)

# async def search(keyword, id, proxy):
#     headers = {'x-api-source': 'rn', 'x-phone-model': iphone(), 'x-phone-brand': 'Apple', 
#             'user-agent': 'iOS app iPhone Shopee appver=29530 language=zh-Hant app_type=1'}
#     ads = 0
#     hypes = 0
#     ad = '無'
#     hype = '無'
#     try:
#         res = await goto(url=s.searchApp(keyword), headers=headers, proxy=proxy, http2=True)
#         items = res.json()['data']['items_response']['items']
#         for item in items:
#             if item['adsid'] != None:
#                 ads += 1
#                 if item['itemid'] == id:
#                     ad = ads
#             else:
#                 hypes += 1
#                 if item['itemid'] == id:
#                     hype = hypes
#         return True, ad, hype
#     except Exception as e:
#         logging.error(e.__class__, exc_info=True)
#         return False, None, None
# shopee-select__menu shopee-select__menu_no_top_radius