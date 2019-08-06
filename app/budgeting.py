from flask import Flask, render_template, url_for, g, request, abort, session
from flask_cas import CAS, login_required, login
from datetime import datetime, date
from database import (db, Conferences, ConferenceRates, ConferenceAttendee, Expenses, ExpenseTypes, FBMSAccounts,
					  Funding, FundingPrograms, OverheadRates, People, Proposals, Salaries, Staffing,
					  Statuses, Tasks)

# Jinja Filters ------------------>
def currencyformat(value):
	if value is None:
		return '$0.00'
	return "${:,.2f}".format(value)

def dateformat(datestring):
	if not datestring:
		return datestring
	else:
		return datestring.strftime('%m/%d/%Y')

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
	if not datestring:
		return datestring
	month = datestring.month
	day = datestring.day
	year = datestring.year
	if month >= 10 and day >= 1:
		fy_year = year
		fy_date = date(fy_year, 10, 1)
	else:
		fy_year = year - 1
		fy_date = date(fy_year, 10, 1)
	return fy_date.strftime('%m/%d/%Y')

def fyformat(datestring):
	if not datestring:
		return datestring
	month = datestring.month
	day = datestring.day
	year = datestring.year
	if month >= 10 and day >= 1:
		year_string = "FY" + str(year+1).replace("20", "", 1)
	else:
		year_string = "FY" + str(year).replace("20", "", 1)
	return year_string

def geteffective(list, cutoff_date = date.today()):
	effective_item = None
	if cutoff_date != date.today():
		cutoff_date = datetime.strptime(cuttoff_date)

	for item in list:
		if item.effectivedate.date() <= cutoff_date:
			effective_item = item
	return effective_item
# ------------------------------

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
app.jinja_env.filters['floatformat'] = floatformat
app.jinja_env.filters['intformat'] = intformat
app.jinja_env.filters['jsonformat'] = jsonformat
app.jinja_env.filters['fyformat'] = fyformat
app.jinja_env.filters['fydateformat'] = fydateformat
app.jinja_env.filters['geteffective'] = geteffective
db.init_app(app)

@app.before_request
def check_login():
	if cas.username:
		g.user = People.get_one(filters = [People.username == cas.username])
		session.permanent = True

@app.route('/')
@login_required
def home():
	return render_template('default.html')

# CONFERENCES

@app.route('/conferences')
@login_required
def conferences():
	return render_template('conferences.html')

@app.route('/conferences/ajax/edit/<int:conferenceid>')
@login_required
def edit_conference(conferenceid):
	conference = Conferences.get_one([Conferences.conferenceid == conferenceid])
	return render_template('conference-edit.html', conference = conference,
												   dd_fiscalyears = fiscal_years(),
												   dd_startdates = start_dates())

@app.route('/conferences/ajax/list')
@login_required
def load_conferences():
	conferences = Conferences.get_many(joins = [], filters = [], orders = [])
	return render_template('conferences-list-ajax.json', conferences = conferences)


# CONFERENCE ATTENDEES

@app.route('/conferenceattendees/ajax/delete/<int:conferenceattendeeid>&<proposalid>')
@login_required
def delete_conferenceattendee(conferenceattendeeid, proposalid):
	conference_attendee = ConferenceAttendee.get_one(filters = [ConferenceAttendee.conferenceattendeeid == conferenceattendeeid,
																 ConferenceAttendee.proposalid == proposalid])

	if not conference_attendee:
		return "null"

	text = "Start date: " + dateformat(conference_attendee.startdate) + " meeting: " + conference_attendee.conference.meeting
	return text

@app.route('/conferenceattendees/ajax/edit/<int:conferenceattendeeid>')
@login_required
def edit_conferenceattendee(conferenceattendeeid):
	conferenceattendee = ConferenceAttendee.get_one(filters = [ConferenceAttendee.conferenceattendeeid == conferenceattendeeid])
	return render_template('conference-attendee-edit.html', conferenceattendee = conferenceattendee,
															conferences = Conferences.get_all(orders = [Conferences.meeting]),
															dd_fiscalyears = fiscal_years(),
															dd_startdates = start_dates())

