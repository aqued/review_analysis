import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup as Bs
import re

THRESHOLD = 40


location_list_url = "https://www.tripadvisor.co.kr/Restaurants-g294196-oa{offset}-South_Korea.html#LOCATION_LIST"
tripadvisor_url = "https://www.tripadvisor.co.kr/RestaurantSearch?Action=PAGE&geo={geo_code}&ajax=1&itags=10591&sortOrder=relevance&o=a{offset}&availSearchEnabled=false"

geo_codes = ['294197', '297884', '297886', '297889', '297887', '297893',
             '304129', '612376', '424960', '983296', '946499', '2024873', '2024865', '1119868',
             '1143545', '1643550', '676092', '297885', '946497', '661419']

offset = 20
while True:
    resp = requests.get(location_list_url.format(offset=offset), allow_redirects=False)
    if resp.status_code > 299:
        break
    
    else:
        soup = Bs(resp.text, 'html.parser')
        a_list = soup.select('.geoList > li > a')
        
        for a in a_list:
            url = a.get('href')
            
            # parse geo code 
            code = re.search('g(\d+)', url).group()[1:]
            geo_codes.append(code)
    offset += 20


restaurants = []
async def get_local_restaurants(code):
    # 리뷰가 50개 이하인 식당이 일정 개수 이상 나오거나 더이상 없는 경우 종료
    count = 0
    offset = 0
    while True:
        print(code, offset)
        if count >= THRESHOLD:
            break

        url = tripadvisor_url.format(geo_code=code, offset=offset)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:

                if int(resp.status) > 400:
                    print(f"{code} {offset} error")
                elif int(resp.status) > 299:
                    break
                else:
                    soup = Bs(await resp.text(), 'html.parser')
                    list_contents = soup.select('#EATERY_LIST_CONTENTS')[0]
                    listing = list_contents.select('div.listing')
                    for l in listing:
                        a_title = l.select('a.property_title')[0]
                        name = a_title.text.strip()
                        url = a_title.get('href')
                        try:
                            review_count = int(re.sub(r'[^0-9]', '', l.select('span.reviewCount > a')[0].text))
                        except:
                            review_count = -1
                        if review_count >= 50:
                            restaurants.append({'name': name, 'url': url})
                        else:
                            count += 1
        offset += 30

async def main():
    c = [get_local_restaurants(code) for code in geo_codes]
    await asyncio.gather(*c)

print(len(restaurants))
print(restaurants[:3])
loop = asyncio.get_event_loop()
loop.run_until_complete(main())


import pandas as pd

df = pd.DataFrame(restaurants)
df.to_csv('trip.csv')

