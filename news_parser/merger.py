#!/usr/bin/python3

from os import listdir
from os.path import isfile, join
import json
import pathlib


def merge_json_files(path, filenames):
	result = list()
	for fn in filenames:
		with open(f'{path}/{fn}', 'r') as infile:
			result.extend(json.load(infile))

	with open(f'{path}/merged.json', 'w') as output_file:
		json.dump(result, output_file)

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
