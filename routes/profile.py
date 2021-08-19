from flask_restx import Resource, fields, Namespace
from models import Profiles, Users, AccountingRecords, IndividualAccountingRecords
from routes.auth import login_required
import operator
from functools import reduce
from peewee import fn
from conf import const

api = Namespace('profile', description="Profiles")

profile_short_response = api.model('profile_short_response', {
    'user_id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'name_kana': fields.String,
    'grade': fields.Integer,
    'part': fields.String,
    'part_full': fields.String,
    'status': fields.String
})

profile_response = api.model('profile_response', {
    'user_id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'name_kana': fields.String,
    'grade': fields.Integer,
    'part': fields.String,
    'part_full': fields.String,
    'email': fields.String,
    'status': fields.String,
    'delinquent': fields.Integer,
    'individual_accounting_total': fields.Integer
})

profile_request_parser = api.parser()
profile_request_parser.add_argument(
    'status', action='append', help='<i>Avaliable values:</i> %s, %s, %s' % (const.PRESENT, const.ABSENT, const.RESIGNED))
profile_request_parser.add_argument('part', choices=('S', 'A', 'T', 'B'))
profile_request_parser.add_argument('grade', type=int)


@api.route('')
class Index(Resource):
    @api.marshal_with(profile_short_response)
    @api.expect(profile_request_parser)
    @api.doc(security='Bearer Token')
    @login_required
    def get(self, _):
        args = profile_request_parser.parse_args()
        status_list = []
        if args['status'] == None:
            for val in [const.PRESENT, const.ABSENT, const.RESIGNED]:
                status_list.append(Users.status == val)
        else:
            for val in args['status']:
                if val not in [const.PRESENT, const.ABSENT, const.RESIGNED]:
                    result = "Status Name Not Valid"
                    return api.abort(400, result)
                status_list.append(Users.status == val)
        expr = reduce(operator.or_, status_list)
        if args['part'] != None:
            if args['part'] not in ['S', 'A', 'T', 'B']:
                result = "Part Name Not Valid"
                return api.abort(400, result)
            expr = reduce(operator.and_, [expr, (Profiles.part == args['part'])])
        if args['grade'] != None:
            expr = reduce(operator.and_, [expr, (Profiles.grade == args['grade'])])
        query = Profiles.select(
            Profiles.user_id,
            Profiles.last_name,
            Profiles.first_name,
            Profiles.name_kana,
            Profiles.grade,
            Profiles.part,
            Users.status,
            fn.IF(Profiles.part == 'S', 'Soprano', fn.IF(Profiles.part == 'A', 'Alto', fn.IF(
                Profiles.part == 'T', 'Tenor', fn.IF(Profiles.part == 'B', 'Bass', '')))).alias('part_full')
        ).join(Users, on=(Profiles.user_id == Users.user_id).alias('Users')).where(expr)
        # TODO: order results
        result = []
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
        return result


@api.route('/me')
class Me(Resource):
    @api.marshal_with(profile_response)
    @api.doc(security='Bearer Token')
    @login_required
    def get(self, user_id):
        query = Profiles.select(
            Profiles.user_id,
            Profiles.last_name,
            Profiles.first_name,
            Profiles.name_kana,
            Profiles.grade,
            Profiles.part,
            Users.status,
            Users.email,
            AccountingRecords.select(fn.IFNULL(fn.SUM(AccountingRecords.price), 0)).where(
                (AccountingRecords.user_id == Profiles.user_id) & AccountingRecords.datetime.is_null()).alias('delinquent'),
            IndividualAccountingRecords.select(fn.IFNULL(fn.SUM(IndividualAccountingRecords.price), 0)).where(
                (IndividualAccountingRecords.user_id == Profiles.user_id)).alias('individual_accounting_total'),
            fn.IF(Profiles.part == 'S', 'Soprano', fn.IF(Profiles.part == 'A', 'Alto', fn.IF(
                Profiles.part == 'T', 'Tenor', fn.IF(Profiles.part == 'B', 'Bass', '')))).alias('part_full')
        ).join(Users, on=(Profiles.user_id == Users.user_id).alias('Users')).where(Profiles.user_id == user_id)
        if len(query) == 0:
            result = "No Record Found"
            return api.abort(400, result)
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
        return result


@api.route('/<int:user_id>')
@api.param('user_id')
class UserProfile(Resource):
    @api.marshal_with(profile_short_response)
    @api.doc(security='Bearer Token')
    @login_required
    def get(self, _, user_id):
        query = Profiles.select(
            Profiles.user_id,
            Profiles.last_name,
            Profiles.first_name,
            Profiles.name_kana,
            Profiles.grade,
            Profiles.part,
            Users.status,
            fn.IF(Profiles.part == 'S', 'Soprano', fn.IF(Profiles.part == 'A', 'Alto', fn.IF(
                Profiles.part == 'T', 'Tenor', fn.IF(Profiles.part == 'B', 'Bass', '')))).alias('part_full')
        ).join(Users, on=(Profiles.user_id == Users.user_id).alias('Users')).where(Profiles.user_id == user_id)
        if len(query) == 0:
            result = "No Record Found"
            return api.abort(400, result)
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
        return result
