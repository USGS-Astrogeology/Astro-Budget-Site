from flask import Flask, render_template, url_for, g, request, abort, session, jsonify
from flask_cas import CAS, login_required, login
from datetime import datetime, date
from database import (db, Conferences, ConferenceRates, ConferenceAttendee, Expenses, ExpenseTypes, FBMSAccounts,
					  Funding, FundingPrograms, OverheadRates, People, Proposals, Salaries, Staffing,
					  Statuses, Tasks)

# Jinja Filters ------------------>
def currencyformat(value):
	if not value:
		return '$0.00'
	return "${:,.2f}".format(value)

def dateformat(datestring):
	if not datestring:
		return datestring
	else:
		return datestring.strftime('%m/%d/%Y')

def floatformat(value):
	if not value:
		return '0.00'
	return "{:,.2f}".format(value)

def intformat(value):
	if not value:
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

def geteffective(list = [], cutoff_date = date.today()):
	effective_item = None
	if cutoff_date != date.today():
		cutoff_date = datetime.strptime(cutoff_date)

	for item in list:
		if item.effectivedate.date() <= cutoff_date:
			effective_item = item
	return effective_item

def currency_strstrp(string):
	banned_chars = ['$', ',']
	new_string = string
	for char in banned_chars:
		new_string = new_string.replace(char, '')
	if not new_string:
		new_string = '0'
	return float(new_string)
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

@app.route('/conferences/ajax/delete/<int:conferenceid>', methods = ['POST'])
@login_required
def delete_conference(conferenceid):
	conference = Conferences.get_one([Conferences.conferenceid == conferenceid])
	response = {'status': 'Error', 'description': 'Conference', 'action': 'found'}	
	return jsonify(delete_dbobject(conference, response))

@app.route('/conferences/ajax/edit/<int:conferenceid>')
@app.route('/conferences/ajax/new/<int:conferenceid>')
@login_required
def edit_conference(conferenceid):
	conference = Conferences.get_one([Conferences.conferenceid == conferenceid])
	params = {'conference': conference, 'dd_fiscalyears': fiscal_years(), 'dd_startdates': start_dates()}

	if 'edit' in request.url_rule.rule:
		return render_template('conference-edit.html', **params)
	else:
		return render_template('conference-new.html', **params)

@app.route('/conferences/ajax/list')
@login_required
def load_conferences():
	conferences = Conferences.get_many(joins = [], filters = [], orders = [])
	return render_template('conferences-list-ajax.json', conferences = conferences)

@app.route('/conferences/ajax/save/<int:conferenceid>', methods = ['POST'])
@login_required
def save_conference(conferenceid):
	conference = Conferences.get_one([Conferences.conferenceid == conferenceid])
	response = {'status': 'Error', 'description': 'Conference', 'action': 'read'}

	if not conference:		
		return save_conferencerate(0)
	try:
		response['action'] = 'updated'
		conference.meeting = request.form['meeting']
		db.session.commit()
	except:
		db.session.rollback()

	response['status'] = 'Success'
	return jsonify(response)


# CONFERENCE ATTENDEES

@app.route('/conferenceattendees/ajax/delete/<int:conferenceattendeeid>')
@login_required
def delete_conferenceattendee(conferenceattendeeid, proposalid):
	conferenceattendee = ConferenceAttendee.get_one(filters = [ConferenceAttendee.conferenceattendeeid == conferenceattendeeid])
	response = {'status': 'Error', 'description': 'Conference Attendee', 'action': 'found'}
	return jsonify(delete_dbobject(conferenceattendee, response))

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

