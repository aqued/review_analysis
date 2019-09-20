import pandas as pd
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup as Bs
from functools import partial

BASE_URL = "https://www.tripadvisor.co.kr"

restaurants = pd.DataFrame.from_csv('trip.csv')

redirects_off = partial(requests.get, allow_redirects=False)



r = []

async def get_review_id(loop, name, url):
    offset = 0
    u = BASE_URL + url
    while True:
        print(name, offset)
        s = u
        if offset != 0:
            s = u.replace('Reviews-', f'Reviews-or{offset}-')
        
        resp = await loop.run_in_executor(None, redirects_off, s)

        if resp.status_code > 399:
            print(resp.text)
            
        elif resp.status_code > 299:
            break
            
        else:
            soup = Bs(resp.text, 'html.parser')
            div_list = soup.select('div.reviewSelector')
            for div in div_list:
                r.append({'name': name, 'review': div.get('data-reviewid')})

        offset += 10

async def main(loop):
    tasks = [get_review_id(loop, row['name'], row['url']) for index, row in restaurants.iterrows()]
    await asyncio.gather(*tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(get_review_id(loop, '숙영식당', '/Restaurant_Review-g297888-d6494504-Reviews-Sukyoung_Sikdang-Gyeongju_Gyeongsangbuk_do.html'))
print(len(r))
# pd.DataFrame(r).to_csv('t.csv')

