from flask import Flask, render_template, url_for, g, request, abort
from flask_cas import CAS, login_required, login
import datetime
from database import (db, Conferences, ConferenceRates, ConferenceAttendee, Expenses, ExpenseTypes, FBMSAccounts,
					  Funding, FundingPrograms, OverheadRates, People, Proposals, Salaries, Staffing,
					  Statuses, Tasks)

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

def fydateformat(datestring):
	month = datestring.month
	day = datestring.day
	year = datestring.year
	if month >= 10 and day >= 1:
		fy_year = year
		fy_date = datetime.date(fy_year, 10, 1)
	else:
		fy_year = year - 1
		fy_date = datetime.date(fy_year, 10, 1)
	return fy_date.strftime('%m/%d/%Y')

def fyformat(datestring):
	month = datestring.month
	day = datestring.day
	year = datestring.year
	if month >= 10 and day >= 1:
		year_string = "FY" + str(year+1).replace("20", "", 1)
	else:
		year_string = "FY" + str(year).replace("20", "", 1)
	return year_string

def fiscal_years():
	return ['FY13', 'FY14', 'FY15', 'FY16', 'FY17', 'FY18', 'FY19', 'FY20', 'FY21']

def start_dates():
	return ['10/01/2012', '10/01/2013', '10/01/2014', '10/01/2015', '10/01/2016',
			'10/01/2017', '10/01/2018', '10/01/2019', '10/01/2020']

app = Flask(__name__)
cas = CAS(app, '/cas')
app.config.from_object('config.Dev')
app.jinja_env.filters['currencyformat'] = currencyformat
app.jinja_env.filters['dateformat'] = dateformat
app.jinja_env.filters['intformat'] = intformat
app.jinja_env.filters['jsonformat'] = jsonformat
app.jinja_env.filters['fyformat'] = fyformat
app.jinja_env.filters['fydateformat'] = fydateformat
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

'''
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
													   dd_fiscalyears = fiscal_years(),
													   dd_startdates = start_dates())
	elif path == 'get':
		return render_template('conferences-list-ajax.json', conferences = conferences)
	else:
		abort(404)
'''

@app.route('/conferences/ajax/edit/<int:conferenceid>')
@login_required
def edit_conferences(conferenceid):
	conferences = Conferences.get_many(joins = [],
									   filters = [Conferences.conferenceid == conferenceid],
									   orders = [])
	return render_template('conference-edit.html', conferences = conferences,
												   dd_fiscalyears = fiscal_years(),
												   dd_startdates = start_dates())

@app.route('/conferences/ajax/list')
@login_required
def load_conferences():
	conferences = Conferences.get_many(joins = [], filters = [], orders = [])
	return render_template('conferences-list-ajax.json', conferences = conferences)


# CONFERENCE ATTENDEES
'''
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
		return render_template('conference-attendee-edit.html', conferenceattendees = conferenceattendees)
	elif path == 'get':
		return render_template('conference-attendee-list-ajax.json', conferenceattendees = conferenceattendees)
	else:
		abort(404)
'''

@app.route('/conferenceattendees/ajax/edit')
@login_required
def edit_conferenceattendees():
	filters = []
	if request.args.get('conferenceattendeeid'):
		filters.append(ConferenceAttendee.conferenceattendeeid == request.args.get('conferenceattendeeid'))
	if request.args.get('conferenceid'):
		filters.append(ConferenceAttendee.conferenceid == request.args.get('conferenceid'))
	if request.args.get('travelers'):
		filters.append(ConferenceAttendee.travelers == request.args.get('travelers'))
	if request.args.get('proposalid'):
		filters.append(ConferenceAttendee.proposalid == request.args.get('proposalid'))

	conferenceattendees = ConferenceAttendee.get_many(joins = [], filters = filters, orders = [])
	return render_template('conference-attendee-edit.html', conferenceattendees = conferenceattendees)

@app.route('/conferenceattendees/ajax/list/<int:proposalid>')
@login_required
def load_conferenceattendees(proposalid):
	conferenceattendees = ConferenceAttendee.get_many(joins = [],
													  filters = [ConferenceAttendee.proposalid == proposalid],
													  orders = [])
	return render_template('conference-attendee-list-ajax.json', conferenceattendees = conferenceattendees)


# CONFERENCE RATES
'''
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
'''

@app.route('/conferencerates/ajax/edit/<int:conferencerateid>')
@login_required
def edit_conferencerates(conferencerateid):
	conferencerates = ConferenceRates.get_many(joins = [],
											   filters = [ConferenceRates.conferencerateid == conferencerateid],
											   orders = [ConferenceRates.effectivedate.desc()])
	return render_template('conference-rate-edit-ajax.json', conferencerates = conferencerates)

