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
		emergency = Emergency(emergency_name=form.emergency_name.data, emergency_location_id=form.emergency_location_id.data.ns_go_id, emergency_type_id=form.emergency_type_id.data.emergency_type_go_id, emergency_glide=form.emergency_glide.data, emergency_go_id=form.emergency_go_id.data, activation_details=form.activation_details.data, slack_channel=form.slack_channel.data, dropbox_url=form.dropbox_url.data, trello_url=form.trello_url.data)
		db.session.add(emergency)
		db.session.commit()
		flash('New emergency successfully created.', 'success')
		return redirect(url_for('main.dashboard'))
	latest_emergencies = Emergency.get_latest_go_emergencies()
	return render_template('create_emergency.html', title='Create New Emergency', form=form, latest_emergencies=latest_emergencies)

@emergencies.route('/emergency/<int:id>', methods=['GET', 'POST'])
@login_required
def view_emergency(id):
	deployments = db.session.query(Assignment, Emergency, User, NationalSociety).join(Emergency, Emergency.id==Assignment.emergency_id).join(User, User.id==Assignment.user_id).join(NationalSociety, NationalSociety.ns_go_id==User.ns_id).filter(Emergency.id==id, Assignment.assignment_status=='Active').all()
	emergency_info = db.session.query(Emergency, EmergencyType).join(EmergencyType, EmergencyType.emergency_type_go_id==Emergency.emergency_type_id).filter(Emergency.id==id).first()
	emergency_portfolio = db.session.query(Portfolio, Emergency).join(Emergency, Emergency.id==Portfolio.emergency_id).filter(Emergency.id==id, Portfolio.product_status=='Active').all()
	return render_template('emergency.html', title='Emergency View', emergency_info=emergency_info, deployments=deployments, emergency_portfolio=emergency_portfolio)

@emergencies.route('/emergency/edit/<int:id>', methods=['GET', 'POST'])
def edit_emergency(id):
	form = UpdateEmergencyForm()
	emergency_info = db.session.query(Emergency).filter(Emergency.id == id).first()
	# emergency_info = db.session.query(Emergency, EmergencyType).join(EmergencyType, EmergencyType.emergency_type_go_id==Emergency.emergency_type_id).filter(Emergency.id==id).first()
	if form.validate_on_submit():
		emergency_info.emergency_name = form.emergency_name.data
		try: 
			emergency_info.emergency_location_id = form.emergency_location_id.data.ns_go_id
		except:
			pass
		try:
			selected_id = form.emergency_type_id.data.emergency_type_go_id
			db.session.query(Emergency).filter(Emergency.id==id).update({'emergency_type_id':selected_id})
		except:
			pass
		try: 
			emergency_info.emergency_go_id = form.emergency_go_id.data
		except:
			pass
		emergency_info.emergency_glide = form.emergency_glide.data
		emergency_info.activation_details = form.activation_details.data
		emergency_info.slack_channel = form.slack_channel.data
		emergency_info.dropbox_url = form.dropbox_url.data
		emergency_info.trello_url = form.trello_url.data
		# print(emergency_info.emergency_type_id)
		# print(type(emergency_info.emergency_type_id))
		print(type(emergency_info.emergency_type_id))
		db.session.commit()
		flash('Emergency record updated!', 'success')
		return redirect(url_for('main.dashboard'))
	elif request.method == 'GET':
		form.emergency_name.data = emergency_info.emergency_name
		form.emergency_glide.data = emergency_info.emergency_glide

		form.emergency_go_id.data = emergency_info.emergency_go_id
		form.activation_details.data = emergency_info.activation_details
		form.slack_channel.data = emergency_info.slack_channel
		form.dropbox_url.data = emergency_info.dropbox_url
		form.trello_url.data = emergency_info.trello_url
	return render_template('emergency_edit.html', form=form, emergency_info=emergency_info)

@emergencies.route('/emergency/closeout/<int:id>')
@login_required
def closeout_emergency(id):
	if current_user.is_admin == 1:
		try:
			db.session.query(Emergency).filter(Emergency.id==id).update({'emergency_status':'Closed'})
			db.session.commit()
			flash("Emergency closed out.", 'success')
		except:
			flash("Error closing emergency. Check that the emergency ID exists.")
		return redirect(url_for('main.dashboard'))
	else:
		list_of_admins = db.session.query(User).filter(User.is_admin==1).all()
		return render_template('errors/403.html', list_of_admins=list_of_admins), 403

@emergencies.route('/emergency/delete/<int:id>')
@login_required
def delete_emergency(id):
	if current_user.is_admin == 1:
		try:
			db.session.query(Emergency).filter(Emergency.id==id).update({'emergency_status':'Removed'})
			db.session.commit()
			flash("Emergency deleted.", 'success')
		except:
			flash("Error deleting emergency. Check that the emergency ID exists.")
		return redirect(url_for('main.dashboard'))
	else:
		list_of_admins = db.session.query(User).filter(User.is_admin==1).all()
		return render_template('errors/403.html', list_of_admins=list_of_admins), 403