@app.route('/conferenceattendees/ajax/save/<int:conferenceattendeeid>', methods = ['POST'])
@login_required
def save_conferenceattendee(conferenceattendeeid):
	conferenceattendee = ConferenceAttendee.get_one(filters = [ConferenceAttendee.conferenceattendeeid == conferenceattendeeid])
	response = {'status': 'Error', 'description': 'Conference Attendee', 'action': 'read', 'reload_path': ''}

	# Conference attributes
	meeting = request.form['meeting']

	conference = Conferences.get_one(filters = [Conferences.conferenceid == int(request.form['conferenceid'])])

	# ConferenceRate attributes

	proposal = request.form.get("proposalid")
	conferenceid = request.form.get("conferenceid")

	#meeting = request.form.get("meeting")
	meeting_days = request.form.get("meetingdays")
	travel_days = request.form.get("traveldays")
	travelers = request.form.get("travelers")
	start_date = request.form.get("tripstartdate")
	rental_cars = request.form.get("rentalcars")
	ground_transport = request.form.get("groundtransport")
	airfare = request.form.get("airfare")
	lodging = request.form.get("lodging")
	other = request.form.get("other")
	per_diem = request.form.get("perdiem")
	registration = request.form.get("registration")
	city = request.args.get("city")
	state = request.args.get("state")
	country = request.args.get("country")

	try:
		if not conference:
			print("new conference")
			conferenceattendee = ConferenceAttendee(proposalid = proposal,
											conferenceid = conferenceid,
											meetingdays = meeting_days,
											traveldays = travel_days,
											startdate = start_date,
											travelers = travelers,
											rentalcars = rental_cars)
			db.session.add(conference)
		else:
			print("existing conference")
			conference.meetingdays = meeting_days
			conference.traveldays = travel_days
			conference.startdate = start_date
			conference.travelers = travelers
			conference.rentalcars = rental_cars

		db.session.commit()
	except:
		db.session.rollback()
		return "Error: Conference Attendee not saved"

	return "Success: Conference Attendee saved"


# CONFERENCE RATES

@app.route('/conferencerates/ajax/delete/<int:conferencerateid>', methods = ['POST'])
@login_required
def delete_conferencerate(conferencerateid):
	conferencerate = ConferenceRates.get_one(filters = [ConferenceRates.conferencerateid == conferencerateid])
	response = {'status': 'Success', 'description': 'Conference Rate', 'action': 'found'}
	return jsonify(delete_dbobject(conferencerate, response))

@app.route('/conferencerates/ajax/edit/<int:conferencerateid>')
@login_required
def edit_conferencerate(conferencerateid):
	conferencerate = ConferenceRates.get_one(filters = [ConferenceRates.conferencerateid == conferencerateid])
	return render_template('conference-rate-edit.html', conferencerate = conferencerate,
														dd_fiscalyears = fiscal_years(),
														dd_startdates = start_dates())

@app.route('/conferencerates/ajax/get/<int:conferenceid>')
@login_required
def get_conferencerate_list(conferenceid):
	conferencerates = ConferenceRates.get_many(filters = [ConferenceRates.conferenceid == conferenceid],
											   orders = [ConferenceRates.effectivedate.asc()])
	most_recent = geteffective(conferencerates)
	result_list = [most_recent.perdiem, most_recent.lodging, most_recent.registration,
	most_recent.groundtransport, most_recent.airfare, most_recent.city, most_recent.state,
	most_recent.country]
	#info = serialize(conferencerates)
	#return str(most_recent)
	return str(result_list)
	#return info

@app.route('/conferencerates/ajax/list/<int:conferenceid>')
@login_required
def load_conferencerates(conferenceid):
	conferencerates = ConferenceRates.get_many(joins = [],
											   filters = [ConferenceRates.conferenceid == conferenceid],
											   orders = [ConferenceRates.effectivedate.desc()])
	return render_template('conference-rate-list-ajax.json', conferencerates = conferencerates)