@app.route('/conferencerates/ajax/list/<int:conferenceid>')
@login_required
def load_conferencerates(conferenceid):
	conferencerates = ConferenceRates.get_many(joins = [],
											   filters = [ConferenceRates.conferenceid == conferenceid],
											   orders = [ConferenceRates.effectivedate.desc()])
	return render_template('conference-rate-list-ajax.json', conferencerates = conferencerates)


# EXPENSES
'''
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
'''

@app.route('/expenses/ajax/edit/<int:expenseid>')
@login_required
def edit_expenses(expenseid):
	expenses = Expenses.get_many(joins = [],
								 filters = [Expenses.expenseid == expenseid],
								 orders = [])
	return render_template('expense-edit.html', expenses = expenses)

@app.route('/expenses/ajax/list/<int:proposalid>')
@login_required
def load_expenses(proposalid):
	expenses = Expenses.get_many(joins = [],
								 filters = [Expenses.proposalid == proposalid],
								 orders = [])
	return render_template('expense-list-ajax.json', expenses = expenses)


# EXPENSE TYPES
@app.route('/expensetypes')
@login_required
def expensetypes():
	return render_template('expensetypes.html')

'''
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
'''

@app.route('/expensetypes/ajax/edit/<int:expensetypeid>')
@login_required
def edit_expensetypes(expensetypeid):
	expensetypes = ExpenseTypes.get_many(joins = [],
										 filters = [ExpenseTypes.expensetypeid == expensetypeid],
										 orders = [])
	return render_template('expensetype-edit.html', expensetypes = expensetypes)

@app.route('/expensetypes/ajax/list')
@login_required
def load_expensetypes():
	expensetypes = ExpenseTypes.get_many(joins = [], filters = [], orders = [])
	return render_template('expensetypes-list-ajax.json', expensetypes = expensetypes)


# FBMSACCOUNTS
'''
@app.route('/fbmsaccounts/ajax/<path:path>')
@login_required
def get_fbmsaccounts(path):
	filters = []
	if request.args.get('proposalid'):
		filters.append(FBMSAccounts.proposalid == request.args.get('proposalid'))

	fbmsaccounts = FBMSAccounts.get_many(joins = [], filters = filters, orders = [])

	if path == 'edit':
		return render_template('fbms-edit.html', fbmsaccounts = fbmsaccounts)
	elif path == 'get':
		return render_template('fbms-list-ajax.json', fbmsaccounts = fbmsaccounts)
	else:
		abort(404)
'''

@app.route('/fbmsaccounts/ajax/edit/<int:proposalid>')
@login_required
def edit_fbmsaccounts(proposalid):
	fbmsaccounts = FBMSAccounts.get_many(joins = [],
										 filters = [FBMSAccounts.proposalid == proposalid],
										 orders = [])
	return render_template('fbms-edit.html', fbmsaccounts = fbmsaccounts)

@app.route('/fbmsaccounts/ajax/list/<int:proposalid>')
@login_required
def load_fbmsaccounts(proposalid):
	fbmsaccounts = FBMSAccounts.get_many(joins = [],
										 filters = [FBMSAccounts.proposalid == proposalid],
										 orders = [])
	return render_template('fbms-list-ajax.json', fbmsaccounts = fbmsaccounts)


# FUNDING
'''
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
'''

@app.route('/funding/ajax/delete')
@login_required
def delete_funding():
	# need to figure out how to remove items from the database with sqlalchemy

	# requirements:
		# update any fundings using the value that's being deleted to a default
		# will the whole table need to be looked through and changed?
			# could it be filtered by the name of the funding program?

	# return message for the div
	return ""

@app.route('/funding/ajax/edit/<int:fundingid>')
@login_required
def edit_funding(fundingid):
	funding = Funding.get_many(joins = [], filters = [Funding.fundingid == fundingid],
							   orders = [])
	return render_template('funding-edit.html', funding = funding,
	 						dd_fiscalyears = fiscal_years(),
							dd_startdates = start_dates())

@app.route('/funding/ajax/list')
@login_required
def load_funding():
	filters = []
	if request.args.get('fundingid'):
		filters.append(Funding.fundingid == request.args.get('fundingid'))
	if request.args.get('proposalid'):
		filters.append(Funding.proposalid == request.args.get('proposalid'))

	funding = Funding.get_many(joins = [], filters = filters, orders = [])
	return render_template('funding-list-ajax.json', funding = funding)

@app.route('/funding/ajax/save')
@login_required
def save_funding():
	# update if already existing
	# make a new one if it is a new funding program

	funding_proposalid = request.args.get('proposalid')
	funding_fundingid = request.args.get('fundingid')
	funding_fiscalyear = request.args.get('fiscalyear')
	funding_newfunding = request.args.get('newfunding')
	funding_carryover = request.args.get("carryover")

	# return the message for the div
	return ""


