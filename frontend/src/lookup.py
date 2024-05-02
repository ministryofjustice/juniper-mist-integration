from flask import Blueprint, current_app, jsonify
import os

lookup_blueprint = Blueprint('lookup_blueprint',__name__)

@lookup_blueprint.route('/data-src', methods=['GET'])
def get_csv_files():
    data_src_dir = '/data_src'
    csv_files = [f for f in os.listdir(data_src_dir) if f.endswith('.csv')]
    return jsonify(csv_files)