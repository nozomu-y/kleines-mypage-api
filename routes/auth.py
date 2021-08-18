from flask import jsonify, make_response, request, Blueprint
import jwt
import datetime
import functools
from models import Users, Admins
import subprocess
import os
from os.path import join, dirname
from dotenv import load_dotenv
from conf import const

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get("SECRET_KEY")

auth = Blueprint('auth', __name__)


@auth.route('/auth', methods=['POST'])
def index():
    email = request.json['email']
    password = request.json['password']
    query_user = Users.select(
        Users.user_id,
        Users.email,
        Users.password,
        Users.status
    ).where(Users.email == email)
    if len(query_user) == 0:
        result = {"Error": "Email Address Not Found"}
        return make_response(jsonify(result), 400)
    elif len(query_user) > 1:    # not neccessary, just in case
        result = {"Error": "Duplicate Email Address"}
        return make_response(jsonify(result), 400)
    if query_user[0].status == 'RESIGNED':
        result = {"Error": "Login of Resigned User Not Allowed"}
        return make_response(jsonify(result), 400)
    script = "php -r 'echo password_verify(\"{0}\",\"{1}\") ? \"true\" : \"false\";'".format(password, query_user[0].password.replace('$', '\$'))
    ret = subprocess.Popen([script], stdout=subprocess.PIPE, shell=True)
    (out, _) = ret.communicate()
    if out.decode('utf-8') != "true":
        result = {"Error": "Passsword Incorrect"}
        return make_response(jsonify(result), 400)
    # check if user is admin
    query_admin = Admins.select(
        Admins.user_id,
        Admins.role
    ).where(Admins.user_id == query_user[0].user_id)
    if len(query_admin) == 0:
        admin_role = const.GENERAL
    else:
        admin_role = query_admin[0].role
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    encoded = jwt.encode({'name': query_user[0].user_id, 'exp': exp}, SECRET_KEY, algorithm="HS256")
    result = {'user_id': query_user[0].user_id, 'token': encoded, 'role': admin_role, 'status': query_user[0].status}
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
            decoded = jwt.decode(token, SECRET_KEY, algorithms='HS256')
            user_id = decoded['name']
            print(user_id)
        except jwt.DecodeError:
            result = {"Error": "Token Not Valid"}
            return make_response(jsonify(result), 400)
        except jwt.ExpiredSignatureError:
            result = {"Error": "Token Expired"}
            return make_response(jsonify(result), 400)
        return method(user_id, *args, **kwargs)
    return wrapper
