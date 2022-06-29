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
	count_active_assignments = db.engine.execute("SELECT COUNT(role) as AssignmentCount FROM assignment WHERE end_date > :todays_date", {'todays_date': todays_date}).first()
	active_assignments = db.engine.execute("SELECT * FROM assignment JOIN user ON user.id = assignment.user_id JOIN emergency ON emergency.id = assignment.emergency_id WHERE end_date > :todays_date", {'todays_date': todays_date})
	most_recent_emergencies = db.session.query(Emergency).order_by(Emergency.created_at.desc()).all()
	surge_alerts = db.session.query(Alert).limit(100).all()
	return render_template('dashboard.html', active_assignments=active_assignments, count_active_assignments=count_active_assignments, most_recent_emergencies=most_recent_emergencies,surge_alerts=surge_alerts)