@app.route('/conferencerates/ajax/save/<int:conferencerateid>', methods = ['POST'])
@login_required
def save_conferencerate(conferencerateid):
	conferencerate = ConferenceRates.get_one(filters = [ConferenceRates.conferencerateid == conferencerateid])
	conference = Conferences.get_one(filters = [Conferences.conferenceid == request.form['conferenceid']])
	response = {'status': 'Error', 'description': 'Conference Rate', 'action': 'read'}

	try:
		criteria = {'conferenceid': int(request.form['conferenceid']), 'perdiem': currency_strstrp(request.form['perdiem']),
					'registration': currency_strstrp(request.form['registration']), 'lodging': currency_strstrp(request.form['lodging']),
					'groundtransport': currency_strstrp(request.form['groundtransport']), 'airfare': currency_strstrp(request.form['airfare']),
					'city': request.form['city'], 'state': request.form['state'], 'country': request.form['country'],
					'effectivedate': datetime.strptime(request.form['effectivedate'], '%m/%d/%Y')}	
		response['description'] = 'Conference'
	except:
		return jsonify(response) # we could not read the inputs

	if not conferencerate:
		if not conference:
			try: 
				conference = Conferences(meeting = request.form['meeting'])
				db.session.add(conference)
				db.session.commit()
			except:
				db.session.rollback()
				return jsonify(response) # there was not a conference and we could not create one
		try:
			response.update({'description': 'Conference Rate', 'action': 'created'})
			criteria['conferenceid'] = conference.conferenceid
			conferencerate = ConferenceRates(**criteria)
			db.session.add(conferencerate)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.delete(conference)
			return jsonify(response) # we could not make a conferencerate	
	else:
		response.update({'description': 'Conference Rate', 'action': 'updated'})
		try:
			for key,value in criteria.items():
				setattr(conferencerate, key, value)
			db.session.commit()
		except:
			db.session.rollback() # we could not update an existing conferencerate

	response['status'] = 'Success'
	return jsonify(response)


# EXPENSES

@app.route('/expenses/ajax/delete/<int:expenseid>')
@login_required
def delete_expense(expenseid):
	expense = Expenses.get_one(filters = [Expenses.expenseid == expenseid])
	response = {'status': 'Error', 'description': 'Expense', 'action': 'found'}
	return jsonify(delete_dbobject(expense, response))

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

@app.route('/expenses/ajax/save/<int:expenseid>', methods = ['POST'])
@login_required
def save_expense(expenseid):
	expense = Expenses.get_one(filters = [Expenses.expenseid == expenseid])
	response = {'status': 'Error', 'description': 'Expense', 'action': 'read'}

	try:
		criteria = {'proposalid': int(request.form['proposalid']), 'expensetypeid': int(request.form['expensetypeid']),
					'description': request.form['description'], 'amount': currency_strstrp(request.form['amount']),
					'fiscalyear': datetime.strptime(request.form['fiscalyear'], '%m/%d/%Y')}
	except:
		return jsonify(response)

	return jsonify(save_dbobject(expense, Expenses, criteria, response))


# EXPENSE TYPES

@app.route('/expensetypes')
@login_required
def expensetypes():
	return render_template('expensetypes.html')

@app.route('/expensetypes/ajax/delete/<int:expensetypeid>', methods = ['POST'])	
@login_required	
def delete_expensetype(expensetypeid):	
	expensetype = ExpenseTypes.get_one(filters = [ExpenseTypes.expensetypeid == expensetypeid])	
	response = {'status': 'Error', 'description': 'Expense Category', 'action': 'found'}
	return jsonify(delete_dbobject(expensetype, response))

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

@app.route('/expensetypes/ajax/save/<int:expensetypeid>', methods = ['POST'])
@login_required
def save_expensetype(expensetypeid):
	expensetype = ExpenseTypes.get_one(filters = [ExpenseTypes.expensetypeid == expensetypeid])
	response = {'status': 'Error', 'description': 'Expense Category', 'action': 'read'}

	try:
		criteria = {'description': request.form['description']}
	except:
		return jsonify(response)

	return jsonify(save_dbobject(expensetype, ExpenseTypes, criteria, response))


# FBMSACCOUNTS

@app.route('/fbmsaccounts/ajax/delete/<int:fbmsid>')
@login_required
def delete_fbmsaccount(fbmsid):
	account = FBMSAccounts.get_one(filters = [FBMSAccounts.fbmsid == fbmsid])
	response = {'status': 'Error', 'description': 'FBMS Account', 'action': 'found'}
	return jsonify(delete_dbobject(account, response))

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

