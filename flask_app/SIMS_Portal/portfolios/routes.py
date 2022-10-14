from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint, current_app, send_file
from SIMS_Portal import db
from SIMS_Portal.models import User, Assignment, Emergency, NationalSociety, Portfolio, EmergencyType, Skill, Language, user_skill, user_language, Badge, Alert
from SIMS_Portal.portfolios.forms import PortfolioUploadForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required
from SIMS_Portal.portfolios.utils import save_portfolio
import os

portfolios = Blueprint('portfolios', __name__)

@portfolios.route('/portfolio')
def portfolio():
	type_search = ''
	type_list = ['Map', 'Infographic', 'Dashboard', 'Mobile Data Collection', 'Assessment', 'Report - Analysis', 'Other']
	public_portfolio = db.session.query(Portfolio).filter(Portfolio.external==1, Portfolio.product_status=='Active').all()
	return render_template('portfolio_public.html', title="SIMS Products", public_portfolio=public_portfolio, type_list=type_list, type_search=type_search)
	
@portfolios.route('/portfolio/filter/<type>', methods=['GET', 'POST'])
def filter_portfolio(type):
	type_list = ['Map', 'Infographic', 'Dashboard', 'Mobile Data Collection', 'Assessment', 'Report - Analysis', 'Other']
	type_search = "{}".format(type)
	public_portfolio = db.session.query(Portfolio).filter(Portfolio.external==1, Portfolio.product_status=='Active', Portfolio.type == type_search).all()
	return render_template('portfolio_public.html', title="SIMS Products", public_portfolio=public_portfolio, type_search=type_search, type_list=type_list)
	
@portfolios.route('/all_products')
@login_required
def all_products():
	type_search = ''
	full_portfolio = db.session.query(Portfolio).filter(Portfolio.product_status=='Active').all()
	type_list = ['Map', 'Infographic', 'Dashboard', 'Mobile Data Collection', 'Assessment', 'Report - Analysis', 'Other']
	return render_template('portfolio_all.html', title="SIMS Products", full_portfolio=full_portfolio, type_list=type_list, type_search=type_search)

@portfolios.route('/portfolio_private/filter/<type>', methods=['GET', 'POST'])
@login_required
def filter_portfolio_private(type):
	type_list = ['Map', 'Infographic', 'Dashboard', 'Mobile Data Collection', 'Assessment', 'Report - Analysis', 'Other']
	type_search = "{}".format(type)
	full_portfolio = db.session.query(Portfolio).filter(Portfolio.product_status=='Active', Portfolio.type == type_search).all()
	return render_template('portfolio_all.html', title="SIMS Products", full_portfolio=full_portfolio, type_search=type_search, type_list=type_list)

@portfolios.route('/portfolio/new', methods=['GET', 'POST'])
@login_required
def new_portfolio():
	form = PortfolioUploadForm()
	if form.validate_on_submit():
		if form.file.data:
			file = save_portfolio(form.file.data)
		if form.external.data == True:
			form.external.data = 1
			status = 'Pending Approval'
		else:
			form.external.data = 0
			status = 'Active'
		product = Portfolio(
			final_file_location = file, title=form.title.data, creator_id=form.creator_id.data.id, description=form.description.data, type=form.type.data, emergency_id=form.emergency_id.data.id, external=form.external.data, asset_file_location=form.asset_file_location.data, product_status=status
		)
		db.session.add(product)
		db.session.commit()
		flash('New product successfully uploaded.', 'success')
		return redirect(url_for('users.profile'))
	return render_template('create_portfolio.html', title='Upload New SIMS Product', form=form)

@portfolios.route('/portfolio/new_from_assignment/<int:assignment_id>/<int:user_id>/<int:emergency_id>', methods=['GET', 'POST'])
@login_required
def new_portfolio_from_assignment(assignment_id, user_id, emergency_id):
	form = PortfolioUploadForm()
	if form.validate_on_submit():
		if form.file.data:
			file = save_portfolio(form.file.data)
		if form.external.data == True:
			form.external.data = 1
			status = 'Pending Approval'
		else:
			form.external.data = 0
			status = 'Active'
		product = Portfolio(
			final_file_location = file, title=form.title.data, creator_id=user_id, description=form.description.data, type=form.type.data, emergency_id=emergency_id, external=form.external.data, assignment_id=assignment_id, asset_file_location=form.asset_file_location.data, product_status=status
		)
		db.session.add(product)
		db.session.commit()
		flash('New product successfully uploaded.', 'success')
		# return redirect(url_for('users.profile'))
		redirect_url = '/assignment/{}'.format(assignment_id)
		return redirect(redirect_url)
	return render_template('create_portfolio_from_assignment.html', title='Upload New SIMS Product', form=form)

