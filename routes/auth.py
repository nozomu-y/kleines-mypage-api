from flask import request
from flask_restx import Resource, fields, Namespace
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

api = Namespace('auth', description="Authentication")

auth_request = api.model('authentication_request', {
    'email': fields.String(default='example@gmail.com'),
    'password': fields.String(default='password')
})
auth_response = api.model('authentication_response', {
    'token': fields.String(default='JSON Web Token'),
    'user_id': fields.Integer,
    'role': fields.String,
    'status': fields.String
})


@api.route('')
class Index(Resource):
    @api.marshal_with(auth_response)
    @api.doc(body=auth_request)
    def post(self):
        email = request.json['email']
        password = request.json['password']
        query_user = Users.select(
            Users.user_id,
            Users.email,
            Users.password,
            Users.status
        ).where(Users.email == email)
        if len(query_user) == 0:
            result = "Passsword or Email Incorrect"
            return api.abort(400, result)
        elif len(query_user) > 1:    # not neccessary, just in case
            result = "Duplicate Email Address"
            return api.abort(400, result)
        if query_user[0].status == 'RESIGNED':
            result = "Login of Resigned User Not Allowed"
            return api.abort(400, result)
        script = "php -r 'echo password_verify(\"{0}\",\"{1}\") ? \"true\" : \"false\";'".format(
            password, query_user[0].password.replace('$', '\$'))
        ret = subprocess.Popen([script], stdout=subprocess.PIPE, shell=True)
        (out, _) = ret.communicate()
        if out.decode('utf-8') != "true":
            result = "Passsword or Email Incorrect"
            return api.abort(400, result)
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
        result = {'user_id': query_user[0].user_id,
                  'token': encoded,
                  'role': admin_role,
                  'status': query_user[0].status}
        return result


def login_required(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization')
        if header is None:
            result = "Authorization Header Not Found"
            return api.abort(400, result)
        try:
            _, token = header.split()
        except ValueError:
            result = "Token Not Valid"
            return api.abort(400, result)
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms='HS256')
            user_id = decoded['name']
        except jwt.DecodeError:
            result = "Token Not Valid"
            return api.abort(400, result)
        except jwt.ExpiredSignatureError:
            result = "Token Expired"
            return api.abort(400, result)
        return method(*args, user_id, **kwargs)
    return wrapper
