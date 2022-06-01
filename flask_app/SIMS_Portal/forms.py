from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DateField, DateTimeField, TextAreaField, SelectField, SelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from SIMS_Portal.models import User, Emergency, NationalSociety, EmergencyType, Portfolio, Skill, Language

def get_users():
	return User.query.all()

class RegistrationForm(FlaskForm):
	firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=40)])
	lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=40)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=24)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6, max=24), EqualTo('password')])
	submit = SubmitField('Register')
	
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email is already registered.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=24)])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')
	
class UpdateAccountForm(FlaskForm):
	firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=40)])
	lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=40)])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	email = StringField('Email', validators=[DataRequired(), Email()])
	job_title = StringField('Job Title')
	ns_id = QuerySelectField('National Society Country', query_factory=lambda:NationalSociety.query.all(), get_label='country_name', allow_blank=True)
	bio = TextAreaField('Short Bio')
	birthday = DateField('Birthday')
	molnix_id = IntegerField('Molnix ID')
	twitter = StringField('Twitter Handle')
	github = StringField('Github Username')
	roles = StringField('SIMS Roles')
	languages = SelectMultipleField('Languages', choices=lambda:[language.name for language in Language.query.all()])
	skills = SelectMultipleField('Skills', choices=lambda:[skill.name for skill in Skill.query.all()])
	submit = SubmitField('Update Profile')
	
	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email is already registered.')

class NewAssignmentForm(FlaskForm):
	user_id = QuerySelectField('SIMS Member', query_factory=lambda:User.query.filter_by(status='Active'), get_label='fullname', allow_blank=True)
	emergency_id = QuerySelectField('Emergency', query_factory=lambda:Emergency.query.all(), get_label='emergency_name', allow_blank=True)
	role = SelectField("Role Type", choices=['', 'SIMS Remote Coordinator', 'Information Management Coordinator', 'Information Analyst', 'Primary Data Collection Officer', 'Mapping and Visualization Officer', 'Remote IM Support'])
	start_date = DateTimeField('Start Date', format='%Y-%m-%d')
	end_date = DateTimeField('End Date', format='%Y-%m-%d')
	remote = BooleanField('Remote?')
	assignment_details = TextAreaField('Assignment Description')
	submit = SubmitField('Create Assignment')
	
class NewEmergencyForm(FlaskForm):
	emergency_name = StringField('Emergency Name', validators=[DataRequired(), Length(min=5, max=100)])
	emergency_location_id = QuerySelectField('Affected Country (Primary)', query_factory=lambda:NationalSociety.query.all(), get_label='country_name', allow_blank=True, validators=[DataRequired()])
	emergency_type_id = QuerySelectField('Emergency Type', query_factory=lambda:EmergencyType.query.all(), get_label='emergency_type_name', allow_blank=True, validators=[DataRequired()])
	emergency_glide = StringField('GLIDE Number')
	emergency_go_id = IntegerField('GO ID Number')
	activation_details = TextAreaField('SIMS Activation Details')
	submit = SubmitField('Create Emergency')

class PortfolioUploadForm(FlaskForm):
	title = StringField('Product Title', validators=[DataRequired()])
	emergency_id = QuerySelectField('Emergency', query_factory=lambda:Emergency.query.all(), get_label='emergency_name', allow_blank=True)
	creator_id = QuerySelectField('Creator', query_factory=lambda:User.query.filter_by(status='Active'), get_label='fullname', allow_blank=True, validators=[DataRequired()])
	description = TextAreaField('Description')
	type = SelectField('File Type', choices=['', 'Map', 'Infographic', 'Dashboard', 'Mobile Data Collection', 'Assessment', 'Report / Analysis', 'Other'], validators=[DataRequired()])
	file = FileField('Attach File', validators=[FileAllowed(['jpg', 'png', 'pdf', 'xls', 'xlsm', 'xltx', 'txt', 'doc', 'docxs' 'csv', 'shp', 'ai', 'zip'])])
	external = BooleanField('Share Publicly')
	submit = SubmitField('Upload SIMS Product')

















