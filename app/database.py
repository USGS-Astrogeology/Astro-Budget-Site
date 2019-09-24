from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Sequence, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.dialects.postgresql import REAL, NUMERIC, SMALLINT, BIGINT

db = SQLAlchemy()

class Base(db.Model):
  __abstract__ = True

  @classmethod
  def get_one(cls, filters=[]):
      return cls.query.filter(db.and_(*filters)).first()

  @classmethod
  def get_many(cls, joins=[], filters=[], orders=[]):
      return cls.query.outerjoin(*joins)\
                      .filter(db.and_(*filters))\
                      .order_by(*orders).all()

  @classmethod
  def get_all(cls, orders=[]):
      return cls.query.order_by(*orders).all()


class DatedBase(Base):
  __abstract__ = True

  @classmethod
  def get_effective(cls, entries, fy):
    all_effective = []

    try:
      for entry in entries:
        if cls.to_fy(entry.effectivedate) == fy:
          all_effective.append(entry)
    except:
      return None

    return all_effective[-1]

  @classmethod
  def to_fy(cls, date):
    year_string = ''
    try:
      if date.month >= 10 and date.day >= 1:
        year_string = "FY" + str(date.year+1).replace("20", "", 1)
      else:
        year_string = "FY" + str(date.year).replace("20", "", 1)
    except:
      return ''
    return year_string


class People(DatedBase):
  __tablename__ = 'people'

  peopleid       = Column(Integer, Sequence('people_peopleid_seq'), primary_key=True)
  name           = Column(String(128))
  username       = Column(String(32))
  admin          = Column(Boolean)
  row_preference = Column(Integer)
  salaries       = relationship('Salaries', backref='person', order_by="asc(Salaries.effectivedate)")
  proposals      = relationship('Proposals', backref='person', cascade='all,delete')
  staffing       = relationship('Staffing', backref='person', cascade='all,delete')

  @hybrid_method
  def salary(self, fy):
    return self.get_effective(self.salaries, fy)

  def __repr__(self):
    return "<People(name='%s', username='%s')>" % (self.name, self.username)

class Salaries(DatedBase):
  __tablename__ = 'salaries'

  salaryid      = Column(Integer, Sequence('salaries_salaryid_seq'), primary_key=True)
  peopleid      = Column(Integer, ForeignKey("people.peopleid"), nullable=False)
  effectivedate = Column(DateTime(timezone=False))
  payplan       = Column(String(32))
  title         = Column(String(128))
  appttype      = Column(String(8))
  authhours     = Column(REAL)
  estsalary     = Column(REAL)
  estbenefits   = Column(REAL)
  leavecategory = Column(REAL)
  laf           = Column(REAL)

  def __repr__(self):
    return "<Salaries(peopleid='%d', payplan='%s', title='%s')>" % (self.peopleid, self.payplan, self.title)

class Funding(Base):
  __tablename__ = 'funding'

  fundingid  = Column(Integer, Sequence('funding_fundingid_seq'), primary_key=True)
  proposalid = Column(Integer, ForeignKey("proposals.proposalid"))
  fiscalyear = Column(DateTime(timezone=False))
  newfunding = Column(NUMERIC(6,2))
  carryover  = Column(NUMERIC(6,2))

  def __repr__(self):
      return "<Funding(newfunding='%d', carryover='%d')>" % (self.newfunding, self.carryover)

class FundingPrograms(Base):
  __tablename__ = 'fundingprograms'

  programid   = Column(Integer, Sequence('fundingprograms_programid_seq'), primary_key=True)
  programname = Column(String(256))
  agency      = Column(String(32))
  pocname     = Column(String(128))
  pocemail    = Column(String(128))
  startdate   = Column(DateTime(timezone=False))
  enddate     = Column(DateTime(timezone=False))
  proposals   = relationship('Proposals', backref='fundingprogram', cascade='all,delete')

  def __repr__(self):
    return "<Funding Program(name='%s', agency='%s')>" % (self.programname, self.agency)

class Proposals(Base):
  __tablename__ = 'proposals'

  proposalid          = Column(Integer, Sequence('proposals_proposalid_seq'), primary_key=True)
  peopleid            = Column(Integer, ForeignKey("people.peopleid"), nullable=False)
  projectname         = Column(String(256))
  proposalnumber      = Column(String(128))
  awardnumber         = Column(String(128))
  programid           = Column(Integer, ForeignKey("fundingprograms.programid"), nullable=False)
  perfperiodstart     = Column(DateTime(timezone=False))
  perfperiodend       = Column(DateTime(timezone=False))
  status              = Column(Integer, ForeignKey("statuses.status"))
  fbmsaccounts        = relationship('FBMSAccounts', backref='proposal', cascade="all,delete")
  conferenceattendees = relationship('ConferenceAttendee', backref='proposal', cascade="all,delete")
  tasks               = relationship('Tasks', backref='proposal', cascade="all,delete")
  expenses            = relationship('Expenses', backref='proposal', cascade="all,delete")
  funding             = relationship('Funding', backref='proposal', cascade="all,delete")
  overheadrates       = relationship('OverheadRates', backref='proposal', cascade="all,delete")
  modified            = Column(DateTime(timezone=False))

  @hybrid_property
  def years(self):
    startyear = self.perfperiodstart.year
    startyear = startyear if self.perfperiodstart.month < 10 and self.perfperiodstart.day < 1 else startyear + 1
    endyear = self.perfperiodend.year
    endyear = endyear if self.perfperiodstart.month < 10 and self.perfperiodstart.day < 1 else startyear + 1

    years = []
    currentyear = startyear
    while currentyear <= endyear:
        years.append(currentyear)
        currentyear += 1
    return years

  @hybrid_property
  def people(self):
    people = []
    for task in self.tasks:
      for staffing in tasks.staffing:
        if staffing.person not in people: people.append(staffing.person)
    return people

  def __repr__(self):
    return "<Proposals(project='%s', proposalnumber='%s', awardnumber='%s')>" % (self.projectname, self.proposalnumber, self.awardnumber)

