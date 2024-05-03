from flask import Flask, render_template,redirect, jsonify
from flask_socketio import SocketIO, emit
from upload import csv_blueprint
from assets_redirect import redirects_blueprint
from lookup import lookup_blueprint
import subprocess

app = Flask(
    __name__
    )
SocketIO = SocketIO(app)

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

@app.route('/interactive-shell')
def interactive_shell():
    return render_template('interactive_shell.html')

@app.route('/interactive_shell_lib.html')
def interactive_shell_lib():
    return render_template('interactive_shell_lib.html')

@SocketIO.on('python_command')
def handle_python_command(command):
    # Execute the Python command and emit the output
    output = execute_python_command(command)
    emit('output', output)

def execute_python_command(command):
    try:
        # Execute the Python script using subprocess.Popen
        process = subprocess.Popen(['python', '/app/src_backend/main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Check if there is any error
        if stderr:
            return f"Error executing script: {stderr.decode('utf-8')}"
        else:
            return f"Output: {stdout.decode('utf-8')}"
    except Exception as e:
        return f"Error executing script: {e}"


if __name__ == '__main__':
    socketio.run(app)
