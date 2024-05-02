import os
from flask import flash, redirect, request
from werkzeug.utils import secure_filename

class CsvUtils:

    def __init__(app):
        self.app=app
        self.upload_folder = '/data_src'
        self.allowed_extentions = {'csv'}


    def upload_csv(self):
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and _allowed_file(file.filename):
            filename = os.path.join(self.app.config[self.upload_folder], file.filename)
            file.save(filename)

            return 'File uploaded successfully'
        else:
            flash('Invalid file type')
            return redirect(request.url)


    def _allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.allowed_extentions
