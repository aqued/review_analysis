"""
망고플레이트의 리뷰를 csv파일로 저장하는 파일입니다.
"""


import asyncio
import aiohttp
import pandas as pd


mango_restaurants = pd.DataFrame.from_csv('mango.csv')
# print(mango_restaurants.head)


mango_reviews = pd.DataFrame(columns=['restaurant_key', 'review'])


keys =list(mango_restaurants['restaurant_key'])

print(len(keys))
mango_review_url = "https://stage.mangoplate.com/api/v5/restaurants/{restaurant_key}/reviews.json?language=kor&device_type=web&start_index={offset}&request_count=50&sort_by=2"

async def fetch_reviews(key):
    """
    key 에 해당하는 식당 리뷰를 가져옵니다.
    """
    offset = 0
    while True:
        print(key, offset)
        first = True
        async with aiohttp.ClientSession() as session:
            url = mango_review_url.format(restaurant_key=key, offset=offset)
            async with session.get(url) as resp:
                if int(resp.status ) >= 400:
                    print(await resp.text())

                else:
                    data = await resp.json()
                    if first and len(data) < 50:
                            break
                    if len(data) == 0:
                        break
                    first = False
                    for item in data:
                        d =  dict(
                                restaurant_key =key,
                                review=item['comment']['comment']
                            )

                        mango_reviews.loc[len(mango_reviews)] =d
        offset += 50


async def main():
    l = len(keys)
    for i in range(100):
        start = i *  (l // 99)
        end = (i + 1) * (l // 99)
        tasks = [fetch_reviews(key) for key in keys[start:end]]
        await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


mango_reviews.to_csv('mango_reviews.csv')