@portfolios.route('/portfolio/view/<int:id>')
def view_portfolio(id):
	try:
		product = db.session.query(Portfolio, User, Emergency).join(User, User.id == Portfolio.creator_id).join(Emergency, Emergency.id == Portfolio.emergency_id).filter(Portfolio.id==id).first()

		return render_template('portfolio_view.html', product=product)
	except:
		return redirect('error404')

@portfolios.route('/portfolio/download/<int:id>')
def download_portfolio(id):
	product = db.session.query(Portfolio).filter(Portfolio.id==id).first()
	path = os.path.join(current_app.root_path, 'static/assets/portfolio', product.final_file_location)
	return send_file(path, as_attachment=True)

@portfolios.route('/portfolio/delete/<int:id>')
@login_required
def delete_portfolio(id):
	if current_user.is_admin == 1 or current_user.id == id:
		try:
			db.session.query(Portfolio).filter(Portfolio.id==id).update({'product_status':'Removed'})
			db.session.commit()
			flash("Product deleted.", 'success')
		except:
			flash("Error deleting product. Check that the product ID exists.")
		return redirect(url_for('main.dashboard'))
	else:
		list_of_admins = db.session.query(User).filter(User.is_admin==1).all()
		return render_template('errors/403.html', list_of_admins=list_of_admins), 403
		
@portfolios.route('/portfolio/review/<int:dis_id>', methods=['GET', 'POST'])
@login_required
def review_portfolio(dis_id):
	# get list of all SIMS coordinators for event
	disaster_coordinator_query = db.session.query(Emergency, Assignment, User).join(Assignment, Assignment.emergency_id == Emergency.id).join(User, User.id == Assignment.user_id).filter(Emergency.id == dis_id, Assignment.role == 'SIMS Remote Coordinator').all()
	# for loop gets the user id of query and appends to list
	disaster_coordinator_list = []
	for coordinator in disaster_coordinator_query:
		disaster_coordinator_list.append(coordinator.User.id)
	
	# check if current user is one of the event's coordinators
	if current_user.id in disaster_coordinator_list or current_user.is_admin == 1:
		pass
	else:
		event_name = db.session.query(Emergency).filter(Emergency.id == dis_id).first()
		list_of_admins = db.session.query(User).filter(User.is_admin==1).all()
		return render_template('errors/403.html', list_of_admins=list_of_admins, disaster_coordinator_query=disaster_coordinator_query, event_name=event_name), 403
	# get pending products for this emergency	
	pending_list = db.session.query(Portfolio, Emergency, User).join(Emergency, Emergency.id == Portfolio.emergency_id).join(User, User.id == Portfolio.creator_id).filter(Portfolio.emergency_id == dis_id, Portfolio.product_status == 'Pending Approval').all()

	return render_template('portfolio_approve.html', pending_list=pending_list)
	
	
@portfolios.route('/portfolio/approve/<int:prod_id>/<int:dis_id>', methods=['GET', 'POST'])
@login_required
def approve_portfolio(prod_id, dis_id):
	# get list of all SIMS coordinators for event
	disaster_coordinator_query = db.session.query(Emergency, Assignment, User).join(Assignment, Assignment.emergency_id == Emergency.id).join(User, User.id == Assignment.user_id).filter(Emergency.id == dis_id, Assignment.role == 'SIMS Remote Coordinator').all()
	# for loop gets the user id of query and appends to list
	disaster_coordinator_list = []
	for coordinator in disaster_coordinator_query:
		disaster_coordinator_list.append(coordinator.User.id)
	
	# check if current user is one of the event's coordinators
	if current_user.id in disaster_coordinator_list or current_user.is_admin == 1:
		try:
			db.session.query(Portfolio).filter(Portfolio.id == prod_id).update({'product_status':'Approved'})
			db.session.commit()
			flash('Product has been approved for external viewers.', 'success')
		except:
			flash('Error approving the product. Check that the product ID is correct.', 'warning')
		redirect_url = '/emergency/{}'.format(dis_id)
		return redirect(redirect_url)
			
	else:
		event_name = db.session.query(Emergency).filter(Emergency.id == dis_id).first()
		list_of_admins = db.session.query(User).filter(User.is_admin==1).all()
		return render_template('errors/403.html', list_of_admins=list_of_admins, disaster_coordinator_query=disaster_coordinator_query, event_name=event_name), 403
	
	
	
	
	
	
	
	
	
	
	
	