class FBMSAccounts(Base):
  __tablename__ = 'fbmsaccounts'

  fbmsid     = Column(Integer, Sequence('fbmsaccounts_fbmsid_seq'), primary_key=True)
  accountno  = Column(String(128))
  proposalid = Column(Integer, ForeignKey("proposals.proposalid"), nullable=False)

  def __repr__(self):
    return "<FBMS Account(accountno='%s')>" % (self.accountno)

class Conferences(Base):
  __tablename__ = 'conferences'

  conferenceid        = Column(Integer, Sequence('conferences_conferenceid_seq'), primary_key=True)
  meeting             = Column(String(256))
  conferencerates     = relationship('ConferenceRates', backref='conference', order_by='asc(ConferenceRates.effectivedate)')
  conferenceattendees = relationship('ConferenceAttendee', backref='conference')

  def __repr__(self):
    return "<Conference(meeting='%s', location='%s')>" % (self.meeting, self.location)

class ConferenceRates(DatedBase):
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

class ConferenceAttendee(DatedBase):
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

class Tasks(Base):
  __tablename__ = 'tasks'

  taskid     = Column(BIGINT, Sequence('tasks_taskid_seq'), primary_key=True)
  proposalid = Column(Integer, ForeignKey("proposals.proposalid"), nullable=False)
  taskname   = Column(String(1024))
  staffing   = relationship('Staffing', backref='task')

  @hybrid_property
  def people(self):
    return {staffing.person for staffing in self.staffing}

  @hybrid_property
  def taskhours(self):
    return sum(staffing.taskhours for staffing in self.staffing)

  def __repr__(self):
    return "<Tasks(taskname='%s')>" % (self.taskname)

class Staffing(DatedBase):
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

  @hybrid_property
  def taskhours(self):
    return self.q1hours + self.q2hours + self.q3hours + self.q4hours + self.flexhours

  @hybrid_property
  def staffcosts(self):
    fy = self.to_fy(self.fiscalyear)
    salary = self.person.salary(fy)
    lafhours = round(self.taskhours * salary.laf, 4)
    return (salary.estsalary * lafhours) + (salary.estbenefits * lafhours)

  def __repr__(self):
    return "<Staffing(FY='%s', q1='%d', q2='%d', q3='%d', q4='%d', flex='%d')>" % (self.fiscalyear, self.q1hours, self.q2hours,
    self.q3hours, self.q4hours, self.flexhours)

class ExpenseTypes(Base):
  __tablename__ = 'expensetypes'

  expensetypeid = Column(Integer, Sequence('expensetypes_expensetypeid_seq'), primary_key=True)
  description   = Column(String(256))
  expenses      = relationship('Expenses', backref='expensetype')

  def __repr__(self):
    return "<ExpenseTypes(description='%s')>" % (self.description)

class Expenses(DatedBase):
  __tablename__ = 'expenses'

  expenseid     = Column(BIGINT, Sequence('expenses_expenseid_seq'), primary_key=True)
  proposalid    = Column(Integer, ForeignKey("proposals.proposalid"), nullable=False)
  expensetypeid = Column(Integer, ForeignKey("expensetypes.expensetypeid"), nullable=False)
  description   = Column(String(256))
  amount        = Column(NUMERIC(6,2))
  fiscalyear    = Column(DateTime(timezone=False))

  def __repr__(self):
    return "<Expenses(description='%s')>" % (self.description)

class OverheadRates(DatedBase):
    __tablename__='overheadrates'

    overheadid      = Column(Integer, Sequence('overheadrates_overheadid_seq'), primary_key=True)
    proposalid      = Column(Integer, ForeignKey("proposals.proposalid"))
    rate            = Column(REAL)
    description     = Column(String(80))
    effectivedate   = Column(DateTime(timezone=False))

    def __repr__(self):
        return "<OverheadRates(description='%s')>" % (self.description)

class Statuses(Base):
  __tablename__ = 'statuses'

  status = Column(Integer, primary_key = True)
  statusname = Column(String(16))
  proposals = relationship('Proposals', backref='proposalstatus')
