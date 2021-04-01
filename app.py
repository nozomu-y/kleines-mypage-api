from flask import Flask, jsonify, make_response
from routes.auth import auth
from routes.profile import profile
import os
from os.path import join, dirname
from dotenv import load_dotenv
from werkzeug.routing import Rule

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

APP_ROOT = os.environ.get("APP_ROOT")

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

if APP_ROOT is not None:
    class Custom_Rule(Rule):
        def __init__(self, string, *args, **kwargs):
            if APP_ROOT.endswith('/'):
                prefix_without_end_slash = APP_ROOT.rstrip('/')
            else:
                prefix_without_end_slash = APP_ROOT
            if APP_ROOT.startswith('/'):
                prefix = prefix_without_end_slash
            else:
                prefix = '/' + prefix_without_end_slash
            super(Custom_Rule, self).__init__(prefix + string, *args, **kwargs)
    app.url_rule_class = Custom_Rule

app.register_blueprint(auth)
app.register_blueprint(profile)


@app.errorhandler(404)
def not_found(error):
    result = {
        "error": "Not Found",
        "result": False
    }
    return make_response(jsonify(result), 404)


if __name__ == '__main__':
    app.run()
