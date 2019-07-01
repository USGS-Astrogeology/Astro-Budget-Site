from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Sequence, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import REAL, NUMERIC, SMALLINT, BIGINT

db = SQLAlchemy()

class People(db.Model):
  __tablename__ = 'people'

  peopleid       = Column(Integer, Sequence('people_peopleid_seq'), primary_key=True)
  name           = Column(String(128))
  username       = Column(String(32))
  admin          = Column(Boolean)
  row_preference = Column(Integer)
  salaries       = relationship('Salaries', backref='person')
  proposals      = relationship('Proposals', backref='person')
  staffing       = relationship('Staffing', backref='person')

  def __repr__(self):
    return "<People(name='%s', username='%s')>" % (self.name, self.username)

class Salaries(db.Model):
  __tablename__ = 'salaries'

  salaryid      = Column(Integer, Sequence('salaries_salaryid_seq'), primary_key=True)
  peopleid      = Column(Integer, ForeignKey("people.peopleid"), nullable=False)
  effectivedate = Column(DateTime(timezone=False))
  payplan       = Column(String(32))
  title         = Column(String(128))
  appttype      = Column(String(8))
  authhours     = Column(REAL)
  estsalary     = Column(NUMERIC(6,2))
  estbenefits   = Column(NUMERIC(6,2))
  leavecategory = Column(REAL)
  laf           = Column(REAL)

  def __repr__(self):
    return "<Salaries(peopleid='%d', payplan='%s', title='%s')>" % (self.peopleid, self.payplan, self.title)

class FundingPrograms(db.Model):
  __tablename__ = 'fundingprograms'

  programid   = Column(Integer, Sequence('fundingprograms_programid_seq'), primary_key=True)
  programname = Column(String(256))
  agency      = Column(String(32))
  pocname     = Column(String(128))
  procemail   = Column(String(128))
  startdate   = Column(DateTime(timezone=False))
  enddate     = Column(DateTime(timezone=False))
  proposals   = relationship('Proposals', backref='fundingprogram')

  def __repr__(self):
    return "<Funding Program(name='%s', agency='%s')>" % (self.programname, self.agency)

class Proposals(db.Model):
  __tablename__ = 'proposals'

  proposalid          = Column(Integer, Sequence('proposals_proposalid_seq'), primary_key=True)
  peopleid            = Column(Integer, ForeignKey("people.peopleid"), nullable=False)
  projectname         = Column(String(256))
  proposalnumber      = Column(String(128))
  awardnumber         = Column(String(128))
  programid           = Column(Integer, ForeignKey("fundingprograms.programid"), nullable=False)
  perfperiodstart     = Column(DateTime(timezone=False))
  perfperiodend       = Column(DateTime(timezone=False))
  status              = Column(Integer)
  fbmsaccounts        = relationship('FBMSAccounts', backref='proposal')
  conferenceattendees = relationship('ConferenceAttendee', backref='proposal')
  tasks               = relationship('Tasks', backref='proposal')
  expenses            = relationship('Expenses', backref='proposal')

  def __repr__(self):
    return "<Proposals(project='%s', proposalnumber='%s', awardnumber='%s')>" % (self.projectname, self.proposalnumber, self.awardnumber)

class FBMSAccounts(db.Model):
  __tablename__ = 'fbmsaccounts'

  fbmsid     = Column(Integer, Sequence('fbmsaccounts_fbmsid_seq'), primary_key=True)
  accountno  = Column(String(128))
  proposalid = Column(Integer, ForeignKey("proposals.proposalid"), nullable=False)

  def __repr__(self):
    return "<FBMS Account(accountno='%s')>" % (self.accountno)

class Conferences(db.Model):
  __tablename__ = 'conferences'

  conferenceid        = Column(Integer, Sequence('conferences_conferenceid_seq'), primary_key=True)
  meeting             = Column(String(256))
  conferencerates     = relationship('ConferenceRates', backref='conference')
  conferenceattendees = relationship('ConferenceAttendee', backref='conference')

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

  def __repr__(self):
    return "<ConferenceRates(perdiem='%d', registration='%s')>" % (self.perdiem, self.registration)

class ConferenceAttendee(db.Model):
  __tablename__ = 'conferenceattendee'

  conferenceattendeeid = Column(Integer, Sequence('conferenceattendee_conferenceattendeeid_seq'), primary_key=True)
  conferenceid         = Column(Integer, ForeignKey("conferences.conferenceid"), nullable=False)
  proposalid           = Column(Integer, ForeignKey("proposals.proposalid"), nullable=False)
  meetingdays          = Column(Integer)
  traveldays           = Column(Integer)
  startdate            = Column(DateTime(timezone=False))
  travelers            = Column(SMALLINT)
  rentalcars           = Column(SMALLINT)

  def __repr__(self):
    return "<ConferenceAttendee(meetingdays='%d', traveldays='%d')>" % (self.meetingdays, self.traveldays)

class Tasks(db.Model):
  __tablename__ = 'tasks'

  taskid     = Column(BIGINT, Sequence('tasks_taskid_seq'), primary_key=True)
  proposalid = Column(Integer, ForeignKey("proposals.proposalid"), nullable=False)
  taskname   = Column(String(1024))
  staffing   = relationship('Staffing', backref='task')

  def __repr__(self):
    return "<Tasks(taskname='%s')>" % (self.taskname)

class Staffing(db.Model):
  __tablename__ = 'staffing'

  staffingid = Column(BIGINT, Sequence('staffing_staffingid_seq'), primary_key=True)
  taskid     = Column(BIGINT, ForeignKey("tasks.taskid"))
  peopleid   = Column(Integer, ForeignKey("people.peopleid"), nullable=False)
  q1hours    = Column(REAL)
  q2hours    = Column(REAL)
  q3hours    = Column(REAL)
  q4hours    = Column(REAL)
  flexhours  = Column(REAL)
  fiscalyear = Column(DateTime(timezone=False))

  def __repr__(self):
    return "<Staffing(FY='%s', q1='%d', q2='%d', q3='%d', q4='%d', flex='%d')>" % (self.fiscalyear, self.q1hours, self.q2hours,
    self.q3hours, self.q4hours, self.flexhours)

class ExpenseTypes(db.Model):
  __tablename__ = 'expensetypes'

  expensetypeid = Column(Integer, Sequence('expensetypes_expensetypeid_seq'), primary_key=True)
  description   = Column(String(256))
  expenses      = relationship('Expenses', backref='expensetype')

  def __repr__(self):
    return "<ExpenseTypes(description='%s')>" % (self.description)

class Expenses(db.Model):
  __tablename__ = 'expenses'

  expenseid     = Column(BIGINT, Sequence('expenses_expenseid_seq'), primary_key=True)
  proposalid    = Column(Integer, ForeignKey("proposals.proposalid"), nullable=False)
  expensetypeid = Column(Integer, ForeignKey("expensetypes.expensetypeid"), nullable=False)
  description   = Column(String(256))
  amount        = Column(NUMERIC(6,2))
  fiscalyear    = Column(DateTime(timezone=False))

  def __repr__(self):
    return "<Expenses(description='%s')>" % (self.description)
