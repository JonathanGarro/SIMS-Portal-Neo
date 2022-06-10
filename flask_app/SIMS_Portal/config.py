import os

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY')
	SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = 'smtp.dreamhost.com'
	MAIL_PORT = 465
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True
	MAIL_USERNAME = 'sims_portal@dissolvingdata.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	MAIL_DEBUG = True
	SCHEDULER_API_ENABLED = True