# OVERHEAD
@app.route('/overhead')
@login_required
def overhead():
	return render_template('overheads.html')

'''
@app.route('/overhead/ajax/<path:path>')
@login_required
def get_overhead(path):
	filters = []

	if request.args.get('proposalid'):
		if request.args.get('proposalid') == 'null':
			filters.append(OverheadRates.proposalid == None)
		else:
			filters.append(OverheadRates.proposalid == request.args.get('proposalid'))

	overheadrates = OverheadRates.get_many(joins = [], filters = filters, orders = [])
	if not overheadrates:
		overheadrates = OverheadRates.get_many(joins = [], filters = [OverheadRates.proposalid == None], orders = [])

	if path == 'edit':
		return render_template('overhead-edit.html', overheadrates = overheadrates)
	elif path == 'get':
		return render_template('overhead-list-ajax.json', overheadrates = overheadrates)
	else:
		abort(404)
'''

@app.route('/overhead/ajax/edit')
@login_required
def edit_overhead():
	filters = []
	if request.args.get('proposalid'):
		if request.args.get('proposalid') == 'null':
			filters.append(OverheadRates.proposalid == None)
		else:
			filters.append(OverheadRates.proposalid == request.args.get('proposalid'))

	overheadrates = OverheadRates.get_many(joins = [], filters = filters, orders = [])
	if not overheadrates:
		overheadrates = OverheadRates.get_many(joins = [], filters = [OverheadRates.proposalid == None], orders = [])

	return render_template('overhead-edit.html', overheadrates = overheadrates)

@app.route('/overhead/ajax/get')
@login_required
def load_overhead():
	filters = []
	if request.args.get('proposalid'):
		if request.args.get('proposalid') == 'null':
			filters.append(OverheadRates.proposalid == None)
		else:
			filters.append(OverheadRates.proposalid == request.args.get('proposalid'))

	overheadrates = OverheadRates.get_many(joins = [], filters = filters, orders = [])
	if not overheadrates:
		overheadrates = OverheadRates.get_many(joins = [], filters = [OverheadRates.proposalid == None], orders = [])

	return render_template('overhead-list-ajax.json', overheadrates = overheadrates)


# PEOPLE
@app.route('/people')
@login_required
def people():
	return render_template('people.html')

'''
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

	people = People.get_many(joins = [Salaries],
						     filters = filters,
							 orders = [])

	staffing = Staffing.get_many(joins = [Tasks, People, Proposals],
								 filters = filters,
								 orders = [])

	if path == 'dropdown':
		return render_template('people-dropdown-list-ajax.json', people = people)
	elif path == 'edit':
		return render_template('people-edit.html', people = people,
												   dd_fiscalyears = fiscal_years(),
												   dd_startdates = start_dates())
	elif path == 'get':
		return render_template('people-list-ajax.json', people = people)
	elif path == 'task':
		return render_template('people-task-list-ajax.json', staffing = staffing)
	else:
		abort(404)
'''


@app.route('/people/ajax/dropdown')
@login_required
def people_dropdown():
	filters = []
	if request.args.get('peopleid'):
		filters.append(People.peopleid == request.args.get('peopleid'))
	people = People.get_many(joins = [Salaries], filters = filters, orders = [])
	return render_template('people-dropdown-list-ajax.json', people = people)


@app.route('/people/ajax/edit')
@login_required
def edit_people():
	filters = []
	if request.args.get('peopleid'):
		filters.append(People.peopleid == request.args.get('peopleid'))

	people = People.get_many(joins = [Salaries], filters = filters, orders = [])

	return render_template('people-edit.html', people = people,
											   dd_fiscalyears = fiscal_years(),
											   dd_startdates = start_dates())

@app.route('/people/ajax/get')
@login_required
def load_people():
	filters = []
	people = People.get_many(joins = [Salaries],
									  filters = filters,
									  orders = [])
	return render_template('people-list-ajax.json', people = people)

@app.route('/people/ajax/task')
@login_required
def load_staffing():
	filters = []
	if request.args.get('peopleid'):
		filters.append(Staffing.peopleid == request.args.get('peopleid'))
	staffing = Staffing.get_many(joins = [Tasks, People, Proposals],
										  filters = filters,
										  orders = [])
	return render_template('people-task-list-ajax.json', staffing = staffing)


# PROGRAMS
@app.route('/programs')
@login_required
def programs():
	return render_template('programs.html')

'''
@app.route('/programs/ajax/<path:path>')
@login_required
def get_programs(path):
	filters = []
	if request.args.get('programid'):
		filters.append(FundingPrograms.programid == request.args.get('programid'))

	programs = FundingPrograms.get_many(joins = [], filters = filters, orders = [])

	if path == 'edit':
		return render_template('programs-edit.html', programs = programs,
													 dd_fiscalyears = fiscal_years(),
													 dd_startdates = start_dates())
	elif path == 'get':
		return render_template('programs-list-ajax.json', programs = programs)
	else:
		abort(404)
'''

