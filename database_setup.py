#configuration code
import sys
from sqlalchemy import Column,ForeignKey,Integer,String

#configuration and class code
from sqlalchemy.ext.declarative import declarative_base

#order to create foreign key relationship
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

#in order to create base class that our class code will inherit
#indicates classes are related to database 
Base=declarative_base()

class Doctor(Base):
	__tablename__='doctor'
	d_id=Column(Integer,primary_key=True)
	d_name=Column(String(300),nullable=False)
	d_education=Column(String(300),nullable=False)
	d_registerationno=Column(String(300),nullable=False)
	d_aadharno=Column(String(300),nullable=False)
	d_mobileno=Column(Integer,nullable=False)
	d_mailid=Column(String(300),nullable=False)
	d_address=Column(String(300),nullable=False)
	d_password=Column(String(300),nullable=False)

	@property
	def serialize(self):

		return {
			'Name': self.d_name,
			'Education': self.d_education,
			'Registerartionno':self.d_registerationno,
			'Mobileno':self.d_mobileno,
			'Mailid':self.d_mailid,
			'Address':self.d_address,		 	 	
	        }

class Patient(Base):
	__tablename__='patient'
	p_id=Column(Integer,primary_key=True)
	p_name=Column(String(300),nullable=False)
	p_birthdate=Column(String(300),nullable=False)
	p_sex=Column(String(10),nullable=False)
	p_weight=Column(Integer,nullable=False)
	p_bloodgroup=Column(String(10),nullable=False)
	p_aadharno=Column(String(10),nullable=False)	
	p_mobileno=Column(Integer,nullable=False)
	p_mailid=Column(String(300),nullable=False)
	p_address=Column(String(300),nullable=False)
	p_password=Column(String(300),nullable=False)

class Allergy(Base):
	__tablename__='allergy'
	a_id=Column(Integer,primary_key=True)
	allergy_name=Column(String(250),nullable=False)
	allergy_pid=Column(Integer,ForeignKey('patient.p_id'))
	patient=relationship(Patient)

class Scans(Base):
	__tablename__='scans'
	description=Column(String(1000),nullable=False)
	paths=Column(String(1000),primary_key=True)
	s_date=Column(String(1000))
	s_pid=Column(Integer,ForeignKey('patient.p_id'))
	visible=Column(Integer,default=1)	
	patient=relationship(Patient)

class Report(Base):
	__tablename__='report'
	r_id=Column(Integer,primary_key=True)
	date=Column(String(1000))
	patient_name=Column(String(300),nullable=False)
	symptoms=Column(String(1000),nullable=False)	
	diagnosis=Column(String(1000),nullable=False)
	treatment=Column(String(1000),nullable=False)
	doctor_name=Column(String(300),nullable=False)
	r_pid=Column(Integer,ForeignKey('patient.p_id'))
	r_did=Column(Integer,ForeignKey('doctor.d_id'))
	visible=Column(Integer,default=1)
	patient=relationship(Patient)
	doctor=relationship(Doctor)

#end of file
#it points to the database that we use 
engine=create_engine('sqlite:///hospital.db')

#adds the classes as new tables  in our database 
Base.metadata.create_all(engine)
