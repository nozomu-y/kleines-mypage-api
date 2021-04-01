from flask import jsonify, make_response, request, Blueprint
from models import Profiles
from routes.auth import login_required

profile = Blueprint('profile', __name__)


@profile.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def get_profile(_, user_id):
    query = Profiles.select(
        Profiles.user_id,
        Profiles.last_name,
        Profiles.first_name,
        Profiles.name_kana,
        Profiles.grade,
        Profiles.part
    ).where(Profiles.user_id == user_id)
    part_full = ""
    if query[0].part == "S":
        part_full = "Soprano"
    elif query[0].part == "A":
        part_full = "Alto"
    elif query[0].part == "T":
        part_full = "Tenor"
    elif query[0].part == "B":
        part_full = "Bass"
    result = {
        "user_id": query[0].user_id,
        "last_name": query[0].last_name,
        "first_name": query[0].first_name,
        "name_kana": query[0].name_kana,
        "grade": query[0].grade,
        "part": query[0].part,
        "part_full": part_full
    }
    return make_response(jsonify(result))
