from flask import Flask, render_template, url_for, g, request, abort
from flask_cas import CAS, login_required, login
from database import (db, Conferences, ConferenceRates, ConferenceAttendee, Expenses, ExpenseTypes,
					  Funding, FundingPrograms, OverheadRates, People, Proposals, Salaries, Staffing,
					  Tasks)

def currencyformat(value):
	if value is None:
		return '$0.00'
	return "${:,.2f}".format(value)

def dateformat(datestring, format='%m/%d/%Y'):
	return datestring.strftime(format)

def floatformat(value):
	if value is None:
		return '0.00'
	return "{:,.2f}".format(value)

def intformat(value):
	if value is None:
		return '0'
	return "{:,}".format(value)

def jsonformat(string):
	string = string.replace("'", r"\'")
	string = string.replace('"', r'\"')
	return string

def fyformat(datestring):
	month = datestring.month
	day = datestring.day
	year = datestring.year
	if month >= 10 and day >= 1:
		year_string = "FY" + str(year+1).replace("20", "")
	else:
		year_string = "FY" + str(year).replace("20", "")
	return year_string

app = Flask(__name__)
cas = CAS(app, '/cas')
app.config.from_object('config.Dev')
app.jinja_env.filters['currencyformat'] = currencyformat
app.jinja_env.filters['dateformat'] = dateformat
app.jinja_env.filters['intformat'] = intformat
app.jinja_env.filters['jsonformat'] = jsonformat
app.jinja_env.filters['fyformat'] = fyformat
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
	else:
		abort(404)

# EXPENSES
@app.route('/expenses/ajax/<path:path>')
@login_required
def get_expenses(path):
	filters = []
	if request.args.get('proposalid'):
		filters.append(Expenses.proposalid == request.args.get('proposalid'))
	if request.args.get('expenseid'):
		filters.append(Expenses.expenseid == request.args.get('expenseid'))

	expenses = Expenses.get_many(joins = [], filters = filters, orders = [])

	if path == 'edit':
		return render_template('expense-edit.html', expenses = expenses)
	elif path == 'get':
		return render_template('expense-list-ajax.json', expenses = expenses)
	else:
		abort(404)

# EXPENSE TYPES
@app.route('/expensetypes')
@login_required
def expensetypes():
	return render_template('expensetypes.html')

@app.route('/expensetypes/ajax/<path:path>')
@login_required
def get_expensetypes(path):
	filters = []
	if request.args.get('expensetypeid'):
		filters.append(ExpenseTypes.expensetypeid == request.args.get('expensetypeid'))

	expensetypes = ExpenseTypes.get_many(joins = [], filters = filters, orders = [])

	if path == 'edit':
		return render_template('expensetype-edit.html', expensetypes = expensetypes)
	elif path == 'get':
		return render_template('expensetypes-list-ajax.json', expensetypes = expensetypes)
	else:
		abort(404)

# FUNDING
@app.route('/funding/ajax/<path:path>')
@login_required
def get_funding(path):
	filters = []
	if request.args.get('fundingid'):
		filters.append(Funding.fundingid == request.args.get('fundingid'))
	if request.args.get('proposalid'):
		filters.append(Funding.proposalid == request.args.get('proposalid'))

	funding = Funding.get_many(joins = [], filters = filters, orders = [])

	if path == 'get':
		return render_template('funding-list-ajax.json', funding = funding)
	else:
		abort(404)

# PROGRAMS
@app.route('/programs')
@login_required
def programs():
	return render_template('programs.html')

@app.route('/programs/ajax/<path:path>')
@login_required
def get_programs(path):
	filters = []
	if request.args.get('programid'):
		filters.append(FundingPrograms.programid == request.args.get('programid'))

	programs = FundingPrograms.get_many(joins = [], filters = filters, orders = [])

	if path == 'edit':
		return render_template('programs-edit.html', programs = programs,
													 dd_fiscalyears = ['FY13', 'FY14', 'FY15', 'FY16', 'FY17', 'FY18', 'FY19', 'FY20', 'FY21'],
													 dd_startdates = ['10/01/2012', '10/01/2013', '10/01/2014', '10/01/2015', '10/01/2016',
					  													'10/01/2017', '10/01/2018', '10/01/2019', '10/01/2020'])
	elif path == 'get':
		return render_template('programs-list-ajax.json', programs = programs)
	else:
		abort(404)



# overhead
@app.route('/overhead', methods=['GET', 'POST'])
@login_required
def overhead():
	return render_template('overheads.html')

