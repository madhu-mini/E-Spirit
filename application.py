from flask import Flask
from flask import request,redirect,url_for,session,g,send_from_directory,jsonify
#from flask.ext.security import Security,SQLAlchemyUserDatastore,UserMixin,RoleMixin,login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Doctor, Patient, Allergy, Scans, Report
from flask import render_template
import os

engine = create_engine('sqlite:///hospital.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
Session = DBSession()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__)
app.config['DEBUG'] = True
app.secret_key=os.urandom(24)
#-------------------------------------------------------------------------------------------------------------------------------------------
#api creation
@app.route('/doctors_info/JSON')
def doctor_info_JSON():
    Doctors=Session.query(Doctor).all()	 
    return jsonify(Doctors=[i.serialize for i in Doctors])
#-------------------------------------------------------------------------------------------------------------------------------------------
#method that called before any request
@app.before_request
def before_request():
	g.doctor=None
	if 'doctor' in session:
		g.doctor=session['doctor']
	g.patient=None
	if 'patient' in session:
		g.patient=session['patient']
	g.doctorpatient=None
	if 'doctorpatient' in session:
		g.doctorpatient=session['doctorpatient']

#-------------------------------------------------------------------------------------------------------------------------------------------
#Registeration,login,logout sessions

#home page login method with session variables
@app.route('/',methods=['GET','POST'])
def index():
	if 'doctor' not in session and 'patient' not in session:
		if request.method == 'POST':
			session.pop('doctor',None)
			session.pop('patient',None)
			user=request.form['user']
			if user=="doctor" :
				email=request.form['email']
				password=request.form['password']
				doctor=Session.query(Doctor).filter_by(d_mailid=email).first()
				if doctor != None:
					if password == doctor.d_password:
						session['doctor']=email
						return redirect(url_for("doctor_profile",email=email))
					else:
						return render_template("home_page.html")
				else:
					return render_template("home_page.html")			
			else:
				email=request.form['email']
				password=request.form['password']
				patient=Session.query(Patient).filter_by(p_mailid=email).first()
				# returns none if no result is found
				if patient != None:
					if password == patient.p_password:
						session['patient']=email	
						return redirect(url_for("patient_profile",email=email))
					else:					
						return render_template("home_page.html")
				else:
					return render_template("home_page.html")			

		else:
			if 'doctor' not in session and 'patient' not in session:
					#tocheck 
					session.pop('doctor',None)
					session.pop('patient',None)
					return render_template("home_page.html")				
				#else:
				#	email=session.get('patient')
				#	return redirect(url_for("patient_profile",email=email))		
			else:			
				if 'doctor' in session:					
					email=session.get('doctor')
					redirect(url_for("doctor_profile",email=email))	
				else:
					email=session.get('patient')
					return redirect(url_for("patient_profile",email=email))		

	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))	
		else:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email))	
		
#for the logout activity
@app.route('/logout',methods=['GET','POST'])
def logout():
	if 'doctor' in session:
		session.pop('doctor',None)
	if 'patient' in session:
		session.pop('patient',None)	
	return redirect(url_for('index'))

#for the registeration of the doctor with session variable handled
@app.route('/post_doctor',methods=['GET','POST'])
def post_doctor():
	if 'doctor' not in session and 'patient' not in session:
		if request.method== 'POST':
			name=request.form['name']
			education=request.form['education']
			regno=request.form['registerationno']
			aadharno=request.form['aadharno'] 
#added aadhar number
			mobno=request.form['mobileno']
			email=request.form['email']
			add=request.form['address']
			pwd=request.form['password']
			doctor=Doctor(d_name=name,d_education=education,d_registerationno=regno,d_aadharno=aadharno,d_mobileno=mobno,d_mailid=email,d_address=add,d_password=pwd)
			Session.add(doctor)
			Session.commit()
			return redirect(url_for('index'))
		return render_template("post_doctor.html")
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))	
		else:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email))	

			
