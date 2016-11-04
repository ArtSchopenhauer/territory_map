import csv
import datetime
from app import db, Assignment

def add_assignments():
	with open("past_assignments.csv") as csvfile:
		csv_r = csv.DictReader(csvfile)
		for row in csv_r:
			territory = row["territory"]
			amb = row["amb"]
			print territory + " " + amb
			start_month = int(row["start_month"])
			start_day = int(row["start_day"])
			start_year = int(row["start_year"])
			start = datetime.date(start_year, start_month, start_day)
			if int(row["end_year"]) == 0:
				end = None
			else:
				end_month = int(row["end_month"])
				end_day = int(row["end_day"])
				end_year = int(row["end_year"])
				end = datetime.date(end_year, end_month, end_day)
			record = Assignment(territory, amb, start, end)
			db.session.add(record)
			db.session.commit()
	csvfile.close()

add_assignments()