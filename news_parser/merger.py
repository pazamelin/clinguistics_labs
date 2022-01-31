#!/usr/bin/python3

from os import listdir
from os.path import isfile, join
import json
import pathlib


def merge_json_files(path, filenames):
	all_articles_list = []

	for fn in filenames:
		full_fn = f'{path}/{fn}'
		print(full_fn)
		with open(full_fn) as json_file:
			data = json.load(json_file)
			all_articles_list += data['catalog']

	all_articles_dict = {'catalog': all_articles_list}
	with open(f'{path}/merged.json', 'w') as output_file:
		json.dump(all_articles_dict, output_file, indent=2)


def main():
	# collect files
	my_path = pathlib.Path(__file__).parent.resolve()
	artifacts_path = f'{my_path}/artifacts/'
	files = [f for f in listdir(artifacts_path) if isfile(join(artifacts_path, f))]
	files = sorted(files)
	
	# merge
	merge_json_files(artifacts_path, files)


if __name__ == "__main__":
	main()
