from flask import request, render_template, url_for, flash, redirect, jsonify, Blueprint, current_app
from SIMS_Portal import db
from SIMS_Portal.config import Config
from SIMS_Portal.models import User, Assignment, Emergency, NationalSociety, EmergencyType, Alert, Portfolio, Story, Learning
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import login_user, logout_user, current_user, login_required

learnings = Blueprint('learnings', __name__)

@learnings.route('/learning/assignment/new/<int:user_id>/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def create_new_assignment_learning(user_id, assignment_id):
	
	
	
	
	return render_template('learning_assignment.html')