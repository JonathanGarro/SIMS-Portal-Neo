from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint
from SIMS_Portal.models import Assignment, User, Emergency, Alert
from SIMS_Portal import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/') 
def index(): 
	return render_template('index.html')
	
@main.route('/staging') 
def staging(): 
	return render_template('visualization.html')

@main.route('/resources')
def resources():
	return render_template('resources.html')

@main.route('/about')
def about():
	return render_template('about.html')
	
@main.route('/resources/colors')
def resources_colors():
	return render_template('resources_colors.html')

@main.route('/dashboard')
@login_required
def dashboard():
	todays_date = datetime.today()
	
	assignments_by_emergency = db.engine.execute("SELECT emergency_name, COUNT(*) as count_assignments FROM emergency JOIN assignment ON assignment.emergency_id = emergency.id WHERE assignment.assignment_status <> 'Removed' GROUP BY emergency_name")
	data_dict = [r._asdict() for r in assignments_by_emergency]
	labels = [row['emergency_name'] for row in data_dict]
	values = [row['count_assignments'] for row in data_dict]
	
	count_active_assignments = db.session.query(Assignment, User, Emergency).join(User, User.id==Assignment.user_id).join(Emergency, Emergency.id==Assignment.emergency_id).filter(Assignment.assignment_status=='Active', Assignment.end_date>todays_date).count()
	active_assignments = db.session.query(Assignment, User, Emergency).join(User, User.id==Assignment.user_id).join(Emergency, Emergency.id==Assignment.emergency_id).filter(Assignment.assignment_status=='Active', Assignment.end_date>todays_date).all()

	most_recent_emergencies = db.session.query(Emergency).order_by(Emergency.created_at.desc()).all()
	surge_alerts = db.session.query(Alert).limit(100).all()
	return render_template('dashboard.html', active_assignments=active_assignments, count_active_assignments=count_active_assignments, most_recent_emergencies=most_recent_emergencies,surge_alerts=surge_alerts, labels=labels, values=values)