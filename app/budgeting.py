from flask import Flask, render_template, url_for, g, request, abort
from flask_cas import CAS, login_required, login
from database import db, Conferences, ConferenceRates, People, ConferenceAttendee

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
@app.route('/conferences')
@login_required
def conferences():
	return render_template('conferences.html')


@app.route('/conferences/ajax/<path:path>')
@login_required
def get_conferences(path):
	filters = []
	if request.args.get('conferenceid'):
		filters.append(Conferences.conferenceid == request.args.get('conferenceid'))
	if request.args.get('meeting'):
		filters.append(Conferences.meeting == request.args.get('meeting'))

	conferences = Conferences.get_many(joins = [],
									   filters = filters,
									   orders = [])

	if path == 'edit':
		return render_template('conference-edit.html', conferences = conferences,
													   dd_fiscalyears = ['FY13', 'FY14', 'FY15', 'FY16', 'FY17', 'FY18', 'FY19', 'FY20', 'FY21'],
													   dd_startdates = ['10/01/2012', '10/01/2013', '10/01/2014', '10/01/2015', '10/01/2016',
					  													'10/01/2017', '10/01/2018', '10/01/2019', '10/01/2020'])
	elif path == 'get':
		return render_template('conferences-list-ajax.json', conferences = conferences)
	else:
		abort(404)


# CONFERENCE RATES
@app.route('/conferencerates/ajax/<path:path>')
@login_required
def get_conferencerates(path):
	filters = []
	if request.args.get('conferenceid'):
		filters.append(ConferenceRates.conferenceid == request.args.get('conferenceid'))
	if request.args.get('conferencerateid'):
		filters.append(ConferenceRates.conferencerateid == request.args.get('conferencerateid'))
	if request.args.get('effectivedate'):
		filters.append(ConferenceRates.effectivedate < request.args.get('effectivedate'))
	conferencerates = ConferenceRates.get_many(joins = [],
											   filters = filters,
											   orders = [ConferenceRates.effectivedate.desc()])

	if path == 'edit':
		return render_template('conference-rate-edit-ajax.json', conferencerates = conferencerates)
	elif path == 'get':
		return render_template('conference-rate-list-ajax.json', conferencerates = conferencerates)
	else:
		abort(404)

# CONFERENCE ATTENDEES
@app.route('/conferenceattendees/ajax/<path:path>')
@login_required
def get_conferenceattendees(path):
	filters = []
	if request.args.get('conferenceattendeeid'):
		filters.append(ConferenceAttendee.conferenceattendeeid == request.args.get('conferenceattendeeid'))
	if request.args.get('conferenceid'):
		filters.append(ConferenceAttendee.conferenceid == request.args.get('conferenceid'))
	if request.args.get('travelers'):
		filters.append(ConferenceAttendee.travelers == request.args.get('travelers'))
	if request.args.get('proposalid'):
		filters.append(ConferenceAttendee.proposalid == request.args.get('proposalid'))

	conferenceattendees = ConferenceAttendee.get_many(joins = [],
													  filters = filters,
													  orders = [])

	if path == 'edit':
		return render_template('conference-attendee-edit.html')
	elif path == 'get':
		return render_template('conference-attendee-list-ajax.json')

# PROPOSALS
@app.route('/proposals', methods=['GET', 'POST'])
@login_required
def proposals():
	return render_template('proposals.html')

@app.route('/proposals/ajax/<path:path>')
@login_required
def get_proposals():
	return render_template('proposal-list-ajax.json')

# people
@app.route('/people', methods=['GET'])
@login_required
def people():
	return render_template('people.html')

@app.route('/people/ajax/<path:path>', methods=['POST', 'GET'])
@login_required
def get_people(path):
	people = People.get_all()
	#people = People.get_many(joins = [Salaries])
	#						 filters = [People.name == name, People.title = title, People.])

	if path == 'edit':
		return render_template('people-edit.html')
	elif path == 'get':
		return render_template('people-list-ajax.json', people = people)


if __name__ == "__main__":
	app.run(host = '0.0.0.0', port = 5000)
