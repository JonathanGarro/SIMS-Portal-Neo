from flask import url_for, current_app
import os
import secrets
from PIL import Image

def save_header(form_header):
	random_hex = secrets.token_hex(8)
	filename, file_ext = os.path.splitext(form_header.filename)
	picture_filename = random_hex + file_ext
	picture_path = os.path.join(current_app.root_path, 'static/assets/img/stories', picture_filename)
	
	output_size = (1300, 650)
	resized_image = Image.open(form_header)
	resized_image.thumbnail(output_size)
	resized_image.save(picture_path)
	
	return picture_filename