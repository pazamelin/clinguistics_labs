#!/usr/bin/python3

import argparse
from datetime import datetime
import subprocess
import os
import pandas as pd
import pathlib


def parse_args():
    parser = argparse.ArgumentParser(description='Parse news atricles from bbc.co.uk')
    parser.add_argument('--start', type=str, required=True, help='date string (YYYY-MM-DD)')
    parser.add_argument('--end',  type=str, required=True, help='date string (YYYY-MM-DD)')
    args = parser.parse_args()
    return args


def main():
	args = parse_args()
	print(f'[DRIVER] start - {args.start}, end - {args.end}')

	my_path = pathlib.Path(__file__).parent.resolve()
	date_range = pd.date_range(start=args.start, end=args.end)
	for date in date_range:
		subprocess.run(['python3', f'{my_path}/parser.py', '--date', str(date.date())])


if __name__ == "__main__":
	main()
