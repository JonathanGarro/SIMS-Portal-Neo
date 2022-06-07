from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint
from SIMS_Portal import db, bcrypt, mail
from SIMS_Portal.models import User, Assignment, Emergency, NationalSociety, Portfolio, EmergencyType, Skill, Language, user_skill, user_language, Badge, Alert
from SIMS_Portal.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from SIMS_Portal.users.utils import save_picture, send_reset_email
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message

users = Blueprint('users', __name__)

@users.route('/members')
def members():
	members = db.engine.execute("SELECT user.id AS user_id, user.ns_id AS user_ns_id, user.firstname, user.lastname, nationalsociety.ns_go_id, user.image_file, user.job_title, nationalsociety.ns_name FROM user  JOIN nationalsociety ON nationalsociety.ns_go_id = user.ns_id WHERE status = 'Active'")

	return render_template('members.html', members=members)

@users.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.dashboard'))
	form = RegistrationForm()
	if request.method == 'GET':
		return render_template('register.html', title='Register for SIMS', form=form)
	else:
		if form.validate_on_submit():
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			user = User(firstname=form.firstname.data, lastname=form.lastname.data, ns_id=form.ns_id.data.ns_go_id, email=form.email.data, password=hashed_password)
			db.session.add(user)
			db.session.commit()
			flash('Your account has been created.', 'success')
			return redirect(url_for('users.login'))
		# else:
		# 	flash('There are errors in your registration details. Please correct them.', 'danger')
		# 	return redirect('/register')
		return render_template('register.html', title='Register for SIMS', form=form)
	
@users.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.dashboard'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			# if request.method == 'POST':
			# 	flash('You have been logged in.', 'success')
			return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
		else:
			flash('Login failed. Please check email and password', 'danger')
	return render_template('login.html', title='Log into SIMS', form=form)

@users.route('/logout')
def logout():
	logout_user()
	flash("You have been logged out.", "success")
	return redirect(url_for('users.login'))

@users.route('/profile')
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
	skills_list = db.engine.execute("SELECT * FROM user JOIN user_skill ON user.id = user_skill.user_id JOIN skill ON skill.id = user_skill.skill_id WHERE user.id=:current_user", {'current_user': current_user.id})
	languages_list = db.engine.execute("SELECT * FROM user JOIN user_language ON user.id = user_language.user_id JOIN language ON language.id = user_language.language_id WHERE user.id=:current_user", {'current_user': current_user.id})
	profile_picture = url_for('static', filename='assets/img/avatars/' + current_user.image_file)
	return render_template('profile.html', title='Profile', profile_picture=profile_picture, ns_association=ns_association, user_info=user_info, assignment_history=assignment_history, deployment_history_count=deployment_history_count, user_portfolio=user_portfolio, skills_list=skills_list, languages_list=languages_list)
	
@users.route('/profile/view/<int:id>')
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
	skills_list = db.engine.execute("SELECT * FROM user JOIN user_skill ON user.id = user_skill.user_id JOIN skill ON skill.id = user_skill.skill_id WHERE user.id=:member_id", {'member_id': id})
	languages_list = db.engine.execute("SELECT * FROM user JOIN user_language ON user.id = user_language.user_id JOIN language ON language.id = user_language.language_id WHERE user.id=:member_id", {'member_id': id})
	profile_picture = url_for('static', filename='assets/img/avatars/' + user_info.image_file)
	return render_template('profile_member.html', title='Member Profile', profile_picture=profile_picture, ns_association=ns_association, user_info=user_info, assignment_history=assignment_history, deployment_history_count=deployment_history_count, user_portfolio=user_portfolio, skills_list=skills_list, languages_list=languages_list)

@users.route('/profile_edit', methods=['GET', 'POST'])
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
		current_user.twitter = form.twitter.data
		current_user.github = form.github.data
		for skill in form.skills.data:
			current_user.skills.append(Skill.query.filter(Skill.name==skill).one())
		# current_user.roles = form.roles.data
		for language in form.languages.data:
			current_user.languages.append(Language.query.filter(Language.name==language).one())
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('users.profile'))
	elif request.method == 'GET':
		form.firstname.data = current_user.firstname
		form.lastname.data = current_user.lastname
		form.email.data = current_user.email
		form.job_title.data = current_user.job_title
		form.ns_id.data = current_user.ns_id
		form.bio.data = current_user.bio
		form.github.data = current_user.github
		form.twitter.data = current_user.twitter
		# form.roles.data = current_user.roles
		# form.languages.data = current_user.languages
	profile_picture = url_for('static', filename='assets/img/avatars/' + current_user.image_file)
	return render_template('profile_edit.html', title='Profile', profile_picture=profile_picture, form=form,ns_association=ns_association)
	
@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.dashboard'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=form)
	
@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.dashboard'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token.', 'warning')
		return redirect(url_for('users.reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been reset.', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_token.html', title='Reset Password', form=form)