"""
수집된 리뷰 id를 이용하여 전체리뷰를 수집하는 코드입니다.
"""

import asyncio
import pandas as pd
import aiohttp
import requests
from bs4 import BeautifulSoup as Bs
from functools import partial


reviews = pd.DataFrame.from_csv('trip2.csv')

url = "https://www.tripadvisor.co.kr/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=&contextChoice=DETAIL&reviews={reviews}"


get = partial(requests.get, headers={'Referer': "https://www.tripadvisor.co.kr/"})


result = []

async def get_review(loop, name, reviews):
    print(name)
    reviews = [int(review) for review in reviews]
    resp = loop.run_in_executor(None, get, url.format(reviews=reviews))
    if not resp.ok:
        print('error', name)
    soup = Bs(resp.text, 'html.parser')
    l = soup.select('p.partial_entry')
    for i in l:
        result.append({'name': name, 'review': i.text})
    

async def main(loop):
    tasks = [get_review(loop,row['name'], eval(row['id'])) for index, row in reviews.iterrows()]
    await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop = loop.run_until_complete(main(loop))


n = pd.DataFrame(result)
n.to_csv('trip_review')
