from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import math
import time	
from SIMS_Portal.config import Config

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login' # 'login' refers to the route to redirect to when user tries to access a page where @login_required but not currently logged in
login_manager.login_message_category = 'danger'
mail = Mail()

from SIMS_Portal import models
# from SIMS_Portal.models import Alert

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)
	
	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	
	from SIMS_Portal.main.routes import main
	from SIMS_Portal.assignments.routes import assignments
	from SIMS_Portal.emergencies.routes import emergencies
	from SIMS_Portal.portfolios.routes import portfolios
	from SIMS_Portal.users.routes import users
	
	app.register_blueprint(main)
	app.register_blueprint(assignments)
	app.register_blueprint(emergencies)
	app.register_blueprint(portfolios)
	app.register_blueprint(users)
	
	return app

get_go = BackgroundScheduler(daemon = True)
get_go.start()

@get_go.scheduled_job(trigger = 'cron', day = '*') 
def get_im_alerts():
	print("RUNNING CRON JOB\n================\n")
	time.sleep(10) # the server seems to hang sometimes and skip this step, adding delay to give it a chance to complete this step before moving forward
	db.engine.execute("DELETE FROM alert") # clear out alerts table before API run
	print("WAITING 10 SECONDS FOR DATABASE CLEANUP")
	time.sleep(10) # the server seems to hang sometimes and skip this step, adding delay to give it a chance to complete this step before moving forward
	print("DATABASE CLEANUP COMPLETE")
	
	api_call = 'https://goadmin.ifrc.org/api/v2/surge_alert/'
	r = requests.get(api_call).json()
	
	current_page = 1
	page_count = int(math.ceil(r['count'] / 50))
	print(f"THE PAGE COUNT TOTAL IS: {page_count}")
	
	output = []
	
	while current_page <= page_count:
		for x in r['results']:
			temp_dict = {}
			if x['molnix_tags']:
				for y in x['molnix_tags']:
					if ("Manager" in y['description']) or ("Officer" in y['description']) or ("Analyst" in y['description']) or ("Coordinator" in y['description']):
						temp_dict['role_profile'] = y['description']
						temp_dict['alert_date'] = x['opens']
						temp_dict['alert_id'] = x['id']
						temp_dict['alert_status'] = x['molnix_status']
						if x['event']:
							temp_dict['event_name'] = x['event']['name']
							temp_dict['event_go_id'] = x['event']['id']
							temp_dict['event_date'] = x['event']['disaster_start_date']
						if x['country']:
							temp_dict['location'] = x['country']['name']
						output.append(temp_dict)
		if r['next']:
			next_page = requests.get(r['next']).json()
			r = next_page
			current_page += 1
		else:
			break
	for each in output:
		for each in output: 
			alert = Alert(role_profile=each.get('role_profile'), alert_date=each.get('alert_date'), alert_id=each.get('alert_id'), alert_status=each.get('alert_status'), event_name=each.get('event_name'), event_go_id=each.get('event_go_id'), event_date=each.get('event_date'), location=each.get('location'))
			db.session.add(alert)
			db.session.commit()
		
	print("\n==================\nFINISHED CRON JOB")