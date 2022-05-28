from SIMS_Portal import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, ForeignKey, Integer, Table

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class NationalSociety(db.Model):
	__tablename__ = 'nationalsociety'
	
	id = db.Column(db.Integer, primary_key=True)
	
	ns_name = db.Column(db.String(120), nullable=False)
	country_name = db.Column(db.String(120), nullable=False)
	ns_go_id = db.Column(db.Integer)
	
	users = db.relationship('User', backref='national_society', lazy=True)
	
	created_at = db.Column(db.DateTime, server_default=func.now())
	updated_at = db.Column(db.DateTime, onupdate=func.now())

	def __repr__(self):
		return f"NationalSociety('{self.ns_name}','{self.country_name}','{self.ns_go_id}'"

class User(db.Model, UserMixin):
	__tablename__ = 'user'
	
	id = db.Column(db.Integer, primary_key=True)
	
	firstname = db.Column(db.String(40), nullable=False)
	lastname = db.Column(db.String(40), nullable=False)
	status = db.Column(db.String(20), default='Pending')
	birthday = db.Column(db.Date)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	molnix_id = db.Column(db.Integer)
	job_title = db.Column(db.String(120))
	bio = db.Column(db.Text)
	is_admin = db.Column(db.Boolean, default=False)
	roles = db.Column(db.String(1000))
	languages = db.Column(db.String(1000))
	image_file = db.Column(db.String(20), nullable=False, default='default.png')
	
	ns_id = db.Column(db.Integer, ForeignKey('nationalsociety.id'))
	
	assignments = db.relationship('Assignment', backref='assigned_member')
	products = db.relationship('Portfolio', backref='creator', lazy=True)
	
	created_at = db.Column(db.DateTime, server_default=func.now())
	updated_at = db.Column(db.DateTime, onupdate=func.now())
	
	@hybrid_property
	def fullname(self):
		return self.firstname + " " + self.lastname
	
	def __repr__(self):
		return f"User('{self.id}, {self.firstname}','{self.lastname}','{self.email}','{self.image_file}')"

class Assignment(db.Model):
	__tablename__ = 'assignment'
	
	id = db.Column(db.Integer, primary_key=True)
	
	role = db.Column(db.String(100))
	start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
	end_date = db.Column(db.Date, nullable=False)
	remote = db.Column(db.Boolean)
	assignment_details = db.Column(db.String(1000))
	
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	emergency_id = db.Column(db.Integer, db.ForeignKey('emergency.id'), default=0)
	
	created_at = db.Column(db.DateTime, server_default=func.now())
	updated_at = db.Column(db.DateTime, onupdate=func.now())

	def __repr__(self):
		return f"Assignment('{self.role}','{self.start_date}','{self.end_date}','{self.remote}','{self.assignment_details}')"

class Emergency(db.Model):
	__tablename__ = 'emergency'
	
	id = db.Column(db.Integer, primary_key=True)
	
	emergency_name = db.Column(db.String(100), nullable=False)
	emergency_glide = db.Column(db.String(20))
	emergency_go_id = db.Column(db.Integer)
	emergency_location_id = db.Column(db.Integer)
	emergency_review_id = db.Column(db.Integer)
	activation_details = db.Column(db.String(1000))
	
	emergency_type_id = db.Column(db.Integer, db.ForeignKey('emergencytype.id'))
	
	emergency_products = db.relationship('Portfolio', backref='emergency_response', lazy=True)
	assigned_to = db.relationship('Assignment', backref='assigned_emergency', lazy=True)
	
	created_at = db.Column(db.DateTime, server_default=func.now())
	updated_at = db.Column(db.DateTime, onupdate=func.now())
		
	def __repr__(self):
		return f"Emergency('{self.emergency_name}','{self.emergency_glide}','{self.emergency_go_id}','{self.emergency_location_id}','{self.emergency_type_id}','{self.emergency_review_id}','{self.activation_details}')"

class EmergencyType(db.Model):
	__tablename__ = 'emergencytype'
	
	id = db.Column(db.Integer, primary_key=True)
	
	emergency_type_go_id = db.Column(db.Integer)
	emergency_type_name = db.Column(db.String)
	
	emergencies = db.relationship('Emergency', backref='emergencies_of_type')
	
	created_at = db.Column(db.DateTime, server_default=func.now())
	updated_at = db.Column(db.DateTime, onupdate=func.now())

class Portfolio(db.Model):
	__tablename__ = 'portfolio'
	
	id = db.Column(db.Integer, primary_key=True)
	
	title = db.Column(db.String(200), nullable=False)
	type = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text)
	final_file_location = db.Column(db.String(100), nullable=False)
	asset_file_location = db.Column(db.String(100), nullable=False)
	
	creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	emergency_id = db.Column(db.Integer, ForeignKey('emergency.id'))
	
	created_at = db.Column(db.DateTime, server_default=func.now())
	updated_at = db.Column(db.DateTime, onupdate=func.now())

	def __repr__(self):
		return f"Portfolio('{self.title}','{self.type}','{self.description}','{self.file_location}','{self.creator_id}')"

