from flask import jsonify, make_response, request, Blueprint
from models import Profiles, Users
from routes.auth import login_required
import operator
from functools import reduce

profile = Blueprint('profile', __name__)


def get_part_full(part):
    part_full = ""
    if part == "S":
        part_full = "Soprano"
    elif part == "A":
        part_full = "Alto"
    elif part == "T":
        part_full = "Tenor"
    elif part == "B":
        part_full = "Bass"
    return part_full


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
        Users.status
    ).join(Users, on=(Profiles.user_id == Users.user_id).alias('Users')).where(expr)
    result = []
    for user in query:
        part_full = get_part_full(user.part)
        result.append({
            "user_id": user.user_id,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "name_kana": user.name_kana,
            "grade": user.grade,
            "part": user.part,
            "part_full": part_full,
            "status": user.Users.status
        })
    return make_response(jsonify(result))


@profile.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def get_profile_by_user_id(_, user_id):
    query = Profiles.select(
        Profiles.user_id,
        Profiles.last_name,
        Profiles.first_name,
        Profiles.name_kana,
        Profiles.grade,
        Profiles.part,
        Users.status
    ).join(Users, on=(Profiles.user_id == Users.user_id).alias('Users')).where(Profiles.user_id == user_id)
    part_full = get_part_full(query[0].part)
    result = {
        "user_id": query[0].user_id,
        "last_name": query[0].last_name,
        "first_name": query[0].first_name,
        "name_kana": query[0].name_kana,
        "grade": query[0].grade,
        "part": query[0].part,
        "part_full": part_full,
        "status": query[0].Users.status
    }
    return make_response(jsonify(result))
