import datetime
import re

def reverse_date(date):
	return datetime.datetime.strptime(date,'%d-%m-%Y').strftime('%Y-%m-%d')

def convert_mm_inch(mm):
	return float(mm)/25.4

def extract_range(val):
	match = re.search('([0-9]+)-([0-9]+)', val)
	return match.group(1),match.group(2)


def check_val_in_range(range_, value):
	from_, to_ = extract_range(range_)
	if float(value) > float(from_) and float(value) <= float(to_):
		return True
	else:
		return False

def is_order_shelf_compatible(shelf, exclusions):
	if exclusions != 'None':
		if shelf not in [int(x) for x in exclusions.split(',')]:
			return True
		else:
			return False
	else:
		return True

def pile_size(bond, thickness):
	if re.match('^VB.+', bond):
		return 1
	else:
		thickness = convert_mm_inch(thickness)
		if thickness < 1.2:
			return 3
		elif thickness < 2.2:
			return 2
		else:
			return 1
