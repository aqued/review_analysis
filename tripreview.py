import requests
import pandas as pd
from bs4 import BeautifulSoup as Bs


trip_review = pd.DataFrame.from_csv('trip.csv')
reviews = []

trip_url = "https://www.tripadvisor.co.kr/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer&contextChoice=DETAIL&reviews={reviews}"

headers = {'Referer': "https://www.tripadvisor.co.kr/"}
for idx, row in trip_review.iterrows():
	id_list = list(map(lambda x: str(x), eval(row['review_x'])))
	url = trip_url.format(reviews=(','.join(id_list)))
	resp = requests.post(url, headers=headers)
	if not resp.ok:
		print(resp.text)
	
	soup = Bs(resp.text, 'html.parser')
	p_list = soup.select('.partial_entry')
	print(len(p_list))
	for p in p_list:
		reviews.append({'name': row['name'], 'review': p.text})


print(len(reviews))

df = pd.DataFrame(reviews)
df.to_csv('last_trip_review.csv')