@app.route('/conferenceattendees/ajax/list/byproposal/<int:id>')
@app.route('/conferenceattendees/ajax/list/byconference/<int:id>')
@login_required
def load_conferenceattendees(id):
	filters = []
	route = request.url_rule
	if 'byproposal' in route.rule:
		filters.append(ConferenceAttendee.proposalid == id)
	if 'byconference' in route.rule:
		filters.append(ConferenceAttendee.conferenceid == id)

	conferenceattendees = ConferenceAttendee.get_many(joins = [], filters = filters, orders = [])
	return render_template('conference-attendee-list-ajax.json', conferenceattendees = conferenceattendees)

@app.route('/conferenceattendees/ajax/save/<int:conferenceattendeeid>', methods = ['GET','POST'])
@login_required
def save_conferenceattendee(conferenceattendeeid):
	meeting = request.form.get("meeting")
	meeting_days = request.form.get("meetingdays")
	travel_days = request.form.get("traveldays")
	travelers = request.form.get("travelers")
	start_date = request.form.get("tripstartdate")
	rental_cars = request.form.get("rentalcars")
	ground_transport = request.form.get("groundtransport")
	airfare = request.form.get("airfare")
	lodging = request.form.get("lodging")
	other = request.form.get("other")
	per_diem = request.form.get("perdium")
	registration = request.form.get("registration")
	city = request.args.get("city")
	state = request.args.get("state")
	country = request.args.get("country")

	if not meeting:
		return "meeting is null"
	elif not travelers:
		return "travelers is null"
	elif not meeting_days:
		return "meeting days is null"
	else:
		text = meeting + " " + travelers + " " + meeting_days
		#text = travelers + " " + meeting_days

		#return "conferenceattendees save request"
		return text


# CONFERENCE RATES

@app.route('/conferencerates/ajax/edit/<int:conferencerateid>')
@login_required
def edit_conferencerate(conferencerateid):
	conferencerates = ConferenceRates.get_many(joins = [], filters = [ConferenceRates.conferencerateid == conferencerateid], orders = [])
	return render_template('conference-rate-edit-ajax.json', conferencerates = conferencerates)

@app.route('/conferencerates/ajax/list/<int:conferenceid>')
@login_required
def load_conferencerates(conferenceid):
	conferencerates = ConferenceRates.get_many(joins = [],
											   filters = [ConferenceRates.conferenceid == conferenceid],
											   orders = [ConferenceRates.effectivedate.desc()])
	return render_template('conference-rate-list-ajax.json', conferencerates = conferencerates)


# EXPENSES

@app.route('/expenses/ajax/delete/<int:expenseid>&<int:proposalid>')
@login_required
def delete_expense(expenseid, proposalid):
	expense = Expenses.get_one(filters = [Expenses.expenseid == expenseid,
										  Expenses.proposalid == proposalid])

	if not expense:
		return "null"

	text = "expense: " + expense.description + " amount: " + currencyformat(expense.amount) + " fiscal year: " + fyformat(expense.fiscalyear)
	return text

@app.route('/expenses/ajax/edit/<int:expenseid>')
@login_required
def edit_expense(expenseid):
	expense = Expenses.get_one(filters = [Expenses.expenseid == expenseid])
	expensetypes = ExpenseTypes.get_all(orders = [ExpenseTypes.description])
	return render_template('expense-edit.html', expense = expense,
												expensetypes = expensetypes,
											 	dd_fiscalyears = fiscal_years(),
												dd_startdates = start_dates())

@app.route('/expenses/ajax/list/<int:proposalid>')
@login_required
def load_expenses(proposalid):
	expenses = Expenses.get_many(filters = [Expenses.proposalid == proposalid])
	return render_template('expense-list-ajax.json', expenses = expenses)


