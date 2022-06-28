from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint
from SIMS_Portal.models import Assignment, User, Emergency
from SIMS_Portal import db, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
from SIMS_Portal.assignments.forms import NewAssignmentForm
from datetime import datetime

assignments = Blueprint('assignments', __name__)

@assignments.route('/assignment/new', methods=['GET', 'POST'])
@login_required
def new_assignment():
	form = NewAssignmentForm()
	if form.validate_on_submit():
		assignment = Assignment(user_id=form.user_id.data.id, emergency_id=form.emergency_id.data.id, start_date=form.start_date.data, end_date=form.end_date.data, role=form.role.data, assignment_details=form.assignment_details.data, remote=form.remote.data)
		print(assignment)
		db.session.add(assignment)
		db.session.commit()
		flash('New assignment successfully created.', 'success')
		return redirect(url_for('main.dashboard'))
	return render_template('create_assignment.html', title='New Assignment', form=form)

@assignments.route('/assignment/new/<int:dis_id>', methods=['GET', 'POST'])
@login_required
def new_assignment_from_disaster(dis_id):
	form = NewAssignmentForm()
	emergency_info = db.session.query(Emergency).filter(Emergency.id == dis_id).first()
	if form.validate_on_submit():
		assignment = Assignment(user_id=form.user_id.data.id, emergency_id=dis_id, start_date=form.start_date.data, end_date=form.end_date.data, role=form.role.data, assignment_details=form.assignment_details.data, remote=form.remote.data)
		print(assignment)
		db.session.add(assignment)
		db.session.commit()
		flash('New assignment successfully created.', 'success')
		return redirect(url_for('main.dashboard'))
	return render_template('create_assignment_from_disaster.html', title='New Assignment', form=form, emergency_info=emergency_info)

@assignments.route('/assignment/<int:id>')
@login_required
def view_assignment(id):
	assignment_info = db.session.query(Assignment, User, Emergency).join(User).join(Emergency).filter(Assignment.id == id).first()
	dict_assignment = assignment_info.Assignment.__dict__
	dict_start_date = str(dict_assignment['start_date'])
	dict_end_date = str(dict_assignment['end_date'])
	
	formatted_start_date = datetime.strptime(dict_start_date, '%Y-%m-%d').strftime('%d %b %Y')
	formatted_end_date = datetime.strptime(dict_end_date, '%Y-%m-%d').strftime('%d %b %Y')
	
	days_left = db.engine.execute("SELECT JULIANDAY(:end_date) - JULIANDAY(DATE('now')) AS days_remaining FROM Assignment WHERE id = :id", {'id': id, 'end_date': dict_end_date})
	days_left_dict = days_left.mappings().first()
	days_left_int = int(days_left_dict['days_remaining'])
	print(f"days left value is: {days_left_int}")
	
	assingment_length = db.engine.execute("SELECT JULIANDAY(:end_date) - JULIANDAY(:start_date) AS length FROM Assignment WHERE id = :id", {'id': id, 'end_date': dict_end_date, 'start_date': dict_start_date})
	assignment_length_dict = assingment_length.mappings().first()
	assignment_length_int = int(assignment_length_dict['length'])
	print(f"assignment length value is: {assignment_length_int}")
	
	return render_template('assignment_view.html', assignment_info=assignment_info, formatted_start_date=formatted_start_date, formatted_end_date=formatted_end_date, days_left_int=days_left_int, assignment_length_int=assignment_length_int)

@assignments.route('/assignment/delete/<int:id>')
@login_required
def delete_assignment(id):
	if current_user.is_admin == 1:
		assignment_to_delete = Assignment.query.get_or_404(id)
		try:
			db.session.delete(assignment_to_delete)
			db.session.commit()
			flash("Assignment deleted.", 'success')
		except:
			flash("Error deleting assignment. Check that the assignment ID exists.")
		return redirect(url_for('main.dashboard'))
	else:
		list_of_admins = db.session.query(User).filter(User.is_admin==1).all()
		return render_template('errors/403.html', list_of_admins=list_of_admins), 403