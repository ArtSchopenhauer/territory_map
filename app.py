from flask import Flask, render_template, jsonify, request, send_file
import json
import pytz
import datetime
import requests
from simple_salesforce import Salesforce
from flask_sqlalchemy import SQLAlchemy, sqlalchemy

sf = Salesforce(
    username='integration@levelsolar.com',
    password='HrNt7DrqaEfZmBqJRan9dKFzmQFp',
    security_token='yWlJG8lAKCq1pTBkbBMSVcKg')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////root/lboard/map-master/database.db'
db = SQLAlchemy(app)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    territory = db.Column(db.String)
    amb = db.Column(db.String)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def __init__(self, territory, amb, start, end):
        self.territory = territory
        self.amb = amb
        self.start = start
        self.end = end

    def __repr__(self):
        return '%r' % (self.amb)

def time_definitions():
	utc_zone = pytz.timezone('UTC')
 	est_zone = pytz.timezone('US/Eastern')
 	now_utc_naive = datetime.datetime.utcnow()
 	now_utc_aware = utc_zone.localize(now_utc_naive)
 	now_est_aware = now_utc_aware.astimezone(est_zone)
 	return now_est_aware

def get_ambassadors():
	amb_list = []
	ambassadors = sf.query_all("SELECT Name from Employee__c where Office__c != null and Status__c = 'Active'")["records"]
	for amb in ambassadors:
		amb_list.append(amb["Name"])
	ambs = sorted(amb_list)
	return ambs

def validate_assignment(ambassador):
	open_ambassador = Assignment.query.filter(Assignment.amb==ambassador, Assignment.end==None).first()
	alert = "Valid"
	if open_ambassador:
		alert = ambassador + " is currently assigned to " + open_ambassador.territory
	return alert

@app.route("/", methods=["GET", "POST"])
def map():
	if request.method == "POST":
		ambs = get_ambassadors()
		if "assign1" in request.form:
			assignment = request.form["assign1"]
			territory, amb = assignment.split('*')
			start = time_definitions()
			end = None
			alert = validate_assignment(amb)
			if alert != "Valid":
				return alert
			else:
				record = Assignment(territory, amb, start, end)
				db.session.add(record)
				db.session.commit()
				return "Valid"
		elif "unassign2" in request.form:
			territory = request.form["unassign2"]
			record = Assignment.query.filter(Assignment.territory==territory, Assignment.end==None).first()
			record.end = time_definitions()
			db.session.commit()
			return "Valid"
	else:
		ambs = get_ambassadors()
		open_assignments = Assignment.query.filter(Assignment.end==None).all()
		once_assigned = Assignment.query.filter(Assignment.end!=None).all()
		assigned_territories = []
		past_assignments = []
		for a in open_assignments:
			assigned_territories.append(a.territory)
		for o in once_assigned:
			past_assignments.append(o.territory)
		return render_template("map2.html", ambs=ambs, assigned="Default", assigned_territories=json.dumps(assigned_territories), past_assignments=json.dumps(past_assignments))

@app.route("/geojson")
def geojson():
	return send_file("1014.json", mimetype='application/vnd.geo+json')

@app.route("/kml")
def kml():
	return send_file("test2.kml", mimetype='application/vnd.google-earth.kml+xml')

@app.route("/status", methods=["POST"])
def status():
	if request.method == "POST":
		territory = request.form["territory"]
		assignments = Assignment.query.filter(Assignment.territory==territory).all()
		currently_assigned = "Unassigned"
		all_assignments = []
		if assignments:
			for a in assignments:
				amb = a.amb
				if a.end == None:
					currently_assigned = amb
				if a.start:
					start = str(a.start.month) + "/" + str(a.start.day) + "/" + str(a.start.year)
				else:
					start = "None"
				if a.end:
					end = str(a.end.month) + "/" + str(a.end.day) + "/" + str(a.end.year)
				else:
					end = "None"
				record = {"amb": amb, "start": start, "end": end}
				all_assignments.append(record)
		else:
			amb = "Unassigned"
		info = {"currently_assigned": currently_assigned, "all_assignments": all_assignments}
		return json.dumps(info)

if __name__ == "__main__":
	app.run(debug=True)