# EXPENSE TYPES

@app.route('/expensetypes')
@login_required
def expensetypes():
	return render_template('expensetypes.html')

@app.route('/expensetypes/ajax/edit/<int:expensetypeid>')
@login_required
def edit_expensetype(expensetypeid):
	expensetype = ExpenseTypes.get_one(filters = [ExpenseTypes.expensetypeid == expensetypeid])
	return render_template('expensetype-edit.html', expensetype = expensetype)

@app.route('/expensetypes/ajax/list')
@login_required
def load_expensetypes():
	expensetypes = ExpenseTypes.get_many(joins = [], filters = [], orders = [])
	return render_template('expensetypes-list-ajax.json', expensetypes = expensetypes)

@app.route('/expensetypes/save/<int:expensetypeid>')
@login_required
def save_expensetype(expensetypeid):
	expensetype = ExpenseTypes.get_one(filters = [ExpenseTypes.expensetypeid == expensetypeid])



# FBMSACCOUNTS

@app.route('/fbmsaccounts/ajax/delete/<int:fbmsid>&<int:proposalid>')
@login_required
def delete_fbmsaccount(fbmsid, proposalid):
	account = FBMSAccounts.get_one(filters = [FBMSAccounts.fbmsid == fbmsid,
											  FBMSAccounts.proposalid == proposalid])

	if not account:
		return "null"

	text = "account number: " + account.accountno
	return text

@app.route('/fbmsaccounts/ajax/edit/<int:fbmsid>')
@login_required
def edit_fbmsaccount(fbmsid):
	fbmsaccount = FBMSAccounts.get_one(filters = [FBMSAccounts.fbmsid == fbmsid])
	return render_template('fbms-edit.html', fbmsaccount = fbmsaccount)

@app.route('/fbmsaccounts/ajax/list/<int:proposalid>')
@login_required
def load_fbmsaccounts(proposalid):
	fbmsaccounts = FBMSAccounts.get_many(filters = [FBMSAccounts.proposalid == proposalid])
	return render_template('fbms-list-ajax.json', fbmsaccounts = fbmsaccounts)

@app.route('/fbmsaccounts/ajax/save/<int:fbmsid>', methods = ['GET', 'POST'])
@login_required
def save_fbmsaccounts(fbmsid):
	account = request.form.get('accountno')

	text = "" + account

	return text


# FUNDING

@app.route('/funding/ajax/delete/<int:fundingid>&<int:proposalid>')
@login_required
def delete_funding(fundingid, proposalid):
	# need to figure out how to remove items from the database with sqlalchemy

	# requirements:
		# update any fundings using the value that's being deleted to a default
		# will the whole table need to be looked through and changed?
			# could it be filtered by the name of the funding program?

	to_be_deleted = Funding.get_one(filters = [Funding.fundingid == fundingid,
											   Funding.proposalid == proposalid])

	if not to_be_deleted:
		return "null"

	text = "fiscalyear: " + fyformat(to_be_deleted.fiscalyear) + " newfunding: " + currencyformat(to_be_deleted.newfunding) + " carryover: " + currencyformat(to_be_deleted.carryover)
	print(text)

	# return message for the div
	return text

@app.route('/funding/ajax/edit/<int:fundingid>')
@login_required
def edit_funding(fundingid = None):
	funding = []
	if fundingid:
		funding = Funding.get_one(filters = [Funding.fundingid == fundingid])
	return render_template('funding-edit.html', funding = funding,
	 						dd_fiscalyears = fiscal_years(),
							dd_startdates = start_dates())

@app.route('/funding/ajax/list/<int:proposalid>')
@login_required
def load_funding(proposalid):
	funding = Funding.get_many(filters = [Funding.proposalid == proposalid])
	return render_template('funding-list-ajax.json', funding = funding)

