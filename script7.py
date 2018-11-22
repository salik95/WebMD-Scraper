import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import csv

conditions_url = []

conditions_starting_id = 1
treatments_starting_id = 1
reviews_starting_id = 1

conditions_data = []
treatments_data = []
reviews_data = []

conditions_column_names = ['id', 'name', 'webmd_url']
treatments_column_names = ['id', 'condition_id', 'name', 'effectiveness', 'average_effectiveness', 'average_easeofuse', 'average_satisfaction', 'total_reviews']
reviews_column_names = ['id', 'treatment_id', 'date', 'reason_for_taking', 'reviewer_info', 'effectiveness', 'easeofuse', 'satsfaction', 'comment', 'people_find_helpful']

with open('WebMD 31-35.tsv') as conditions:
	for cnd in conditions:
		conditions_url.append(cnd.strip('\n').split('\t'))

del conditions_url[0]

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options)

condition_id = conditions_starting_id
treatment_id = treatments_starting_id
review_id = reviews_starting_id

for url in conditions_url:

	condition_req = requests.get(url[1])
	condition_soup = BeautifulSoup(condition_req.text)

	print('========================')

	treatments = condition_soup.find('table', {'class':'vitamins-treatments-table'})
	for tmt in treatments.find('tbody').find_all('tr'):
		row = tmt.find_all('td')
		treatment_name = row[0].find('a').text.strip()
		print('Treatment Name: ' + treatment_name)
		effectiveness = row[1].find(text=True, recursive=False).strip()
		reviews_page_link = row[2].find('a')['href']
		print('========================')

		driver.get(row[2].find('a')['href']+'&pageIndex=0&sortby=3&conditionFilter=-1')
		driver.implicitly_wait(23)

		reviews_req = driver.page_source
		reviews_soup = BeautifulSoup(reviews_req)

		try:
			total_reviews = int(reviews_soup.find('span', {'class':'totalreviews'}).text.strip().split(' ')[0])
		except:
			# ========================================
			# Data Filling for treatments if reviews are zero
			treatments_data.append([treatment_id, condition_id, treatment_name, effectiveness, 0.0, 0.0, 0.0, 0])
			# -----------------------------
			# Treatment ID increment
			treatment_id = treatment_id + 1
			# ========================================
			print('Total Reviews: ' + '0')
			continue

		average_effectiveness = float(reviews_soup.find('p', {'id':'EffectivenessSummaryValue','class':'numbRating'}).text.strip('()'))
		average_easeofuse = float(reviews_soup.find('p', {'id':'EaseOfUseSummaryValue','class':'numbRating'}).text.strip('()'))
		average_satisfaction = float(reviews_soup.find('p', {'id':'SideEffectsSummaryValue','class':'numbRating'}).text.strip('()'))

		current_review_page = 0

		review_count = 0
		while review_count < total_reviews:
			print('Review Page Number: ' + str(current_review_page))
			for user_reviews in reviews_soup.find_all('div', {'id':'ratings_fmt'}):
				for rev in user_reviews.find_all('div', {'class':'userPost'}):
					reason_for_taking = rev.find('div',{'class':'conditionInfo'}).find('span',{'class':'reason'})['title'].strip()
					rev_date = rev.find('div',{'class':'date'}).text.strip()
					rev_info = rev.find('p',{'p','reviewerInfo'}).text.replace('Reviewer: ', '').strip()
					star_ratings = rev.find_all('span',{'class':'current-rating'})
					rev_effectiveness = int(star_ratings[0].text.lower().replace('current rating:', '').strip())
					rev_easeofuse = int(star_ratings[1].text.lower().replace('current rating:', '').strip())
					rev_satisfaction = int(star_ratings[2].text.lower().replace('current rating:', '').strip())
					rev_comment = rev.select('p[id*="comFull"]')[0].find(text=True, recursive=False)
					rev_helpful = int(rev.find('p',{'class':'helpful'}).find(text=True, recursive=False).split('\n')[0].strip())
					if len(rev_date) > 1 and len(reason_for_taking) > 1:
						# ========================================
						# Data Filling for reviews
						reviews_data.append([review_id, treatment_id, rev_date, reason_for_taking, rev_info, rev_effectiveness, rev_easeofuse, rev_satisfaction, rev_comment, rev_helpful])
						review_count = review_count + 1
						# -----------------------------
						# Review ID increment				
						review_id = review_id + 1
						# ========================================
			if current_review_page > (1 + (total_reviews/5)):
				break

			current_review_page = current_review_page + 1
			driver.get(row[2].find('a')['href']+'&pageIndex=' + str(current_review_page) + '&sortby=3&conditionFilter=-1')
			driver.implicitly_wait(23)
			reviews_req = driver.page_source
			reviews_soup = BeautifulSoup(reviews_req)
		# ========================================
		# Data Filling for treatments
		treatments_data.append([treatment_id, condition_id, treatment_name, effectiveness, average_effectiveness, average_easeofuse, average_satisfaction, total_reviews])
		# -----------------------------
		# Treatment ID increment
		treatment_id = treatment_id + 1
		# ========================================
		print('Total Reviews: ' + str(total_reviews))
		print('Reviews Array Length: ' + str(review_count))
		print('+++++++++++++++++++++++++++++++++++++')
	# ========================================
	# Data Filling for conditions
	conditions_data.append([condition_id, url[0], url[1]])
	# -----------------------------
	# Condition ID increment
	condition_id = condition_id + 1
	print('********************************')
	print(url[1])
	# ========================================

driver.close()

condition_outfile = open('condition 7.csv', 'w')
condition_outcsv = csv.writer(condition_outfile)
condition_outcsv.writerow([column for column in conditions_column_names])
[condition_outcsv.writerow([value for value in item]) for item in conditions_data]
condition_outfile.close()
print('===================================')
print('Conditions Data Length: ' + str(len(conditions_data)))

treatment_outfile = open('treatment 7.csv', 'w')
treatment_outcsv = csv.writer(treatment_outfile)
treatment_outcsv.writerow([column for column in treatments_column_names])
[treatment_outcsv.writerow([value for value in item]) for item in treatments_data]
treatment_outfile.close()
print('===================================')
print('Treatments Data Length: ' + str(len(treatments_data)))

review_outfile = open('review 7.csv', 'w')
review_outcsv = csv.writer(review_outfile)
review_outcsv.writerow([column for column in reviews_column_names])
[review_outcsv.writerow([value for value in item]) for item in reviews_data]
review_outfile.close()
print('===================================')
print('Reviews Data Length: ' + str(len(reviews_data)))