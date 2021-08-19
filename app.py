from flask import Flask, jsonify, make_response
from flask_restx import Api
import os
from os.path import join, dirname
from dotenv import load_dotenv
from routes import auth, profile

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

APP_ROOT = os.environ.get("APP_ROOT")

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_MASK_SWAGGER'] = False

authorization = {
    'Bearer Token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': '**Value:** Bearer *JWT*'
    }
}

api = Api(app,
          version='1.0',
          title='Kleines Mypage API',
          description='API developed for Kleines Mypage',
          doc='/swagger/',
          prefix='/v1',
          license='GitHub',
          license_url='https://github.com/nozomu-y/kleines-mypage-api',
          authorizations=authorization
          )

api.add_namespace(auth.api)
api.add_namespace(profile.api)


@app.errorhandler(404)
def not_found(error):
    result = {
        "message": "Not Found",
    }
    return make_response(jsonify(result), 404)


if __name__ == '__main__':
    app.run(debug=True)
