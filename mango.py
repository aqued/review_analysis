"""
망고플레이트의 음심적 목록을 불러오는 파일입니다.
"""

import asyncio
import requests
import json
import aiohttp


search_key_url = "https://stage.mangoplate.com/api/common/codetable.js?device_type=web&device_uuid=jHgTW15581988947720556msiwg&language=kor"

topic_list_url = "https://stage.mangoplate.com/api/v5/top_lists/list.json?language=kor&device_type=web&start_index={offset}&request_count=50"

restuarant_lisr_url = "https://stage.mangoplate.com/api/v2/web/top_lists/{topic}/restaurants.js?language=kor&device_type=web&start_index={offset}&request_count=50"



search_key = []

resp = requests.get(search_key_url)
data = json.loads(resp.text)

for item in data:
    search_key.append(item['display_text'])

print(len(search_key))


restaurants_key = []

async def search(key):
    offset = 0
    while True:
        asyncio.sleep(0.01)
        data = {"language": "kor", "device_type": "web", "start_index": offset,
                "keyword": key, "request_count": 40, "order_by": 2}
        print(key, offset)
        async with aiohttp.ClientSession() as session:
            async with session.post("https://stage.mangoplate.com/api/v5/search/by_keyword.json", json=data) as resp:
                if not resp.status != '200':
                    print('error ')
                else:
                    try:
                        data = (await resp.json())['result']
                    except:
                        print(await resp.text())
                        break

                    if len(data) == 0:
                        break

                    for restaurant in data:
                        restaurant = restaurant['restaurant']
                        r = dict(name=restaurant.get('name', ''),
                                 address=restaurant.get('address', ''),
                                 restaurant_key=restaurant.get('restaurant_key', ''),
                                 latitude=restaurant.get('latitude', ''),
                                 longitude=restaurant.get('longitude', '')
                                )
                        restaurants_key.append(r)

        offset += 40




async def f():
    coros = [search(key) for key in search_key]
    await asyncio.gather(*coros)


loop = asyncio.get_event_loop()
loop.run_until_complete(f())

print(restaurants_key)
print(restaurants_key[:3])

import pandas as pd

df = pd.DataFrame(restaurants_key)
df.to_csv('mango.csv')