@app.route('/funding/ajax/save/<int:fundingid>', methods = ['GET','POST'])
@login_required
def save_funding(fundingid):
	# update if already existing
	# make a new one if it is a new funding program

	if fundingid == 0:
		print("new funding")
	else:
		print("existing funding")

	#funding_proposalid = request.form.get('proposalid')
	#funding_fundingid = request.form.get('fundingid')
	funding_fiscalyear = request.form.get('fiscalyear')
	funding_newfunding = request.form.get('newfunding')
	funding_carryover = request.form.get("carryover")

	text = funding_fiscalyear + " " + funding_newfunding + " " + funding_carryover

	# return the message for the div
	return text


# OVERHEAD

@app.route('/overhead')
@login_required
def overhead():
	return render_template('overheads.html')

@app.route('/overhead/ajax/delete/<int:overheadid>&<int:proposalid>')
@login_required
def delete_overhead(overheadid, proposalid):
	# use the get arguments methods to get the elements in the url
	# return a message saying that this specific overhead was deleted?
	# make sure all parameters have been filled out for this delete, make sure
	# not to try to delete something that doesn't exist
		# might be how a whole table got deleted before

	overhead = OverheadRates.get_one(filters = [OverheadRates.overheadid == overheadid,
												OverheadRates.proposalid == proposalid])

	#overhead = OverheadRates.get_one(filters = [OverheadRates.overheadid == overheadid])

	if not overhead:
		return "null"

	text = "description: " + overhead.description
	return text

@app.route('/overhead/ajax/edit/<int:overheadid>')
@login_required
def edit_overhead(overheadid):
	overheadrate = OverheadRates.get_one([OverheadRates.overheadid == overheadid])
	return render_template('overhead-edit.html', overheadrate = overheadrate,
												 dd_fiscalyears = fiscal_years(),
												 dd_startdates = start_dates())

@app.route('/overhead/ajax/list')
@login_required
def load_overhead_list():
	overheadrates = OverheadRates.get_many(filters = [OverheadRates.proposalid == None])
	return render_template('overhead-list-ajax.json', overheadrates = overheadrates)

@app.route('/overhead/ajax/list/<int:proposalid>')
@login_required
def load_overhead(proposalid):
	overheadrates = OverheadRates.get_many(filters = [OverheadRates.proposalid == proposalid])
	if not overheadrates:
		overheadrates = OverheadRates.get_many(filters = [OverheadRates.proposalid == None])
	return render_template('overhead-list-ajax.json', overheadrates = overheadrates)

@app.route('/overhead/ajax/save/<int:overheadid>', methods = ['GET', 'POST'])
@login_required
def save_overhead(overheadid):
	overhead_rate = request.form.get("rate")
	description = request.form.get("description")
	effective_date = request.form.get("effectivedate")

	text = overhead_rate + " " + description + " " + effective_date

	return text


# PEOPLE

@app.route('/people')
@login_required
def people():
	return render_template('people.html')

@app.route('/people/ajax/dropdown')
@login_required
def people_dropdown():
	filters = []
	if request.args.get('peopleid'):
		filters.append(People.peopleid == request.args.get('peopleid'))
	people = People.get_many(joins = [Salaries], filters = filters, orders = [])
	return render_template('people-dropdown-list-ajax.json', people = people)


@app.route('/people/ajax/edit/<int:peopleid>')
@login_required
def edit_person(peopleid):
	person = People.get_one(filters = [People.peopleid == peopleid])
	return render_template('people-edit.html', person = person,
											   dd_fiscalyears = fiscal_years(),
											   dd_startdates = start_dates())

@app.route('/people/ajax/list')
@login_required
def load_people():
	people = People.get_many(joins = [Salaries], filters = [], orders = [])
	return render_template('people-list-ajax.json', people = people)

@app.route('/people/ajax/task/<int:peopleid>')
@login_required
def load_staffing(peopleid):
	staffing = Staffing.get_many(joins = [Tasks, People, Proposals],
										  filters = [Staffing.peopleid == peopleid],
										  orders = [])
	return render_template('people-task-list-ajax.json', staffing = staffing)


