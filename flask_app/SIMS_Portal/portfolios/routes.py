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
	public_portfolio = db.session.query(Portfolio).filter(Portfolio.external==1).all()
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
			final_file_location = file, title=form.title.data, creator_id=form.creator_id.data.id, description=form.description.data, type=form.type.data, emergency_id=form.emergency_id.data.id, external=form.external.data
		)
		db.session.add(product)
		db.session.commit()
		flash('New product successfully uploaded.', 'success')
		return redirect(url_for('users.profile'))
	return render_template('create_portfolio.html', title='Upload New SIMS Product', form=form)

@portfolios.route('/portfolio/view/<int:id>')
def view_portfolio(id):
	product = db.session.query(Portfolio, User, Emergency).join(User, User.id == Portfolio.creator_id).join(Emergency, Emergency.id == Portfolio.emergency_id).filter(Portfolio.id==id).first()
	return render_template('portfolio_view.html', product=product)