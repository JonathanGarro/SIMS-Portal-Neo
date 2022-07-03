from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint
from SIMS_Portal import db
from SIMS_Portal.models import User, Assignment, Emergency, NationalSociety, Portfolio, EmergencyType, Skill, Language, user_skill, user_language, Badge, Alert
from SIMS_Portal.portfolios.forms import PortfolioUploadForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required
from SIMS_Portal.portfolios.utils import save_portfolio

portfolios = Blueprint('portfolios', __name__)

@portfolios.route('/portfolio')
def portfolio():
	public_portfolio = db.session.query(Portfolio).filter(Portfolio.external==1, Portfolio.product_status=='Active').all()
	return render_template('portfolio_public.html', title="SIMS Products", public_portfolio=public_portfolio)

@portfolios.route('/portfolio/new', methods=['GET', 'POST'])
@login_required
def new_portfolio():
	form = PortfolioUploadForm()
	if form.validate_on_submit():
		if form.file.data:
			file = save_portfolio(form.file.data)
		if form.external.data == True:
			form.external.data = 1
		else:
			form.external.data = 0
		product = Portfolio(
			final_file_location = file, title=form.title.data, creator_id=form.creator_id.data.id, description=form.description.data, type=form.type.data, emergency_id=form.emergency_id.data.id, external=form.external.data, asset_file_location=form.asset_file_location.data
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
		else:
			form.external.data = 0
		product = Portfolio(
			final_file_location = file, title=form.title.data, creator_id=user_id, description=form.description.data, type=form.type.data, emergency_id=emergency_id, external=form.external.data, assignment_id=assignment_id, asset_file_location=form.asset_file_location.data
		)
		print(product)
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
		print(product)
		return render_template('portfolio_view.html', product=product)
	except:
		return redirect('error404')

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