# PROGRAMS

@app.route('/programs')
@login_required
def programs():
	return render_template('programs.html')

@app.route('/programs/ajax/edit/<int:programid>')
@login_required
def edit_program(programid):
	program = FundingPrograms.get_one(filters = [FundingPrograms.programid == programid])
	return render_template('programs-edit.html', program = program,
												 dd_fiscalyears = fiscal_years(),
												 dd_startdates = start_dates())

@app.route('/programs/ajax/list')
@login_required
def load_programs():
	programs = FundingPrograms.get_many(joins = [], filters = [], orders = [])
	return render_template('programs-list-ajax.json', programs = programs)


# PROPOSALS

@app.route('/proposals')
@login_required
def proposals():
	return render_template('proposals.html')

@app.route('/proposals/ajax/edit/<int:proposalid>')
@app.route('/proposals/view/<int:proposalid>')
@login_required
def view_proposal(proposalid):
	params = {'proposal': Proposals.get_one(filters = [Proposals.proposalid == proposalid]),
			  'people': People.get_all(orders = [People.name]),
			  'programs': FundingPrograms.get_all(orders = [FundingPrograms.programname]),
			  'statuses': Statuses.get_all(orders = [Statuses.statusname]),
			  'dd_fiscalyears': fiscal_years(),
			  'dd_startdates': start_dates()}
	if 'edit' in request.url_rule.rule:
		return render_template('proposal-edit.html', **params)
	else:
		return render_template('proposal-view.html', **params)

@app.route('/proposals/ajax/list')
@login_required
def load_proposals():
	proposals = Proposals.get_all()
	return render_template('proposal-list-ajax.json', proposals = proposals)


@app.route('/proposal-basis/<int:proposalid>')
@login_required
def proposal_basis(proposalid):
	return render_template('proposal-basis.html')

@app.route('/proposal-budget/<int:proposalid>')
@login_required
def proposal_budget_details(proposalid):
	return render_template('proposal-budget-details.html')

@app.route('/proposal-nspires/<int:proposalid>')
@login_required
def proposal_nspires(proposalid):
	return render_template('proposal-nspires.html')

@app.route('/proposal-roses/<int:proposalid>')
@login_required
def proposal_redacted(proposalid):
	return render_template('proposal-roses.html')


# REPORTS

@app.route('/reports')
@login_required
def reports():
	return render_template('reports.html')


# SALARIES

@app.route('/salaries/ajax/edit/<int:salaryid>')
@login_required
def edit_salary(salaryid):
	salaries = Salaries.get_many(filters = [Salaries.salaryid == salaryid])
	return render_template('salary-edit-ajax.json', salaries = salaries)

@app.route('/salaries/ajax/list/<int:peopleid>')
@login_required
def load_salaries(peopleid):
	salaries = Salaries.get_many(filters = [Salaries.peopleid == peopleid])
	return render_template('salary-list-ajax.json', salaries = salaries)

# TASKS

@app.route('/tasks/ajax/dropdown')
@login_required
def task_dropdown():
	filters = []
	if request.args.get('proposalid'):
		filters.append(Tasks.proposalid == request.args.get('proposalid'))
	tasks = Tasks.get_many(joins = [], filters = filters, orders = [])
	return render_template('tasks-dropdown-ajax.json', tasks = tasks)

@app.route('/tasks/ajax/edit/<int:taskid>')
@login_required
def edit_task(taskid):
	task = Tasks.get_one(filters = [Tasks.taskid == taskid])
	return render_template('task-edit.html', task = task)

@app.route('/tasks/ajax/list/<int:proposalid>')
@login_required
def load_tasks(proposalid):
	tasks = Tasks.get_many(filters = [Tasks.proposalid == proposalid])
	return render_template('tasks-list-ajax.json', tasks = tasks)


if __name__ == "__main__":
	app.run(host = '0.0.0.0', port = 5000)
