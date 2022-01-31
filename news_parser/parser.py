#!/usr/bin/python3

import bs4
import json
import requests
import http
import re
import pandas as pd
from datetime import datetime
import argparse
import pathlib
from enum import Enum


MSG_LBL_BASE = '[PARSER]'
MSG_LBL_INFO = f'{MSG_LBL_BASE}[INFO]'
MSG_LBL_FAIL = f'{MSG_LBL_BASE}[FAIL]'


def parse_args():
    parser = argparse.ArgumentParser(description='Parse news atricles from bbc.co.uk')
    parser.add_argument('--date', type=str, required=True, help='date string (YYYY-MM-DD)')
    args = parser.parse_args()
    return args


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
		print(f'{MSG_LBL_FAIL} {url}: {http.client.responses[status]}')
		return None


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
		print(f'{MSG_LBL_FAIL} {e}')
		return None

	return content


def collect_urls(date):
	date = pd.to_datetime(date)
	collected = set()

	archive_url_base = 'https://dracos.co.uk/made/bbc-news-archive'
	article_url_regex_raw = '(?:^|\W)http:\/\/www\.bbc\.co\.uk\/news(?:^|\W)([a-z|-]+)+([0-9])+'
	article_url_regex = re.compile(article_url_regex_raw)

	year, month, day = str(date.date()).split('-')
	print(f'{MSG_LBL_INFO} Collecting articles for {year}/{month}/{day} ...')

	archive_url = f'{archive_url_base}/{year}/{month}/{day}/'
	page = get_page(archive_url)
	if page is not None:
		soup = bs4.BeautifulSoup(page, 'html.parser')
		urls_tags = soup.find_all('a')

		for tag in urls_tags:
			url = tag['href']
			if article_url_regex.match(url):
				collected.add(url)

	print(f'{MSG_LBL_INFO} Collected {len(collected)} articles links for {year}/{month}/{day},')

	return collected


def parse_urls(urls):
	parsed = []
	total = len(urls)

	for i, url in enumerate(urls):
		print(f'{MSG_LBL_INFO} Parsing {url}, {i + 1}/{total}')

		article_page = get_page(url)
		article_content = parse_article(article_page, url)
		if article_content is not None:
			parsed.append(article_content)

	return parsed


def main():
	args = parse_args()
	print(f'{MSG_LBL_BASE} date - {args.date}')	

	urls = collect_urls(args.date)
	parsed = parse_urls(urls)

	my_path = pathlib.Path(__file__).parent.resolve()
	output_filename = f'{my_path}/artifacts/{args.date}.json'
	catalog = {'catalog': parsed}
	with open(output_filename, 'w') as fout:
		json.dump(catalog, fout, indent=2)


if __name__ == "__main__":
	main()
