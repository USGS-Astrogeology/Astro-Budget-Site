from datetime import datetime, date

class BudgetFiscalYear:

    def __init__(self, year):
        self.name = "FY" + str(year).replace("20", "", 1)
        self.startdate = datetime(year-1, 10, 1)
        self.enddate = datetime(year, 10, 1)
        self.people = []
        self.conferenceattendees = []
        self.expenses = []
        self.funding = []
        self.overheadrate = 0

class ProposalBudget:

    def __init__(self, proposal):

        fylist = list(map(BudgetFiscalYear, proposal.years))
        fydict = {fy.name:fy for fy in fylist}

        for people in proposal.people:
            this_fy = fyformat(staffing.fiscalyear)
            if staffing.person not in fydict[this_fy].people:
                fydict[this_fy].people.append(staffing.person) 

        for funding in proposal.funding:
            this_fy = fyformat(funding.fiscalyear)
            if funding not in fydict[this_fy].funding:
                fydict[this_fy].funding.append(funding) 

        for conferenceattendee in proposal.conferenceattendees:
            this_fy = fyformat(conferenceattendee.startdate)
            if conferenceattendee not in fydict[this_fy].conferenceattendees: 
                fydict[this_fy].conferenceattendees.append(conferenceattendee) 

        for expense in proposal.expenses:
            this_fy = fyformat(expense.fiscalyear)
            if expense not in fydict[this_fy].expenses:
                fydict[this_fy].expenses.append(expense) 

        staffcosts = 
        taskhourlist = 
        tasktotalcost =

        # properties for ALL
        self.staffingcost = # running cost
        self.peopletotals = # += (salary + benefits)
        self.peoplehrtotals = # += taskhours



                
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
