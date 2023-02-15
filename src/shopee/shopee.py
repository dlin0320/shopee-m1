from dataclasses import dataclass
import time
from urllib.parse import quote
from datetime import datetime

class Shopee:
    home = 'https://shopee.tw/'

    seller = 'https://seller.shopee.tw/'

    mobile = 'https://mall.shopee.tw/'

    portal = 'https://seller.shopee.tw/portal/shop'

    search = 'https://shopee.tw/api/v4/search/search_items?by=relevancy'

    def product(id=''):
        return f'{Shopee.seller}portal/product/{id}'

    def ads(id=''):
        if id == '':
            return f'{Shopee.seller}portal/marketing/pas/assembly?type=search'
        return f'{Shopee.seller}portal/marketing/pas/assembly?type=search&search={id}'

    def searchWeb(keyword: str):
        keyword = quote(keyword)
        return f'{Shopee.home}search?keyword={keyword}'

    def searchApp(keyword: str):
        keyword = quote(keyword)
        return f'{Shopee.mobile}api/v4/search/search_page_common?by=relevancy&keyword={keyword}&newest=0&order=desc&page=2&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2&with_filter_config=true'

    # TODO add spc_cds to path url
    def products(offset=0, limit=50, spc_cds='', spc_cds_ver='2'):
        start_time = int(time.time()) - 600000
        end_time = int(time.time())
        return f'{Shopee.seller}api/marketing/v3/pas/homepage/?campaign_type=keyword&campaign_state=ongoing&sort_key=performance&sort_direction=1&search_content=&start_time={start_time}&end_time={end_time}&offset={offset}&limit={limit}'

    def details(itemid: str, span: int):
        today = datetime.now()
        now = int(time.time())
        start_time = now - (today.hour * 60 * 60) - (today.minute * 60) - (today.second) - (60 * 60 * 24 * span)
        end_time = now
        return f'{Shopee.seller}api/marketing/v3/pas/report/detail_report_by_keyword/?itemid={itemid}&start_time={start_time}&end_time={end_time}&placement_list=%5B0%5D'

@dataclass
class Profile:
    id: str
    cookie: str
    agent: str

@dataclass
class ChangePayload:
    name: str
    price: str
    row: str

# @dataclass
# class ChangeResult:
#     new_price: str
#     row: str

@dataclass
class SearchPayload:
    name: str
    id: str
    row: str

@dataclass
class SearchResult:
    ad: str
    hype: str
    row: str

@dataclass
class Keyword:
    name: str
    price: str

@dataclass
class Advertisement:
    id: str
    keywords: list[Keyword]