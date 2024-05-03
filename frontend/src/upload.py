import os
from flask import flash, redirect, request, Blueprint, current_app
from werkzeug.utils import secure_filename

csv_blueprint = Blueprint('uploads',__name__)

def _allowed_file(filename):
    allowed_extentions = {'csv','env'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extentions

@csv_blueprint.route('/csv', methods=['POST'])
def upload_csv():
    upload_folder = '/data_src'

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and _allowed_file(file.filename):
        filename = os.path.join(upload_folder, file.filename)
        file.save(filename)

        return 'File uploaded successfully'
    else:
        flash('Invalid file type')
        return redirect(request.url)