#for the registeration of the patient with the session variable handled
@app.route('/post_patient',methods=['GET','POST'])
def post_patient():
	if 'doctor' not in session and 'patient' not in session:
		if request.method== 'POST':
			name=request.form['name']
			dob=request.form['birthdate']
			sex=request.form['gender']
			weight=request.form['weight']
			bloodgroup=request.form['bloodgroup']
			aadharno=request.form['aadharno']
			mobileno=request.form['mobileno']
			email=request.form['email']
			add=request.form['address']
			pwd=request.form['password']
			patient=Patient(p_name=name,p_birthdate=dob,p_sex=sex,p_weight=weight,p_bloodgroup=bloodgroup,p_aadharno=aadharno,p_mobileno=mobileno,p_mailid=email,p_address=add,p_password=pwd)
			Session.add(patient)
			Session.commit()
			return redirect(url_for('index'))
		return render_template("post_patient.html")
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))	
		else:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email))	

#-------------------------------------------------------------------------------------------------------------------------------------------
#doctor_session

#for the doctor profile with session variable
@app.route('/doctor_profile/<email>',methods=['GET','POST'])
def doctor_profile(email):
	if 'doctor' in session and 'doctorpatient' not in session:
		if request.method== 'POST':   #request for the login of patient through doctor profile
			if 'doctorpatient' not in session:
				session.pop('doctorpatient',None)
				email=request.form['email']
				password=request.form['password']
				patient=Session.query(Patient).filter_by(p_mailid=email).first()
				# returns none if no result is found
				if patient != None:
					if password == patient.p_password:
						session['doctorpatient']=email
						email=session.get('doctor')
						dpemail=session.get('doctorpatient')
						return redirect(url_for("doctor_patient_profile",email=email,dpemail=dpemail))

					else:#wrong password
						email=session.get('doctor')
						return redirect(url_for("doctor_profile",email=email))
	
				else:#patient not found
					email=session.get('doctor')
					return redirect(url_for("doctor_profile",email=email))	
			
			else:#if already doctor logged in doctorpatient session
				email=session.get('doctor')
				dpemail=session.get('doctorpatient')
				return redirect(url_for("doctor_patient_profile",email=email,dpemail=dpemail))
					
		else:
			doctor=Session.query(Doctor).filter_by(d_mailid=email).first()
			return render_template('doctor_profile.html',doctor=doctor)
	else:
		if 'doctorpatient' in session:
				email=session.get('doctor')
				dpemail=session.get('doctorpatient')
				return redirect(url_for("doctor_patient_profile",email=email,dpemail=dpemail))
		if 'patient' in session:
			email=session.get('patient')
			patient=Session.query(Patient).filter_by(p_mailid=email).first()
			return redirect(url_for("patient_profile",email=email)) 
		else:
			return redirect(url_for('index'))


#to display doctor records with session variable
@app.route('/doctor_record_history/<string:email>',methods=['GET','POST'])
def doctor_record_history(email):
	if 'doctor' in session:
		if 'doctorpatient' in session:
			email=session.get('doctor')
			dpemail=session.get('doctorpatient')
			return redirect(url_for("doctor_patient_profile",email=email,dpemail=dpemail))
		else:
			doctor=Session.query(Doctor).filter_by(d_mailid=email).first()
			reports=Session.query(Report).filter_by(r_did=doctor.d_id).all()
			return render_template('doctor_record_history.html',reports=reports,doctor=doctor) 
	else:
		if 'patient' in session:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email)) 
		else:
			return redirect(url_for('index'))

#-------------------------------------------------------------------------------------------------------------------------------------------
#doctor_patient_session

#to display the patient deatils in doctor profile only to the doctor
@app.route('/doctor_patient_profile/<string:email>/<string:dpemail>',methods=['GET','POST'])
def doctor_patient_profile(email,dpemail):
	if 'doctor' in session :
		if 'doctorpatient' in session:
			patient=Session.query(Patient).filter_by(p_mailid=dpemail).first()
			doctor=Session.query(Doctor).filter_by(d_mailid=email).first()
			return render_template('doctor_patient_profile .html',patient=patient,doctor=doctor) 
		else:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
	else:
		if 'patient' in session:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email)) 
		else:
			return redirect(url_for('index'))


#for the logout activity
@app.route('/doctor_patient_logout',methods=['GET','POST'])
def doctor_patient_logout():
	if 'doctorpatient' in session:
		session.pop('doctorpatient',None)	
	email=session.get('doctor')
	return redirect(url_for("doctor_profile",email=email))


