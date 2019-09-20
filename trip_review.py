"""
트립어드바이저는 리뷰페이지에서 전체리뷰가 보이지 않고 더보기를 눌러야
전체 리뷰가 나타나기 때문에 먼저 리뷰 id 만 수집하여 csv로 저장하는 파일입니다.
"""

import pandas as pd
import requests
import asyncio
import functools
from bs4 import BeautifulSoup as Bs
import re


no_redirect_requests = functools.partial(requests.get, allow_redirects=False)

trip = pd.DataFrame.from_csv('trip.csv')




base_url = "https://www.tripadvisor.co.kr"

review = []

def insert_offset(url, offset):
    if offset == 0:
        return url
    return re.sub('-Reviews', 'o%d' % offset, url)


async def get_review_id(index, url, name):
    loop = asyncio.get_event_loop()
    offset = 0
    id_list = []
    while True:
        offset_url = insert_offset(url, offset)
        resp = await loop.run_in_executor(None, no_redirect_requests,
                base_url + offset_url)
        
        if resp.status_code > 399:
            print(resp.text)

        elif resp.status_code > 299:
            break

        else:
            soup = Bs(resp.text, 'html.parser')
            div_list = soup.select('div.review-container')

            for div in div_list:
                id_list.append(div.get('data-reviewid'))
        offset += 20
    
    review.append({'name': name, 'id': id_list})


async def main():
    tasks = [get_review_id(index, row['url'], row['name'])
            for index, row in trip.iterrows()]
    await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()

loop.run_until_complete(main())

trip2 = pd.DataFrame(review)
trip2.to_csv('trip2.csv')