@app.route('/fbmsaccounts/ajax/save/<int:fbmsid>', methods = ['POST'])
@login_required
def save_fbmsaccounts(fbmsid):
	account = FBMSAccounts.get_one(filters = [FBMSAccounts.fbmsid == fbmsid])
	response = {'status': 'Error', 'description': 'FBMS Account', 'action': 'read'}

	try:
		criteria = {'proposalid': int(request.form['proposalid']), 'acccountno': request.form['accountno']}
	except:
		return jsonify(response)

	return jsonify(save_dbobject(account, FBMSAccounts, criteria, response))


# FUNDING

@app.route('/funding/ajax/delete/<int:fundingid>')
@login_required
def delete_funding(fundingid):
	funding = Funding.get_one(filters = [Funding.fundingid == fundingid])
	response = {'status': 'Error', 'description': 'Funding', 'action': 'found'}
	return jsonify(delete_dbobject(funding, response))

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

@app.route('/funding/ajax/save/<int:fundingid>', methods = ['POST'])
@login_required
def save_funding(fundingid):
	funding = Funding.get_one(filters = [Funding.fundingid == fundingid])
	response = {'status': 'Error', 'description': 'Funding', 'action': 'read'}

	try:
		criteria = {'proposalid': int(request.form['proposalid']), 'fiscalyear': datetime.strptime(request.form['fiscalyear'], '%m/%d/%Y'),
					'newfunding': currency_strstrp(request.form['newfunding']), 'carryover': currency_strstrp(request.form['carryover'])}
	except:
		return jsonify(response)

	return jsonify(save_dbobject(funding, Funding, criteria, response))


# OVERHEAD

@app.route('/overhead')
@login_required
def overhead():
	return render_template('overheads.html')

@app.route('/overhead/ajax/delete/<int:overheadid>')
@login_required
def delete_overhead(overheadid):
	overhead = OverheadRates.get_one(filters = [OverheadRates.overheadid == overheadid])
	response = {'status': 'Error', 'description': 'Overhead Rate', 'action': 'found'}
	return jsonify(delete_dbobject(overhead, response))

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

@app.route('/overhead/ajax/save/<int:overheadid>', methods = ['POST'])
@login_required
def save_overhead(overheadid):
	overhead = OverheadRates.get_one(filters = [OverheadRates.overheadid == overheadid])
	response = {'status': 'Error', 'description': 'Overhead Rate', 'action': 'read'}

	try:
		criteria = {'proposalid': int(request.form['proposalid']), 'rate': currency_strstrp(request.form['rate']),
					'description': request.form['description'], 'effectivedate': datetime.strptime(request.form['effectivedate'], '%m/%d/%Y')}
	except:
		return jsonify(response)

	return jsonify(save_dbobject(overhead, OverheadRates, criteria, response))

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
@app.route('/people/ajax/new/<int:peopleid>')
@login_required
def edit_person(peopleid):
	person = People.get_one(filters = [People.peopleid == peopleid])

	if 'edit' in request.url_rule.rule:
		return render_template('people-edit.html', person = person,
											   	   dd_fiscalyears = fiscal_years(),
												   dd_startdates = start_dates())
	else:
		return render_template('people-new.html')

@app.route('/people/ajax/list')
@login_required
def load_people():
	people = People.get_many(joins = [Salaries], filters = [], orders = [])
	return render_template('people-list-ajax.json', people = people)

@app.route('/people/ajax/save/<int:peopleid>', methods=['POST'])
@login_required
def save_person(peopleid):
	person = People.get_one(filters = [People.peopleid == peopleid])
	response = {'status': 'Error', 'description': 'Person', 'action': 'read'}

	try:
		criteria = {'name': request.form['name'], 'username': request.form['username'],
					'admin': True if request.form['admin'] == 'true' else False}
	except:
		return jsonify(response)

	return jsonify(save_dbobject(person, People, criteria, response))

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

