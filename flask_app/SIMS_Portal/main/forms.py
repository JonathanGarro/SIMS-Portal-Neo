from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, BooleanField, IntegerField, DateField, DateTimeField, SelectField, SelectMultipleField, HiddenField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from SIMS_Portal.models import User, Emergency, Portfolio, Skill, Language, EmergencyType, NationalSociety, Badge

class MemberSearchForm(FlaskForm):
	name = StringField('Member Name')
	skills = QuerySelectField('Skill', query_factory=lambda:Skill.query.all(), get_label='name', allow_blank=True)
	languages = QuerySelectField('Language', query_factory=lambda:Language.query.order_by(Language.name).all(), get_label='name', allow_blank=True)
	submit = SubmitField('Search Members')

class EmergencySearchForm(FlaskForm):
	name = StringField('Emergency Name')
	status = SelectField('SIMS Status', choices=['', 'Active', 'Closed', 'Removed'])
	type = QuerySelectField('Emergency Type', query_factory=lambda:EmergencyType.query.all(), get_label='emergency_type_name', allow_blank=True)
	location = QuerySelectField('Primary Country', query_factory=lambda:NationalSociety.query.all(), get_label='country_name', allow_blank=True)
	glide = StringField('GLIDE Number')
	submit = SubmitField('Search Emergencies')

class ProductSearchForm(FlaskForm):
	name = StringField('Product Name')
	type = SelectField('File Type', choices=['', 'Map', 'Infographic', 'Dashboard', 'Mobile Data Collection', 'Assessment', 'Report / Analysis', 'Other'])
	description = StringField('Search Product Description')
	submit = SubmitField('Search Products')
	
class BadgeAssignmentForm(FlaskForm):
	user_name = QuerySelectField('Member', query_factory=lambda:User.query.order_by(User.firstname).filter(User.status == 'Active').all(), get_label='fullname', allow_blank=True)
	badge_name = QuerySelectField('Badge', query_factory=lambda:Badge.query.order_by(Badge.name).all(), get_label='name', allow_blank=True)
	submit = SubmitField('Assign')