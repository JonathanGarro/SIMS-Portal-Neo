from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, BooleanField, IntegerField, DateField, DateTimeField, SelectField, SelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from SIMS_Portal.models import User, Emergency, Portfolio, Skill, Language

class MemberSearchForm(FlaskForm):
	name = StringField('Member Name')
	skills = QuerySelectField('Skill', query_factory=lambda:Skill.query.all(), get_label='name', allow_blank=True)
	languages = QuerySelectField('Language', query_factory=lambda:Language.query.all(), get_label='name', allow_blank=True)
	submit = SubmitField('Search Members')