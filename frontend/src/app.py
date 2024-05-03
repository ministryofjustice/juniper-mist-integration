from flask import Flask, render_template,redirect, jsonify, request
from flask_socketio import SocketIO, emit
from upload import csv_blueprint
from assets_redirect import redirects_blueprint
from lookup import lookup_blueprint
import subprocess
import shutil

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
    return render_template('configure_my_session.html')

@app.route('/assign-site')
def assign_site():
    return render_template('assign_site.html')

@app.route('/interactive-shell')
def interactive_shell():
    return render_template('interactive_shell.html')

@app.route('/interactive_shell_lib.html')
def interactive_shell_lib():
    return render_template('interactive_shell_lib.html')

@app.route('/submit', methods=['POST'])
def when_user_submits_setup_csv_and_env_for_session():
    csv_file_name = request.form.get('csv_file')
    env_file_name = request.form.get('env_file')

    if not csv_file_name or not env_file_name:
        return "CSV file name or environment file name missing", 400
    # This will overwrite exsiting sessions if they already exist
    shutil.copyfile('/data_src/' + csv_file_name, '/user_session/current_session.csv')
    shutil.copyfile('/data_src/' + env_file_name, '/user_session/current_session.env')

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