@app.route('/programs/ajax/edit')
@login_required
def edit_program():
	filters = []
	if request.args.get('programid'):
		filters.append(FundingPrograms.programid == request.args.get('programid'))

	programs = FundingPrograms.get_many(joins = [], filters = filters, orders = [])
	return render_template('programs-edit.html', programs = programs,
												 dd_fiscalyears = fiscal_years(),
												 dd_startdates = start_dates())

@app.route('/programs/ajax/get')
@login_required
def load_programs():
	filters = []
	programs = FundingPrograms.get_many(joins = [], filters = filters, orders = [])
	return render_template('programs-list-ajax.json', programs = programs)


# PROPOSALS
@app.route('/proposals')
@login_required
def proposals():
	return render_template('proposals.html')

'''
@app.route('/proposals/ajax/<path:path>')
@login_required
def get_proposals(path):
	filters = []
	if request.args.get('proposalid'):
		filters.append(Proposals.proposalid == request.args.get('proposalid'))

	proposals = Proposals.get_many(joins = [], filters = filters, orders = [])

	if path == 'edit':
		return render_template('proposal-edit.html', proposals = proposals,
													 people = People.get_all(orders = [People.name]),
													 programs = FundingPrograms.get_all(orders = [FundingPrograms.programname]),
													 statuses = Statuses.get_all(orders = [Statuses.statusname]),
													 dd_fiscalyears = fiscal_years(),
													 dd_startdates = start_dates())
	elif path == 'get':
		return render_template('proposal-list-ajax.json', proposals = proposals)
	else:
		abort(404)
'''

@app.route('/proposals/ajax/edit')
@login_required
def edit_proposal():
	filters = []
	if request.args.get('proposalid'):
		filters.append(Proposals.proposalid == request.args.get('proposalid'))

	proposals = Proposals.get_many(joins = [], filters = filters, orders = [])
	return render_template('proposal-edit.html', proposals = proposals,
												 people = People.get_all(orders = [People.name]),
												 programs = FundingPrograms.get_all(orders = [FundingPrograms.programname]),
												 statuses = Statuses.get_all(orders = [Statuses.statusname]),
												 dd_fiscalyears = fiscal_years(),
												 dd_startdates = start_dates())

@app.route('/proposals/ajax/get')
@login_required
def load_proposals():
	filters = []
	proposals = Proposals.get_many(joins = [], filters = filters, orders = [])
	return render_template('proposal-list-ajax.json', proposals = proposals)


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


# REPORTS
@app.route('/reports')
@login_required
def reports():
	return render_template('reports.html')


# SALARIES
'''
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
'''

@app.route('/salary/ajax/edit')
@login_required
def edit_salary():
	filters = []
	if request.args.get('peopleid'):
		filters.append(Salaries.peopleid == request.args.get('peopleid'))

	salaries = Salaries.get_many(joins = [], filters = filters, orders = [])
	return render_template('salary-edit-ajax.json', salaries = salaries)

@app.route('/salary/ajax/get')
@login_required
def load_salaries():
	filters = []
	if request.args.get('peopleid'):
		filters.append(Salaries.peopleid == request.args.get('peopleid'))

	salaries = Salaries.get_many(joins = [], filters = filters, orders = [])
	return render_template('salary-list-ajax.json', salaries = salaries)


# TASKS
'''
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
'''


@app.route('/tasks/ajax/dropdown')
@login_required
def task_dropdown():
	filters = []
	if request.args.get('proposalid'):
		filters.append(Tasks.proposalid == request.args.get('proposalid'))
	tasks = Tasks.get_many(joins = [], filters = filters, orders = [])
	return render_template('tasks-dropdown-ajax.json', tasks = tasks)

@app.route('/tasks/ajax/edit')
@login_required
def edit_task():
	if request.args.get('proposalid'):
		filters.append(Tasks.proposalid == request.args.get('proposalid'))
	if request.args.get('taskid'):
		filters.append(Tasks.taskid == request.args.get('taskid'))

	tasks = Tasks.get_many(joins = [], filters = filters, orders = [])
	return render_template('task-edit.html', tasks = tasks)

@app.route('/tasks/ajax/get')
@login_required
def load_tasks():
	filters = []
	if request.args.get('proposalid'):
		filters.append(Tasks.proposalid == request.args.get('proposalid'))

	tasks = Tasks.get_many(joins = [], filters = filters, orders = [])
	return render_template('tasks-list-ajax.json', tasks = tasks)


if __name__ == "__main__":
	app.run(host = '0.0.0.0', port = 5000)
