from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Sequence, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import REAL

db = SQLAlchemy()

class People(db.Model):
  __tablename__ = 'people'

  peopleid = Column(Integer, Sequence('people_peopleid_seq'), primary_key=True)
  name     = Column(String(128))
  username = Column(String(32))
  admin    = Column(Boolean)

  def __repr__(self):
    return "<People(name='%s', username='%s')>" % (self.name, self.username)
 
class Salaries(db.Model):
  __tablename__ = 'salaries'

  salaryid      = Column (Integer, Sequence('salaries_salaryid_seq'), primary_key=True)
  peopleid      = Column (Integer, ForeignKey("people.peopleid"), nullable=False)
  effectivedate = Column (DateTime)
  payplan       = Column (String)
  title         = Column (String)
  appttype      = Column (String)
  authhours     = Column (Float)
  estsalary     = Column (Float)
  estbenefits   = Column (Float)
  leavecategory = Column (Float)
  laf           = Column (Float)

  def __repr__(self):
    return "<Salaries(peopleid='%d', payplan='%s', title='%s')>" % (self.peopleid, self.payplan, self.title)

class FundingPrograms(db.Model):
  __tablename__ = 'fundingprograms'

  programid   = Column (Integer, Sequence('fundingprograms_programid_seq'), primary_key=True)
  programname = Column (String)
  agency      = Column (String)
  pocname     = Column (String)
  procemail   = Column (String)
  startdate   = Column (DateTime)
  enddate     = Column (DateTime)

  def __repr__(self):
    return "<Funding Program(name='%s', agency='%s')>" % (self.programname, self.agency)

class Proposals(db.Model):
  __tablename__ = 'proposals'

  proposalid      = Column (Integer, Sequence('proposals_proposalid_seq'), primary_key=True)
  peopleid        = Column (Integer, ForeignKey("people.peopleid"), nullable=False)
  programid       = Column (Integer, ForeignKey("fundingprograms.programid"), nullable=False)
  projectname     = Column (String)
  proposalnumber  = Column (String)
  awardnumber     = Column (String)
  perfperiodstart = Column (DateTime)
  perfperiodend   = Column (DateTime)

  def __repr__(self):
    return "<Proposals(project='%s', proposalnumber='%s', awardnumber='%s')>" % (self.projectname, self.proposalnumber, self.awardnumber)

class FBMSAccounts(db.Model):
  __tablename__ = 'fbmsaccounts'

  fbmsid     = Column (Integer, Sequence('fbmsaccounts_fbmsid_seq'), primary_key=True)
  proposalid = Column (Integer, ForeignKey("proposals.proposalid"), nullable=False)
  accountno  = Column (String)

  def __repr__(self):
    return "<FBMS Account(accountno='%s')>" % (self.accountno)

class Conferences(db.Model):
  __tablename__ = 'conferences'

  conferenceid     = Column(Integer, Sequence('conferences_conferenceid_seq'), primary_key=True)
  meeting          = Column(String(256))
  conferencerates  = relationship('ConferenceRates')

  def __repr__(self):
    return "<Conference(meeting='%s', location='%s')>" % (self.meeting, self.location)

class ConferenceRates(db.Model):
  __tablename__ = 'conferencerates'

  conferencerateid = Column(Integer, Sequence('conferencerates_conferencerateid_seq'), primary_key=True)
  conferenceid     = Column(Integer, ForeignKey("conferences.conferenceid"), nullable=False)
  effectivedate    = Column(DateTime(timezone=False))
  perdiem          = Column(REAL)
  registration     = Column(REAL)
  groundtransport  = Column(REAL)
  airfare          = Column(REAL)
  city             = Column(String(120))
  state            = Column(String(2))
  country          = Column(String(40))
  lodging          = Column(REAL)
  conference       = relationship('Conferences')

  def __repr__(self):
    return "<ConferenceRates(perdiem='%d', registration='%s')>" % (self.perdiem, self.registration)

class ConferenceAttendee(db.Model):
  __tablename__ = 'conferenceattendee'

  conferenceattendeeid = Column (Integer, Sequence('conferenceattendee_conferenceattendeeid_seq'), primary_key=True)
  conferenceid         = Column (Integer, ForeignKey("conferences.conferenceid"), nullable=False)
  proposalid           = Column (Integer, ForeignKey("proposals.proposalid"), nullable=False)
  peopleid             = Column (Integer, ForeignKey("people.peopleid"), nullable=False)
  meetindays           = Column (Integer)
  traveldays           = Column (Integer)

  def __repr__(self):
    return "<ConferenceAttendee(meetingdays='%d', traveldays='%d')>" % (self.meetingdays, self.traveldays)

class Tasks(db.Model):
  __tablename__ = 'tasks'

  taskid     = Column (Integer, Sequence('tasks_taskid_seq'), primary_key=True)
  proposalid = Column (Integer, ForeignKey("proposals.proposalid"), nullable=False)
  taskname   = Column (String)

  def __repr__(self):
    return "<Tasks(taskname='%s')>" % (self.taskname)

class Staffing(db.Model):
  __tablename__ = 'staffing'

  staffingid = Column (Integer, Sequence('staffing_staffingid_seq'), primary_key=True)
  peopleid   = Column (Integer, ForeignKey("people.peopleid"), nullable=False)
  fiscalyear = Column (String)
  q1hours    = Column (Float)
  q2hours    = Column (Float)
  q3hours    = Column (Float)
  q4hours    = Column (Float)
  flexhours  = Column (Float)

  def __repr__(self):
    return "<Staffing(FY='%s', q1='%d', q2='%d', q3='%d', q4='%d', flex='%d')>" % (self.fiscalyear, self.q1hours, self.q2hours,
    self.q3hours, self.q4hours, self.flexhours)

class ExpenseTypes(db.Model):
  __tablename__ = 'expensetypes'

  expensetypeid = Column (Integer, Sequence('expensetypes_expensetypeid_seq'), primary_key=True)
  description   = Column (String)

  def __repr__(self):
    return "<ExpenseTypes(description='%s')>" % (self.description)

class Expenses(db.Model):
  __tablename__ = 'expenses'

  expenseid = Column (Integer, Sequence('expenses_expenseid_seq'), primary_key=True)
  proposalid = Column (Integer, ForeignKey("proposals.proposalid"), nullable=False)
  expensetypeid = Column (Integer, ForeignKey("expensetypes.expensetypeid"), nullable=False)
  description = Column (String)
  amount = Column (Float)
  fiscalyear = Column (String)

  def __repr__(self):
    return "<Expenses(description='%s')>" % (self.description)