from flask import Flask, render_template, redirect, url_for, g, session
from flask_cas import CAS, login_required, login
from database import db, Conferences, ConferenceRates, People

def currencyformat(value):
	if value is None:
		return '$0.00'
	return "${:,.2f}".format(value)

def dateformat(value, format='%m/%d/%Y'):
	return value.strftime(format)


app = Flask(__name__)
cas = CAS(app, '/cas')
app.config.from_object('config.Dev')
app.jinja_env.filters['currencyformat'] = currencyformat
app.jinja_env.filters['dateformat'] = dateformat
db.init_app(app)

@app.before_request
def check_login():
	if cas.username:
		g.user = People.get_one(filters = [People.username == cas.username])
	
@app.route('/')
@login_required
def main():
	return render_template('default.html')


# CONFERENCES
@app.route('/conferences', methods=['GET'])
@login_required
def conferences():
	return render_template('conferences.html')

@app.route('/conferences/edit/<int:conferenceid>', methods=['POST', 'GET'])
@login_required
def edit_conference(conferenceid):
	conference = Conferences.get_one(filters = [Conferences.conferenceid == conferenceid])
	dd_fiscalyears = ['FY13', 'FY14', 'FY15', 'FY16', 'FY17', 'FY18', 'FY19', 'FY20', 'FY21']
	dd_startdates = ['10/01/2012', '10/01/2013', '10/01/2014', '10/01/2015', '10/01/2016',
				'10/01/2017', '10/01/2018', '10/01/2019', '10/01/2020']
	return render_template('conference-edit.html', conference = conference, 
												   dd_fiscalyears = dd_fiscalyears,
												   dd_startdates = dd_startdates)

@app.route('/ajax/get/conferences', methods=['POST', 'GET'])
@login_required
def get_conferences():
	conferences = Conferences.get_all()
	return render_template('conferences-list-ajax.json', conferences = conferences)


# CONFERENCE RATES
@app.route('/conferencerates/edit/<int:conferencerateid>', methods=['POST', 'GET'])
@login_required
def edit_conferencerate(conferencerateid):
	conferencerates = [ConferenceRates.get_one(filters = [ConferenceRates.conferencerateid == conferencerateid])]
	return render_template('conference-rate-edit-ajax.json', conferencerates = conferencerates)

@app.route('/ajax/get/conferencerates/<int:conferenceid>', methods=['POST', 'GET'])
@login_required
def get_conferencerates(conferenceid):
	conferencerates = ConferenceRates.get_many(joins = [], 
											   filters = [ConferenceRates.conferenceid == conferenceid], 
											   orders = [ConferenceRates.effectivedate.desc()])
	return render_template('conference-rate-list-ajax.json', conferencerates = conferencerates)

# CONFERENCE ATTENDEES
@app.route('/ajax/get/conferenceattendees/<int:conferenceid>', methods=['POST', 'GET'])
@login_required
def get_conferenceattendees():
	pass


if __name__ == "__main__":
	app.run(host = '0.0.0.0', port = 5000)
