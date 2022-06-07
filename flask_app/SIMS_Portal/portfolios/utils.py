import os
import secrets
from flask import current_app

def save_portfolio(form_file):
	random_hex = secrets.token_hex(8)
	filename, file_ext = os.path.splitext(form_file.filename)
	file_filename = random_hex + file_ext
	file_path = os.path.join(current_app.root_path, 'static/assets/portfolio', file_filename)
	form_file.save(file_path)
	
	return file_filename