@app.route('/overhead/ajax/<path:path>')
@login_required
def get_overhead(path):
	filters = []

	if request.args.get('proposalid'):
		if request.args.get('proposalid') == 'null':
			filters.append(OverheadRates.proposalid == None)
		else:
			filters.append(OverheadRates.proposalid == request.args.get('proposalid'))
	#if request.args.get('_'):
	#	filters.append(OverheadRates.proposalid == request.args.get('_'))


	overheadrates = OverheadRates.get_many(joins = [], filters = filters, orders = [])
	#overhead = OverheadRates.get_all()

	if path == 'get':
		return render_template('overhead-list-ajax.json', overheadrates = overheadrates)
		#return render_template('overhead-list-ajax.json')
	else:
		abort(404)


# PROPOSALS
@app.route('/proposals')
@login_required
def proposals():
	return render_template('proposals.html')

@app.route('/proposals/ajax/<path:path>')
@login_required
def get_proposals(path):
	filters = []
	if request.args.get('proposalid'):
		filters.append(Proposals.proposalid == request.args.get('proposalid'))

	proposals = Proposals.get_many(joins = [], filters = filters, orders = [])

	if path == 'edit':
		return render_template('proposal-edit.html', proposals = proposals)
	elif path == 'get':
		return render_template('proposal-list-ajax.json', proposals = proposals)
	else:
		abort(404)

@app.route('/proposal-basis/<int:proposalid>')
@app.route('/proposal-budget/<int:proposalid>')
@app.route('/proposal-nspires/<int:proposalid>')
@app.route('/proposal-roses/<int:proposalid>')
@login_required
def budget_reports(proposalid):
	proposals = Proposals.get_many(joins = [], filters = [Proposals.proposalid == proposalid], orders = [])

	route = request.url_rule
	if 'basis' in route.rule:
		return render_template('proposal-basis.html', proposals = proposals)
	elif 'budget' in route.rule:
		return render_template('proposal-budget-details.html', proposals = proposals)
	elif 'nspires' in route.rule:
		return render_template('proposal-nspires.html', proposals = proposals)
	elif 'roses' in route.rule:
		return render_template('proposal-roses.html', proposals = proposals)
	else:
		abort(404)

# PEOPLE
@app.route('/people')
@login_required
def people():
	return render_template('people.html')


@app.route('/people/ajax/<path:path>')
@login_required
def get_people(path):
	filters = []
	if path == 'task':
		if request.args.get('peopleid'):
			filters.append(Staffing.peopleid == request.args.get('peopleid'))
	else:
		if request.args.get('peopleid'):
			filters.append(People.peopleid == request.args.get('peopleid'))
	#if request.args.get('name'):
	#	filters.append(People.name == request.args.get('name'))

	people = People.get_many(joins = [Salaries],
						     filters = filters,
							 orders = [])

	staffing = Staffing.get_many(joins = [Tasks, People, Proposals],
								 filters = filters,
								 orders = [])

	if path == 'dropdown':
		return render_template('people-dropdown-list-ajax.json', people = people)
	elif path == 'edit':
		return render_template('people-edit.html', people = people)
	elif path == 'get':
		return render_template('people-list-ajax.json', people = people)
	elif path == 'task':
		return render_template('people-task-list-ajax.json', staffing = staffing)
	else:
		abort(404)


# SALARIES
@app.route('/salary/ajax/<path:path>', methods=['POST', 'GET'])
@login_required
def getSalaries(path):
	filters = []
	if request.args.get('peopleid'):
		filters.append(Salaries.peopleid == request.args.get('peopleid'))

	salaries = Salaries.get_many(joins = [], filters = filters, orders = [])

	if path == 'edit':
		return render_template('salary-edit-ajax.json', salaries = salaries)
	elif path == 'get':
		return render_template('salary-list-ajax.json', salaries = salaries)
	else:
		abort(404)



# TASKS
@app.route('/tasks/ajax/<path:path>')
@login_required
def get_tasks(path):
	filters = []
	if request.args.get('proposalid'):
		filters.append(Tasks.proposalid == request.args.get('proposalid'))
	if request.args.get('taskid'):
		filters.append(Tasks.taskid == request.args.get('taskid'))

	tasks = Tasks.get_many(joins = [], filters = filters, orders = [])

	if path == 'dropdown':
		return render_template('tasks-dropdown-ajax.json', tasks = tasks)
	elif path == 'edit':
		return render_template('task-edit.html', tasks = tasks)
	elif path == 'get':
		return render_template('tasks-list-ajax.json', tasks = tasks)

if __name__ == "__main__":
	app.run(host = '0.0.0.0', port = 5000)
