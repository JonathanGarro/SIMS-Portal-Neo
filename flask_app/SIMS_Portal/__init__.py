from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import requests
import math
import os
import time	

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login' # 'login' refers to the route to redirect to when user tries to access a page where @login_required but not currently logged in
login_manager.login_message_category = 'danger'
app.config['MAIL_SERVER'] = 'smtp.dreamhost.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'sims_portal@dissolvingdata.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEBUG'] = True
mail = Mail(app)

# 
from SIMS_Portal import routes, models
# 
# get_go = BackgroundScheduler(daemon = True)
# get_go.start()
# 
# @get_go.scheduled_job(trigger = 'cron', day = '*')
# def get_im_alerts():
# 	print("RUNNING CRON JOB\n================\n")
# 	time.sleep(10) # the server seems to hang sometimes and skip this step, adding delay to give it a chance to complete this step before moving forward
# 	alert.Alert.clear_alert_table_before_update() # clear out alerts table before API run
# 	print("WAITING 10 SECONDS FOR DATABASE CLEANUP")
# 	time.sleep(10) # the server seems to hang sometimes and skip this step, adding delay to give it a chance to complete this step before moving forward
# 	print("DATABASE CLEANUP COMPLETE")
# 	
# 	api_call = 'https://goadmin.ifrc.org/api/v2/surge_alert/'
# 	r = requests.get(api_call).json()
# 	
# 	current_page = 1
# 	page_count = int(math.ceil(r['count'] / 50))
# 	print(f"THE PAGE COUNT TOTAL IS: {page_count}")
# 	
# 	output = []
# 	
# 	while current_page <= page_count:
# 		for x in r['results']:
# 			temp_dict = {}
# 			if x['molnix_tags']:
# 				for y in x['molnix_tags']:
# 					if ("Manager" in y['description']) or ("Officer" in y['description']) or ("Analyst" in y['description']) or ("Coordinator" in y['description']):
# 						temp_dict['role_profile'] = y['description']
# 						temp_dict['alert_date'] = x['opens']
# 						temp_dict['alert_id'] = x['id']
# 						temp_dict['alert_status'] = x['molnix_status']
# 						if x['event']:
# 							temp_dict['event_name'] = x['event']['name']
# 							temp_dict['event_go_id'] = x['event']['id']
# 							temp_dict['event_date'] = x['event']['disaster_start_date']
# 						if x['country']:
# 							temp_dict['location'] = x['country']['name']
# 						output.append(temp_dict)
# 		if r['next']:
# 			next_page = requests.get(r['next']).json()
# 			r = next_page
# 			current_page += 1
# 		else:
# 			break
# 	for each in output:
# 		alert.Alert.save_GO_alerts_from_API(each)
# 	print("\n==================\nFINISHED CRON JOB")