from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint
from SIMS_Portal.models import Assignment, User, Emergency, Alert, user_skill, user_language, Skill, Language
from SIMS_Portal import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from SIMS_Portal.main.forms import MemberSearchForm

main = Blueprint('main', __name__)

@main.route('/') 
def index(): 
	return render_template('index.html')
	
@main.route('/about')
def about():
	return render_template('about.html')

@main.route('/staging') 
def staging(): 
	mkd_text = "## Your Markdown Here \n **bold**"
	return render_template('visualization.html', mkd_text=mkd_text)

@main.route('/emergencies')
def emergencies():
	return render_template('emergencies.html')

@main.route('/learning')
def learning():
	return render_template('learning.html')

@main.route('/resources')
def resources():
	return render_template('resources.html')

@main.route('/resources/colors')
def resources_colors():
	return render_template('resources_colors.html')

@main.route('/search', methods=['GET', 'POST'])
def search():
	member_form = MemberSearchForm()
	# emergency_form
	# product_form
	if request.method == 'GET':
		return render_template('search.html', member_form=member_form)
	else: 
		if member_form.validate_on_submit():
			name_search = member_form.name.data
			# convert name search to sqlalchemy-friendly syntax for LIKE operator
			search_for_name = "%{}%".format(name_search)
			try:
				skill_search = member_form.skills.data.id
				skill_search_name = member_form.skills.data.name
			except:
				skill_search = 0
				skill_search_name = ''
			try:
				language_search = member_form.languages.data.id
				language_search_name = member_form.languages.data.name
			except:
				language_search = 0
				language_search_name = ''
			if name_search:
				query_by_name = db.session.query(User).filter( (User.firstname.like(search_for_name)) | (User.lastname.like(search_for_name)) ).filter(User.status == 'Active').all()
			else:
				query_by_name = 'None'
				print(query_by_name)
			if skill_search:
				query_by_skill = db.engine.execute("SELECT * FROM user JOIN user_skill ON user_skill.user_id = user.id JOIN skill ON skill.id = user_skill.skill_id WHERE skill_id = :skill", {'skill': skill_search})
			else:
				query_by_skill = 'None'
			if language_search:
				query_by_language = db.engine.execute("SELECT * FROM user JOIN user_language ON user_language.user_id = user.id JOIN language ON language.id = user_language.language_id WHERE language_id = :language", {'language': language_search})
			else:
				query_by_language = 'None'
			return render_template('search_members_results.html', query_by_name=query_by_name, name_search=name_search, query_by_skill=query_by_skill, skill_search_name=skill_search_name, query_by_language=query_by_language, language_search_name=language_search_name)

@main.route('/search/members', methods=['GET', 'POST'])
def search_members():
	form = MemberSearchForm()

	return render_template('search_members.html', query=query)

@main.route('/dashboard')
@login_required
def dashboard():
	todays_date = datetime.today()
	
	assignments_by_emergency = db.engine.execute("SELECT emergency_name, COUNT(*) as count_assignments FROM emergency JOIN assignment ON assignment.emergency_id = emergency.id WHERE assignment.assignment_status <> 'Removed' GROUP BY emergency_name")
	data_dict_assignments = [x._asdict() for x in assignments_by_emergency]
	labels_for_assignment = [row['emergency_name'] for row in data_dict_assignments]
	values_for_assignment = [row['count_assignments'] for row in data_dict_assignments]
	
	products_by_emergency = db.engine.execute("SELECT emergency_name , COUNT(*) as count_products FROM emergency JOIN portfolio ON portfolio.emergency_id = emergency.id WHERE portfolio.product_status <> 'Removed' GROUP BY emergency_name")
	data_dict_products = [y._asdict() for y in products_by_emergency]
	labels_for_product = [row['emergency_name'] for row in data_dict_products]
	values_for_product = [row['count_products'] for row in data_dict_products]
	
	count_active_assignments = db.session.query(Assignment, User, Emergency).join(User, User.id==Assignment.user_id).join(Emergency, Emergency.id==Assignment.emergency_id).filter(Assignment.assignment_status=='Active', Assignment.end_date>todays_date).count()
	active_assignments = db.session.query(Assignment, User, Emergency).join(User, User.id==Assignment.user_id).join(Emergency, Emergency.id==Assignment.emergency_id).filter(Assignment.assignment_status=='Active', Assignment.end_date>todays_date).all()

	most_recent_emergencies = db.session.query(Emergency).order_by(Emergency.created_at.desc()).all()
	surge_alerts = db.session.query(Alert).limit(100).all()
	
	return render_template('dashboard.html', active_assignments=active_assignments, count_active_assignments=count_active_assignments, most_recent_emergencies=most_recent_emergencies,surge_alerts=surge_alerts, labels_for_assignment=labels_for_assignment, values_for_assignment=values_for_assignment, labels_for_product=labels_for_product, values_for_product=values_for_product)
	
	