#
import csv
scores_path = 'C:\Users\Joe\Dropbox\jobland\ulti scraping\ultiscores\test_out.csv'

gamedata = []
with open(scores_path, 'rb') as f:
	rdr = csv.reader(f)
	print rdr[0]