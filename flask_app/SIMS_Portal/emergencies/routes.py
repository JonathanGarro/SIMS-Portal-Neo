from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint
from SIMS_Portal import db
from SIMS_Portal.models import User, Assignment, Emergency, NationalSociety, EmergencyType, Alert, Portfolio
from SIMS_Portal.emergencies.forms import NewEmergencyForm, UpdateEmergencyForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required

emergencies = Blueprint('emergencies', __name__)

@emergencies.route('/emergency/new', methods=['GET', 'POST'])
@login_required
def new_emergency():
	form = NewEmergencyForm()
	if form.validate_on_submit():
		emergency = Emergency(emergency_name=form.emergency_name.data, emergency_location_id=form.emergency_location_id.data.ns_go_id, emergency_type_id=form.emergency_type_id.data.id, emergency_glide=form.emergency_glide.data, emergency_go_id=form.emergency_go_id.data, activation_details=form.activation_details.data)
		db.session.add(emergency)
		db.session.commit()
		flash('New emergency successfully created.', 'success')
		return redirect(url_for('main.dashboard'))
	latest_emergencies = Emergency.get_latest_go_emergencies()
	return render_template('create_emergency.html', title='Create New Emergency', form=form, latest_emergencies=latest_emergencies)

@emergencies.route('/emergency/<int:id>', methods=['GET', 'POST'])
@login_required
def view_emergency(id):
	emergency_info = db.session.query(Emergency).filter(Emergency.id == id).first()
	deployments = db.engine.execute("SELECT * FROM assignment JOIN emergency ON emergency.id = assignment.emergency_id JOIN user ON user.id = assignment.user_id JOIN nationalsociety ON nationalsociety.ns_go_id = user.ns_id WHERE emergency.id = :id", {'id': id}).all()
	emergency_type = db.engine.execute("SELECT * FROM emergency JOIN emergencytype ON emergencytype.emergency_type_go_id = emergency.emergency_type_id WHERE emergency.id = :id", {'id': id})
	emergency_portfolio = db.engine.execute("SELECT * FROM portfolio JOIN emergency ON emergency.id = portfolio.emergency_id WHERE emergency.id = :id", {'id': id}).all()
	emergency_type_name = [row.emergency_type_name for row in emergency_type]
	return render_template('emergency.html', title='Emergency View', emergency_info=emergency_info, emergency_type=emergency_type, emergency_type_name=emergency_type_name[0], deployments=deployments, emergency_portfolio=emergency_portfolio)

@emergencies.route('/emergency/edit/<int:id>', methods=['GET', 'POST'])
def edit_emergency(id):
	form = UpdateEmergencyForm()
	emergency_info = db.session.query(Emergency).filter(Emergency.id == id).first()
	if form.validate_on_submit():
		emergency_info.emergency_name = form.emergency_name.data
		emergency_info.emergency_location_id = form.emergency_location_id.data.ns_go_id
		emergency_info.emerency_type_id = form.emergency_type_id.data.id
		emergency_info.emergency_glide = form.emergency_glide.data
		# emergency_info.emergency_go_id = form.emergency_go_id.data
		emergency_info.activation_details = form.activation_details.data
		db.session.commit()
		flash('Emergency record updated!', 'success')
		return redirect(url_for('main.dashboard'))
	elif request.method == 'GET':
		form.emergency_name.data = emergency_info.emergency_name
		# form.emergency_location_id.data = 
		form.emergency_glide.data = emergency_info.emergency_glide
		form.emergency_type_id.data = db.session.execute("SELECT emergencytype.id FROM emergencytype JOIN emergency ON emergency.emergency_type_id == emergencytype.id WHERE emergency.id = 1").first()[0]
		print(form.emergency_type_id.data)
		# form.emergency_go_id.data = emergency_info.emergency_go_id
		form.activation_details.data = emergency_info.activation_details
	return render_template('emergency_edit.html', form=form, emergency_info=emergency_info)