@app.route('/programs/ajax/delete/<int:programid>', methods = ['POST'])	
@login_required	
def delete_program(programid):	
	program = FundingPrograms.get_one(filters = [FundingPrograms.programid == programid])	
	response = {'status': 'Success', 'description': 'funding program', 'action': 'found'}
	return jsonify(delete_dbobject(program, response))

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

@app.route('/programs/ajax/save/<int:programid>', methods = ['POST'])
@login_required
def save_program(programid):
	program = FundingPrograms.get_one(filters = [FundingPrograms.programid == programid])
	response = {'status': 'Error', 'description': 'Funding Program', 'action': 'read'}

	try:
		criteria = {'programname': request.form['programname'], 'agency': request.form['agency'],
					'pocname': request.form['pocname'], 'pocemail': request.form['pocemail'],
					'startdate': datetime.strptime(request.form['startdate'], '%m/%d/%Y'),
					'enddate': datetime.strptime(request.form['enddate'], '%m/%d/%Y')}	
	except:
		return jsonify(response)

	return jsonify(save_dbobject(program, FundingPrograms, criteria, response))



# PROPOSALS

@app.route('/proposals')
@login_required
def proposals():
	return render_template('proposals.html')

@app.route('/proposals/ajax/delete/<int:proposalid>')
@login_required
def delete_proposal(proposalid):
	proposal = Proposals.get_one(filters = [Proposals.proposalid == proposalid])
	response = {'status': 'Error', 'description': 'Proposal', 'action': 'found'}
	return jsonify(delete_dbobject(proposal, response))

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

@app.route('/proposals/ajax/save/<int:proposalid>', methods = ['POST'])
@login_required
def save_proposal(proposalid):
	proposal = Proposals.get_one(filters = [Proposals.proposalid == proposalid])
	response = {'status': 'Error', 'description': 'Proposal', 'action': 'found', 'reload_path': ''}

	try:
		criteria = {'projectname': request.form['projectname'], 'peopleid': request.form['peopleid'],
					'programid': request.form['programid'], 'status': request.form['status'],
					'proposalnumber': request.form['proposalnumber'], 'awardnumber': request.form['awardnumber'],
					'perfperiodstart': datetime.strptime(request.form['perfperiodstart'], '%m/%d/%Y'),
					'perfperiodend': datetime.strptime(request.form['perfperiodend', '%m/%d/%Y'])}
	except:
		return jsonify(response)

	return jsonify(save_dbobject(proposal, Proposals, criteria, response))

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


# ROW SETTING

@app.route('/row_setting/ajax/get')
@login_required
def get_saved_preference():
	user_preference = g.user.row_preference
	return str(user_preference)

@app.route('/row_setting/ajax/save/<row_preference>')
@login_required
def save_rows(row_preference):
	new_setting = row_preference

	try:
		g.user.row_preference = row_preference
		db.session.commit()
		return ("Success: New row preference saved")
	except:
		db.session.rollback()
		return ("Error: row preference not saved")

# this route is just used for testing purposes
@app.route('/row_setting/ajax/reset')
@login_required
def reset_row():
	try:
		g.user.row_preference = None
		db.session.commit()
		return("row preference reset")
	except:
		db.session.rollback()
		return("unsuccessful")


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


# Helpers ------------------>

def serialize(self):
	return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def save_dbobject(obj, dbclass, attributes, response):
	try:
		if not obj:
			response['action'] = 'created'
			obj = dbclass(**attributes)
			db.session.add(obj)
		else:
			response['action'] = 'updated'
			for key,value in attributes.items():
				setattr(obj, key, value)
		db.session.commit()
	except:
		db.session.rollback()
	
	response['status'] = 'Success'
	return response

def delete_dbobject(obj, response):
	if not obj:
		return response
	try:
		response['action'] = 'deleted'
		db.session.delete(obj)
		db.session.commit()
	except:
		db.session.rollback()
		
	response['status'] = 'Success'
	return response
	
# -------------------------->


if __name__ == "__main__":
	app.run(host = '0.0.0.0', port = 5000)