#for display and add allergy
@app.route('/doctor_patient_allergy/<string:email>',methods=['GET','POST'])
def doctor_patient_allergy(email):
	if 'doctorpatient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=session.get('doctorpatient')).first()
		doctor=Session.query(Doctor).filter_by(d_mailid=session.get('doctor')).first()
		allergys=Session.query(Allergy).filter_by(allergy_pid=patient.p_id).all()
		return render_template("doctor_patient_allergy.html",patient=patient,doctor=doctor,allergys=allergys)
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		elif 'patient'in session:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email)) 
			
		else:
			return redirect(url_for('index'))

#To add allergy with session variable
@app.route('/doctor_patient_add_allergy',methods=['GET','POST'])
def doctor_patient_add_allergy():
	if 'doctorpatient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=session.get('doctorpatient')).first()
		allergys=Session.query(Allergy).filter_by(allergy_pid=patient.p_id).all()
		if request.method== 'POST':
			allergy=Allergy(allergy_name=request.form['allergy'],patient=patient)
			Session.add(allergy)
			Session.commit()
			redirect(url_for("doctor_patient_allergy",email=patient.p_mailid))
		return redirect(url_for("doctor_patient_allergy",email=patient.p_mailid))
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		elif 'patient'in session:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email)) 
			
		else:
			return redirect(url_for('index'))


#for display and add reports
@app.route('/doctor_patient_report/<string:email>',methods=['GET','POST'])
def doctor_patient_report(email):
	if 'doctorpatient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=session.get('doctorpatient')).first()
		doctor=Session.query(Doctor).filter_by(d_mailid=session.get('doctor')).first()
		reports=Session.query(Report).filter_by(r_pid=patient.p_id,visible=1).all()
		return render_template("doctor_patient_report.html",patient=patient,doctor=doctor,reports=reports)
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		elif 'patient'in session:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email)) 
			
		else:
			return redirect(url_for('index'))

#to add the report
@app.route('/doctor_patient_add_report',methods=['GET','POST'])
def doctor_patient_add_report():
	if 'doctorpatient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=session.get('doctorpatient')).first()
		doctor=Session.query(Doctor).filter_by(d_mailid=session.get('doctor')).first()
		reports=Session.query(Report).filter_by(r_pid=patient.p_id,visible=1).all()
		if request.method== 'POST':
			report=Report(date=request.form['date'],patient_name=patient.p_name,symptoms=request.form['symptoms'],diagnosis=request.form['diagnosis'],treatment=request.form['treatment'],doctor_name=doctor.d_name,patient=patient,doctor=doctor)
			Session.add(report)
			Session.commit()
			redirect(url_for("doctor_patient_report",email=patient.p_mailid))
		return redirect(url_for("doctor_patient_report",email=patient.p_mailid))
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		elif 'patient'in session:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email)) 
			
		else:
			return redirect(url_for('index'))

#for display and add scans
@app.route('/doctor_patient_scan/<string:email>',methods=['GET','POST'])
def doctor_patient_scan(email):
	if 'doctorpatient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=session.get('doctorpatient')).first()
		doctor=Session.query(Doctor).filter_by(d_mailid=session.get('doctor')).first()
		scans = Session.query(Scans).filter_by(s_pid=patient.p_id,visible=1).all()
		return render_template("doctor_patient_scan.html",patient=patient,doctor=doctor,scans=scans)
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		elif 'patient'in session:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email)) 
			
		else:
			return redirect(url_for('index'))


#to add the scan
@app.route('/doctor_patient_add_scan',methods=['GET','POST'])
def doctor_patient_add_scan():
	if 'doctorpatient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=session.get('doctorpatient')).first()
		doctor=Session.query(Doctor).filter_by(d_mailid=session.get('doctor')).first()
		scans = Session.query(Scans).filter_by(s_pid=patient.p_id,visible=1).all()
		if request.method=='POST':
			target=os.path.join(APP_ROOT, 'images/')
			if not os.path.isdir(target):
				os.mkdir(target)
			for upload in request.files.getlist("file"):
				ukey= Session.query(Scans).count()
				ukey+=1
				filename=str(ukey)+"."+upload.filename
				destination="/".join([target, filename])
				upload.save(destination)
				newScan=Scans(description=request.form['description'],paths=filename,s_date=request.form['date'],patient=patient)
				Session.add(newScan)
				Session.commit()
			redirect(url_for("doctor_patient_scan",email=patient.p_mailid))
		return redirect(url_for("doctor_patient_scan",email=patient.p_mailid))
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		elif 'patient'in session:
			email=session.get('patient')
			return redirect(url_for("patient_profile",email=email)) 
			
		else:
			return redirect(url_for('index'))


