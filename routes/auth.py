from flask import jsonify, make_response, request, Blueprint
import jwt
import datetime
import functools
from models import Users
import bcrypt

auth = Blueprint('auth', __name__)


@auth.route('/auth', methods=['POST'])
def index():
    email = request.json['email']
    password = request.json['password']
    query = Users.select(
        Users.user_id,
        Users.email,
        Users.password, Users.status
    ).where(Users.email == email)
    if len(query) == 0:
        result = {"Error": "Email Address Not Found"}
        return make_response(jsonify(result), 400)
    elif len(query) > 1:    # not neccessary, just in case
        result = {"Error": "Duplicate Email Address"}
        return make_response(jsonify(result), 400)
    if not bcrypt.checkpw(password.encode('utf-8'), query[0].password.encode('utf-8')):
        result = {"Error": "Passsword Incorrect"}
        return make_response(jsonify(result), 400)
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    encoded = jwt.encode({'name': query[0].user_id, 'exp': exp}, 'SECRET_KEY', algorithm="HS256")
    result = {'user_id': query[0].user_id, 'token': encoded}
    return make_response(jsonify(result))


def login_required(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization')
        if header is None:
            result = {"Error": "Authorization Header Not Found"}
            return make_response(jsonify(result), 400)
        try:
            _, token = header.split()
        except ValueError:
            result = {"Error": "Token Not Valid"}
            return make_response(jsonify(result), 400)
        try:
            decoded = jwt.decode(token, 'SECRET_KEY', algorithms='HS256')
            user_id = decoded['name']
        except jwt.DecodeError:
            result = {"Error": "Token Not Valid"}
            return make_response(jsonify(result), 400)
        except jwt.ExpiredSignatureError:
            result = {"Error": "Token Expired"}
            return make_response(jsonify(result), 400)
        return method(user_id, *args, **kwargs)
    return wrapper
