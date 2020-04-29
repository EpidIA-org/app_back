import os
# import sys
# sys.path.append(os.path.abspath(__file__))
from flask import Flask, render_template, jsonify

from config import config
from libs.blueprints.api import api_bp
from libs.blueprints.ephad import ephad_bp
from libs.blueprints.api_simu import api_simu
from libs.blueprints.api_insee import api_insee_bp
from libs.blueprints.api_predictions import predictor_bp

app = Flask(__name__) # Create the Flask App

# Register the blueprints to use
app.register_blueprint(api_bp)
app.register_blueprint(ephad_bp)
app.register_blueprint(api_simu)
app.register_blueprint(api_insee_bp)
app.register_blueprint(predictor_bp)


# Generate the configuration object 
ENV = os.environ.get('ENVIRONMENT').lower()
app.config.from_object(config[ENV])

# To launch on DEBUG MODE
if app.config['DEBUG']:
    # Handle CORS request in local(debug) mode
    # CORS is handled automatically by Azure Web Services
    from flask_cors import CORS
    CORS(app, resources={r'/*': {'origins': '*'}}) # Allow any origin

    # Add CORS headers in request
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                                'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                                'GET,PUT,POST,DELETE')

        return response

# Setup app for testing
if app.config['TESTING']: 
    @app.before_first_request
    def initialize_app():
        pass


# Main Route
@app.route('/', methods=['GET', 'POST'])
def main():
    return jsonify({
        'message': 'CovidIA API',
        'version': os.environ.get('API_VERSION', None),
        'status': os.environ.get('ENVIRONMENT', None)
    })

