import os
import secrets
from PIL import Image
from flask import request, render_template, url_for, flash, redirect
from SIMS_Portal import app, db, bcrypt
from SIMS_Portal.models import User, Assignment, Emergency, NationalSociety, Portfolio, EmergencyType
from SIMS_Portal.forms import RegistrationForm, LoginForm, UpdateAccountForm, NewAssignmentForm, NewEmergencyForm, PortfolioUploadForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

@app.route('/') 
def index(): 
	return render_template('index.html')

@app.route('/members')
def members():
	members = db.engine.execute("SELECT user.id AS user_id, user.ns_id AS user_ns_id, user.firstname, user.lastname, nationalsociety.ns_go_id, user.image_file, user.job_title, nationalsociety.ns_name FROM user  JOIN nationalsociety ON nationalsociety.ns_go_id = user.ns_id WHERE status = 'Active'")

	return render_template('members.html', members=members)

@app.route('/dashboard')
@login_required
def dashboard():
	todays_date = datetime.today()
	
	count_active_assignments = db.engine.execute("SELECT COUNT(role) as AssignmentCount FROM assignment WHERE end_date > :todays_date", {'todays_date': todays_date}).first()
	active_assignments = db.engine.execute("SELECT * FROM assignment JOIN user ON user.id = assignment.user_id JOIN emergency ON emergency.id = assignment.emergency_id WHERE end_date > :todays_date", {'todays_date': todays_date})
	
	return render_template('dashboard.html', active_assignments=active_assignments, count_active_assignments=count_active_assignments)

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	form = RegistrationForm()
	if request.method == 'GET':
		return render_template('register.html', title='Register for SIMS', form=form)
	else:
		if form.validate_on_submit():
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			user = User(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)
			db.session.add(user)
			print(user)
			db.session.commit()
			return redirect(url_for('login'))
		# else:
		# 	flash('There are errors in your registration details. Please correct them.', 'danger')
		# 	return redirect('/register')
		return render_template('register.html', title='Register for SIMS', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			# if request.method == 'POST':
			# 	flash('You have been logged in.', 'success')
			return redirect(next_page) if next_page else redirect(url_for('dashboard'))
		else:
			flash('Login failed. Please check email and password', 'danger')
	return render_template('login.html', title='Log into SIMS', form=form)

@app.route('/logout')
def logout():
	logout_user()
	flash("You have been logged out.", "success")
	return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
	user_info = User.query.filter(User.id==current_user.id).first()
	try:
		ns_association = db.session.query(User, NationalSociety).join(NationalSociety, NationalSociety.ns_go_id == User.ns_id).filter(User.id==current_user.id).with_entities(NationalSociety.ns_name).first()[0]	
	except:
		ns_association = 'None' 
	
	try:
		assignment_history = db.session.query(User, Assignment, Emergency).join(Assignment, Assignment.user_id==User.id).join(Emergency, Emergency.id==Assignment.emergency_id).filter(User.id==current_user.id).all()
	except:
		pass
	deployment_history_count = len(assignment_history)
	user_portfolio = db.session.query(User, Portfolio).join(Portfolio, Portfolio.creator_id==User.id).filter(User.id==current_user.id).all()
	print(user_portfolio)
	skills_list = db.engine.execute("SELECT * FROM user JOIN user_skill ON user.id = user_skill.user_id JOIN skill ON skill.id = user_skill.skill_id WHERE user.id=:current_user", {'current_user': current_user.id})
	profile_picture = url_for('static', filename='assets/img/avatars/' + current_user.image_file)
	return render_template('profile.html', title='Profile', profile_picture=profile_picture, ns_association=ns_association, user_info=user_info, assignment_history=assignment_history, deployment_history_count=deployment_history_count, user_portfolio=user_portfolio, skills_list=skills_list)
	
@app.route('/profile/view/<int:id>')
def view_profile(id):
	user_info = User.query.filter(User.id==id).first()
	try:
		ns_association = db.session.query(User, NationalSociety).join(NationalSociety, NationalSociety.ns_go_id == User.ns_id).filter(User.id==id).with_entities(NationalSociety.ns_name).first()[0]	
	except:
		ns_association = 'None' 
	try:
		assignment_history = db.session.query(User, Assignment, Emergency).join(Assignment, Assignment.user_id==User.id).join(Emergency, Emergency.id==Assignment.emergency_id).filter(User.id==id).all()
	except:
		pass
	deployment_history_count = len(assignment_history)

	user_portfolio = db.session.query(User, Portfolio).join(Portfolio, Portfolio.creator_id==id).filter(User.id==id).all()
	print(user_portfolio)
	
	profile_picture = url_for('static', filename='assets/img/avatars/' + user_info.image_file)
	return render_template('profile_member.html', title='Member Profile', profile_picture=profile_picture, ns_association=ns_association, user_info=user_info, assignment_history=assignment_history, deployment_history_count=deployment_history_count, user_portfolio=user_portfolio)

@app.route('/profile_edit', methods=['GET', 'POST'])
@login_required
def update_profile():
	form = UpdateAccountForm()
	try:
		ns_association = db.session.query(User, NationalSociety).join(NationalSociety, NationalSociety.ns_go_id == User.ns_id).filter(User.id==current_user.id).with_entities(NationalSociety.ns_name).first()[0]	
	except:
		ns_association = 'None'
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.firstname = form.firstname.data
		current_user.lastname = form.lastname.data
		current_user.email = form.email.data
		current_user.job_title = form.job_title.data
		try:
			current_user.ns_id = form.ns_id.data.ns_go_id
		except:
			pass
		current_user.bio = form.bio.data
		# current_user.birthday = form.birthday.data
		# current_user.molnix_id = form.molnix_id.data
		# current_user.roles = form.roles.data
		# current_user.languages = form.languages.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('profile'))
	elif request.method == 'GET':
		form.firstname.data = current_user.firstname
		form.lastname.data = current_user.lastname
		form.email.data = current_user.email
		form.job_title.data = current_user.job_title
		form.ns_id.data = current_user.ns_id
		# form.ns_id.data = current_user.ns_id
		form.bio.data = current_user.bio
		# form.birthday.data = current_user.birthday
		# form.molnix_id.data = current_user.molnix_id
		# form.roles.data = current_user.roles
		# form.languages.data = current_user.languages
	profile_picture = url_for('static', filename='assets/img/avatars/' + current_user.image_file)
	return render_template('profile_edit.html', title='Profile', profile_picture=profile_picture, form=form,ns_association=ns_association)
	
@app.route('/assignment/new', methods=['GET', 'POST'])
@login_required
def new_assignment():
	form = NewAssignmentForm()
	if form.validate_on_submit():
		assignment = Assignment(user_id=form.user_id.data.id, emergency_id=form.emergency_id.data.id,start_date=form.start_date.data, end_date=form.end_date.data, role=form.role.data, assignment_details=form.assignment_details.data, remote=form.remote.data)
		print(assignment)
		db.session.add(assignment)
		db.session.commit()
		flash('New assignment successfully created.', 'success')
		return redirect(url_for('dashboard'))
	return render_template('create_assignment.html', title='New Assignment', form=form)

@app.route('/emergency/<int:id>', methods=['GET', 'POST'])
@login_required
def view_emergency(id):
	emergency_info = db.session.query(Emergency).filter(Emergency.id == id).first()
	# emergency_type = db.session.query(Emergency, EmergencyType).join(EmergencyType, EmergencyType.emergency_type_go_id == Emergency.emergency_type_id).first()
	
	emergency_type = db.engine.execute("SELECT * FROM emergency JOIN emergencytype ON emergencytype.id = emergency.emergency_type_id WHERE emergency.id = :id", {'id': id})
	emergency_type_name = [row.emergency_type_name for row in emergency_type]
	return render_template('emergency.html', title='Emergency View', emergency_info=emergency_info, emergency_type=emergency_type, emergency_type_name=emergency_type_name[0])

@app.route('/emergency/new', methods=['GET', 'POST'])
@login_required
def new_emergency():
	form = NewEmergencyForm()
	if form.validate_on_submit():
		emergency = Emergency(emergency_name=form.emergency_name.data, emergency_location_id=form.emergency_location_id.data.ns_go_id, emergency_type_id=form.emergency_type_id.data.id, emergency_glide=form.emergency_glide.data, emergency_go_id=form.emergency_go_id.data, activation_details=form.activation_details.data)
		db.session.add(emergency)
		db.session.commit()
		flash('New emergency successfully created.', 'success')
		return redirect(url_for('dashboard'))
	return render_template('create_emergency.html', title='Create New Emergency', form=form)

@app.route('/portfolio/new', methods=['GET', 'POST'])
@login_required
def new_portfolio():
	form = PortfolioUploadForm()
	if form.validate_on_submit():
		if form.file.data:
			file = save_portfolio(form.file.data)
		product = Portfolio(
			final_file_location = file, title=form.title.data, creator_id=form.creator_id.data.id, description=form.description.data, type=form.type.data, emergency_id=form.emergency_id.data.id
		)
		db.session.add(product)
		db.session.commit()
		flash('New product successfully uploaded.', 'success')
		return redirect(url_for('profile'))
	return render_template('create_portfolio.html', title='Upload New SIMS Product', form=form)


def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	filename, file_ext = os.path.splitext(form_picture.filename)
	picture_filename = random_hex + file_ext
	picture_path = os.path.join(app.root_path, 'static/assets/img/avatars', picture_filename)
	
	output_size = (400, 400)
	resized_image = Image.open(form_picture)
	resized_image.thumbnail(output_size)
	resized_image.save(picture_path)
	
	return picture_filename

def save_portfolio(form_file):
	random_hex = secrets.token_hex(8)
	filename, file_ext = os.path.splitext(form_file.filename)
	file_filename = random_hex + file_ext
	file_path = os.path.join(app.root_path, 'static/assets/portfolio', file_filename)
	form_file.save(file_path)
	
	return file_filename