#to get images
@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


#----------------------------------------------------------------------------------------------------------------------------------
#form here it is the code for patient record to be displayed when he himself get login

#for the patient profile with session variable	
@app.route('/patient_profile/<email>')
def patient_profile(email):
	if 'patient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=email).first()
		return render_template('patient_profile.html',patient=patient) 
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		else:
			return redirect(url_for('index'))
		

#To display patient Allergy in patient's profile with session variable
@app.route('/patient_profile_allergy/<string:email>',methods=['GET','POST'])
def patient_profile_allergy(email):
	if 'patient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=email).first()
		allergys=Session.query(Allergy).filter_by(allergy_pid=patient.p_id).all()
		return render_template("patient_profile_allergy.html",patient=patient,allergys=allergys)
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		else:
			return redirect(url_for('index'))


#To add allergy with session variable
@app.route('/patient_add_allergy',methods=['GET','POST'])
def patient_add_allergy():
	if 'patient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=request.form['email']).first()
		allergys=Session.query(Allergy).filter_by(allergy_pid=patient.p_id).all()
		if request.method== 'POST':
			allergy=Allergy(allergy_name=request.form['allergy'],patient=patient)
			Session.add(allergy)
			Session.commit()
			redirect(url_for("patient_profile_allergy",email=patient.p_mailid))
		return redirect(url_for("patient_profile_allergy",email=patient.p_mailid))
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		else:
			return redirect(url_for('index'))
	

#patient Reports to be displayed to patient with session variable
@app.route('/patient_profile_report/<string:email>',methods=['GET','POST'])
def patient_profile_report(email):
	if 'patient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=email).first()
		reports=Session.query(Report).filter_by(r_pid=patient.p_id).all()
		return render_template("patient_profile_report.html",patient=patient,reports=reports)
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		else:
			return redirect(url_for('index'))


#To change visibility of patient report with session variable
@app.route('/patient_change_visibility',methods=['GET','POST'])
def patient_change_visibility():
	if 'patient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=request.form['email']).first()
		report=Session.query(Report).filter_by(r_id=request.form['reportid']).first()
		if request.method== 'POST':
			if report.visible == 1:
				report.visible=0
			else:
				report.visible=1
			Session.add(report)
			Session.commit()
			redirect(url_for("patient_profile_report",email=patient.p_mailid))
		return redirect(url_for("patient_profile_report",email=patient.p_mailid))
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		else:
			return redirect(url_for('index'))

#patient Scans to be displayed to patient with session variable
@app.route('/patient_profile_scan/<string:email>',methods=['GET','POST'])
def patient_profile_scan(email):
	if 'patient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=email).first()
		scans = Session.query(Scans).filter_by(s_pid=patient.p_id).all()
		return render_template("patient_profile_scan.html",patient=patient,scans=scans)
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		else:
			return redirect(url_for('index'))


#To change visibility of patient scan with session variable
@app.route('/patient_change_scan_visibility',methods=['GET','POST'])
def patient_change_scan_visibility():
	if 'patient' in session:
		patient=Session.query(Patient).filter_by(p_mailid=request.form['email']).first()
		scans = Session.query(Scans).filter_by(paths=request.form['scanpaths']).first()
		if request.method== 'POST':
			if scans.visible == 1:
				scans.visible=0
			else:
				scans.visible=1
			Session.add(scans)
			Session.commit()
			redirect(url_for("patient_profile_scan",email=patient.p_mailid))
		return redirect(url_for("patient_profile_scan",email=patient.p_mailid))
	else:
		if 'doctor' in session:
			email=session.get('doctor')
			return redirect(url_for("doctor_profile",email=email))
		else:
			return redirect(url_for('index'))

#___________________________________________________________________________________________________________________________________________
#main method of the program
if __name__=="__main__":
	app.debug = True
	app.run(host = '0.0.0.0',port=5000)

#developed by madhuminiyar@gmail.com,padmajadhonddev15@gmail.com
