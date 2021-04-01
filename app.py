from flask import Flask, jsonify, make_response
from routes.auth import auth
from routes.profile import profile

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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
