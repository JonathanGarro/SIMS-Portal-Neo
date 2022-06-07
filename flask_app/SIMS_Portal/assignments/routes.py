from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint
from SIMS_Portal.models import Assignment, User
from SIMS_Portal import db, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
from SIMS_Portal.assignments.forms import NewAssignmentForm

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