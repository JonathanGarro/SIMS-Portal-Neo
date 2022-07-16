from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint, current_app
from SIMS_Portal import db
from SIMS_Portal.config import Config
from SIMS_Portal.models import Story, Emergency, User, Assignment, Portfolio
from SIMS_Portal.stories.forms import NewStoryForm, UpdateStoryForm
from flask_sqlalchemy import SQLAlchemy
from SIMS_Portal.stories.utils import save_header
from sqlalchemy.sql import func
from flask_login import login_user, logout_user, current_user, login_required

stories = Blueprint('stories', __name__)

@stories.route('/story/<int:emergency_id>')
def view_story(emergency_id): 
	if db.session.query(Story).filter(Story.emergency_id == emergency_id).first():
		story_data = db.session.query(Story).filter(Story.emergency_id == emergency_id).first()
		emergency_name = db.session.query(Story, Emergency).join(Emergency, Emergency.id == emergency_id).first()
		members_supporting = db.session.query(Assignment, User, Story).join(User, User.id == Assignment.user_id).join(Story, Story.emergency_id == Assignment.emergency_id).filter(Assignment.emergency_id == emergency_id, Assignment.assignment_status == 'Active').count()
		member_days = db.engine.execute("SELECT id, JULIANDAY(end_date) - JULIANDAY(start_date) as day_count, emergency_id FROM assignment WHERE emergency_id = :id AND assignment.assignment_status = 'Active'", {'id': emergency_id})
		sum_days = 0
		for day in member_days:
			sum_days += day[1]
		sum_days = int(sum_days)
		products_created = db.session.query(Portfolio, Emergency).join(Emergency, Emergency.id == Portfolio.emergency_id).filter(Emergency.id == emergency_id, Portfolio.product_status == 'Active').count()

		return render_template('story.html', story_data=story_data, emergency_name=emergency_name, members_supporting=members_supporting, sum_days=sum_days, products_created=products_created)
	else:
		return render_template('errors/404.html'), 404

@stories.route('/story/create/<int:emergency_id>', methods=["GET", "POST"])
@login_required
def create_story(emergency_id): 
	form = NewStoryForm()
	check_existing = db.session.query(Story).filter(Story.emergency_id == emergency_id).all()
	if check_existing:
		flash('A story already exists for this emergency', 'danger')
		return redirect(url_for('emergencies.view_emergency', id=emergency_id))
	if current_user.is_admin == 0:
		list_of_admins = db.session.query(User).filter(User.is_admin==1).all()
		return render_template('errors/403.html', list_of_admins=list_of_admins), 403
	if request.method == 'POST' and current_user.is_admin == 1:
		if form.validate_on_submit():
			header_file = save_header(form.header_image.data)
			story = Story(header_image=header_file, header_caption=form.header_caption.data, entry=form.entry.data, emergency_id=emergency_id)
			db.session.add(story)
			db.session.commit()
			flash('New story added!', 'success')
			return redirect(url_for('stories.view_story', emergency_id = emergency_id))
	else:
		emergency_name = db.session.query().with_entities(Emergency.emergency_name).filter(Emergency.id == emergency_id).first()
		return render_template('story_create.html', form=form, emergency_name=emergency_name)

@stories.route('/story/edit/<int:emergency_id>', methods=["GET", "POST"])
@login_required
def edit_story(emergency_id): 
	form = UpdateStoryForm()
	story = db.session.query(Story).filter(Story.emergency_id == emergency_id).first()
	if current_user.is_admin == 0:
		list_of_admins = db.session.query(User).filter(User.is_admin==1).all()
		return render_template('errors/403.html', list_of_admins=list_of_admins), 403
	elif request.method == 'POST' and current_user.is_admin == 1:
		if form.header_image.data:
			header_file = save_header(form.header_image.data)
		else:
			header_file = story.header_image
		header_caption = form.header_caption.data
		story.header_image = header_file
		story.header_caption = header_caption 
		story.entry = form.entry.data
		db.session.commit()
		flash('The story has been updated', 'success')
		return redirect(url_for('stories.view_story', emergency_id=story.emergency_id))
	else:
		emergency_name = db.session.query().with_entities(Emergency.emergency_name).filter(Emergency.id == emergency_id).first()
		form.header_caption.data = story.header_caption
		form.entry.data = story.entry
		return render_template('story_edit.html', form=form, emergency_name=emergency_name, story=story)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	