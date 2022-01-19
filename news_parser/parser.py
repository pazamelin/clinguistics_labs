#!/usr/bin/python3

import bs4
import json
import requests
import http
import re
import pandas as pd
from datetime import datetime


def get_page(url, filename=None):
	response = requests.get(url, allow_redirects=True)
	status = response.status_code
	if status == 200:
		content = response.content
		if filename is not None:
			soup = bs4.BeautifulSoup(content, 'html.parser')
			with open(filename, 'w') as file:
				file.write(str(soup.prettify()))
		return content
	else:
		raise Exception(f'{url}: {http.client.responses[status]}')


def parse_article(page, url):
	content = {}
	try:
		soup = bs4.BeautifulSoup(page, 'html.parser')

		attributes = ['article_id', 'title', 'category', 'tags', 'text']

		content['article_id'] = url
		content['category'] = url[url.rfind('/')+1:url.rfind('-')]
		content['title'] = soup.find(id='main-heading').text.strip()

		tags = soup.find('section', attrs={'data-component' : 'tag-list'})
		if tags is not None:
			tags = tags.find_all('a', attrs={'class' : 'ssrcss-1yno9a1-StyledLink ed0g1kj0'})
			if tags is not None:
				content['tags'] = ','.join([item.text for item in tags])
			else:
				content['tags'] = None

		text_blocks = soup.find_all('div', attrs={'data-component' : 'text-block'})
		if text_blocks is not None:
			text_blocks = [tb.text for tb in text_blocks]
			content['text'] = '\n'.join(text_blocks)
	except Exception as e:
		print(f'[ERROR] {e}')
		return None

	return content


def collect_articles(output_file='articles.json'):
	collected = []

	collected_links = {}

	archive_url_base = 'https://dracos.co.uk/made/bbc-news-archive'
	article_url_regex_raw = '(?:^|\W)http:\/\/www\.bbc\.co\.uk\/news(?:^|\W)([a-z|-]+)+([0-9])+'
	article_url_regex = re.compile(article_url_regex_raw)

	date_range = pd.date_range(start="2021-03-01", end="2021-05-01")
	for date in date_range:
		counter_date = 0
		year, month, day = str(date.date()).split('-')
		print(f'[LOG] Collecting articles for {year}/{month}/{day} ...')

		archive_url = f'{archive_url_base}/{year}/{month}/{day}/'
		page = get_page(archive_url)
		soup = bs4.BeautifulSoup(page, 'html.parser')
		urls_tags = soup.find_all('a')
		for tag in urls_tags:
			url = tag['href']
			if article_url_regex.match(url):
				collected_links[url] = 1

		print(f'[LOG] Collected {len(collected_links.keys())} articles for {year}/{month}/{day},')


	total = len(collected_links.keys())
	for i, url in enumerate(collected_links.keys()):
		print(f'[LOG] Parsing article at {url}, {i}/{total}')

		article_page = get_page(url)
		article_content = parse_article(article_page, url)
		if article_content is not None:
			collected.append(article_content)

	catalog = {'catalog': collected}
	with open(output_file, 'w') as fout:
		json.dump(catalog, fout, indent=2)


def main():
	collect_articles()


if __name__ == "__main__":
	main()