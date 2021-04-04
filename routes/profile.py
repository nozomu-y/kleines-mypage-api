from flask import jsonify, make_response, request, Blueprint
from models import Profiles, Users, AccountingRecords, IndividualAccountingRecords
from routes.auth import login_required
import operator
from functools import reduce
from peewee import fn

profile = Blueprint('profile', __name__)


@profile.route('/profile', methods=['GET'])
@login_required
def get_profiles(_):
    status_list = []
    if len(request.args.getlist('status')) == 0:
        for val in ['PRESENT', 'ABSENT', 'RESIGNED']:
            status_list.append(Users.status == val)
    else:
        for val in request.args.getlist('status'):
            status_list.append(Users.status == val)
    expr = reduce(operator.or_, status_list)
    if len(request.args.getlist('part')) != 0:
        expr = reduce(operator.and_, [expr, (Profiles.part == request.args.get('part'))])
    if len(request.args.getlist('grade')) != 0:
        expr = reduce(operator.and_, [expr, (Profiles.grade == request.args.get('grade'))])
    query = Profiles.select(
        Profiles.user_id,
        Profiles.last_name,
        Profiles.first_name,
        Profiles.name_kana,
        Profiles.grade,
        Profiles.part,
        Users.status,
        fn.IF(Profiles.part == 'S', 'Soprano', fn.IF(Profiles.part == 'A', 'Alto', fn.IF(Profiles.part == 'T', 'Tenor', fn.IF(Profiles.part == 'B', 'Bass', '')))).alias('part_full')
    ).join(Users, on=(Profiles.user_id == Users.user_id).alias('Users')).where(expr)
    result = []
    if len(query) == 0:
        result = {"Error": "No Record Found"}
        return make_response(jsonify(result), 400)
    for user in query:
        result.append({
            "user_id": user.user_id,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "name_kana": user.name_kana,
            "grade": user.grade,
            "part": user.part,
            "part_full": user.part_full,
            "status": user.Users.status
        })
    return make_response(jsonify(result))


@profile.route('/profile/me', methods=['GET'])
@login_required
def get_my_profile(user_id):
    query = Profiles.select(
        Profiles.user_id,
        Profiles.last_name,
        Profiles.first_name,
        Profiles.name_kana,
        Profiles.grade,
        Profiles.part,
        Users.status,
        Users.email,
        AccountingRecords.select(fn.IFNULL(fn.SUM(AccountingRecords.price), 0)).where((AccountingRecords.user_id == Profiles.user_id) & AccountingRecords.datetime.is_null()).alias('delinquent'),
        IndividualAccountingRecords.select(fn.IFNULL(fn.SUM(IndividualAccountingRecords.price), 0)).where((IndividualAccountingRecords.user_id == Profiles.user_id)).alias('individual_accounting_total'),
        fn.IF(Profiles.part == 'S', 'Soprano', fn.IF(Profiles.part == 'A', 'Alto', fn.IF(Profiles.part == 'T', 'Tenor', fn.IF(Profiles.part == 'B', 'Bass', '')))).alias('part_full')
    ).join(Users, on=(Profiles.user_id == Users.user_id).alias('Users')).where(Profiles.user_id == user_id)
    if len(query) == 0:
        result = {"Error": "No Record Found"}
        return make_response(jsonify(result), 400)
    result = {
        "user_id": query[0].user_id,
        "last_name": query[0].last_name,
        "first_name": query[0].first_name,
        "name_kana": query[0].name_kana,
        "grade": query[0].grade,
        "part": query[0].part,
        "part_full": query[0].part_full,
        "email": query[0].Users.email,
        "status": query[0].Users.status,
        "delinquent": int(query[0].delinquent),
        "individual_accounting_total": int(query[0].individual_accounting_total)
    }
    return make_response(jsonify(result))


@ profile.route('/profile/<int:user_id>', methods=['GET'])
@ login_required
def get_profile_by_user_id(_, user_id):
    query = Profiles.select(
        Profiles.user_id,
        Profiles.last_name,
        Profiles.first_name,
        Profiles.name_kana,
        Profiles.grade,
        Profiles.part,
        Users.status,
        fn.IF(Profiles.part == 'S', 'Soprano', fn.IF(Profiles.part == 'A', 'Alto', fn.IF(Profiles.part == 'T', 'Tenor', fn.IF(Profiles.part == 'B', 'Bass', '')))).alias('part_full')
    ).join(Users, on=(Profiles.user_id == Users.user_id).alias('Users')).where(Profiles.user_id == user_id)
    if len(query) == 0:
        result = {"Error": "No Record Found"}
        return make_response(jsonify(result), 400)
    result = {
        "user_id": query[0].user_id,
        "last_name": query[0].last_name,
        "first_name": query[0].first_name,
        "name_kana": query[0].name_kana,
        "grade": query[0].grade,
        "part": query[0].part,
        "part_full": query[0].part_full,
        "status": query[0].Users.status
    }
    return make_response(jsonify(result))
