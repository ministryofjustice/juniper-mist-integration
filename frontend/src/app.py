import os
from flask import Flask, render_template,redirect, jsonify
from upload import csv_blueprint
from assets_redirect import redirects_blueprint
from lookup import lookup_blueprint

app = Flask(
    __name__
    )

app.config['APP_NAME'] = 'juniper_web_handler'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.register_blueprint(csv_blueprint, url_prefix='/upload')
app.register_blueprint(redirects_blueprint, url_prefix='/assets')
app.register_blueprint(lookup_blueprint, url_prefix='/lookup')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-site')
def add_site():
    return render_template('add_site.html')

@app.route('/assign-site')
def assign_site():
    return render_template('assign_site.html')


if __name__ == '__main__':
    app.run(debug=True)
