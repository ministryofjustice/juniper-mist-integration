import os
from flask import Flask, render_template,redirect, url_for, request, flash, redirect
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/data_src'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(
    __name__
    )

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key_here'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-site')
def add_site():
    return render_template('add_site.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = os.path.join(app.config['UPLOAF_FOLDER'], file.filename)
        file.save(filename)
        
        return 'File uploaded successfully'
        
    
@app.route('/assign-site')
def assign_site():
    return render_template('assign_site.html')

@app.route('/assets/images/<path:path>')
def asset_images_govuk(path):
    return redirect('/static/gov-uk-frontend/assets/images/' + path, code=301)

@app.route('/assets/fonts/<path:path>')
def asset_fonts(path):
    return redirect('/static/gov-uk-frontend/assets/fonts/' + path, code=301)


if __name__ == '__main__':
    app.run(debug=True)
