from __future__ import print_function
from flask_restful import reqparse, Resource, Api
from flask import jsonify
from app import app
from app import db
from models import user, account, users_accounts
from werkzeug.security import safe_str_cmp
from flask_jwt import JWT, jwt_required
import sys

api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('email')
parser.add_argument('password')
parser.add_argument('username')
parser.add_argument('domain')
parser.add_argument('newpassword')


class User(Resource):
    @jwt_required()
    def get(self, user_id):
        dbuser = user.User.query.filter_by(id=int(user_id)).first()

        retuser = {
            'email': dbuser.email,
            'hash': dbuser.userhash,
            'slots': dbuser.slots,
        }
        return retuser

    def post(self):
        args = parser.parse_args()
        new_user = user.User(args['email'], '1234')
        retuser = {
            'email': new_user.email,
            'password': new_user.password
        }
        db.session.add(new_user)
        db.session.commit()
        return retuser

    def delete(self, user_id):
        # TODO: implement
        pass

    def put(self, user_id):
        dbuser = user.User.query.filter_by(id=int(user_id)).first()
        args = parser.parse_args()
        # TODO: Check old password

        dbuser.email = args['email']
        dbuser.password = args['newpassword']

        db.session.add(dbuser)
        db.session.commit()
        return {
            'id': dbuser.id,
            'email': dbuser.email,
            'password': dbuser.password}


class Account(Resource):
    @jwt_required()
    def get(self, user_id):
        uarels = users_accounts.UsersAccounts.query.filter_by(
            userid=int(user_id))

        dbaccs = {}
        for uarel in uarels:
            dbacc = account.Account.query.filter_by(
                id=int(uarel.accountid)).first()
            dbaccs[uarel.accountid] = dbacc

        retaccs = {}
        for accid, acc in dbaccs.items():
            retacc = {
                'userid': user_id,
                'account_id': acc.id,
                'username': acc.username,
                'domain': acc.domain
            }
            retaccs[acc.id] = retacc

        return retaccs

    def post(self, user_id):
        args = parser.parse_args()
        new_account = account.Account(args['username'], args['domain'])

        db.session.add(new_account)
        db.session.commit()

        new_ua_rel = users_accounts.UsersAccounts(user_id, new_account.id)
        db.session.add(new_ua_rel)
        print(new_account.id)
        db.session.commit()

        retacc = {
            'userid': user_id,
            'account_id': new_account.id,
            'username': new_account.username,
            'domain': new_account.domain
        }
        return retacc

    def put(self, user_id, acc_id):
        # TODO: stuff
        return {'message': 'not yet implemented'}

    def delete(self, user_id, acc_id):
        # TODO: kill it with fire
        return {'message': 'not yet implemented'}

api.add_resource(User, '/users/<user_id>', '/users')
api.add_resource(Account, '/users/<user_id>/accounts',
                 '/users/<user_id>/accounts/<acc_id>')


def authenticate(username, password):
    dbuser = user.User.query.filter_by(email=username).first()
    if dbuser and safe_str_cmp(dbuser.password,
                               password):
        print('==== pw match ====', file=sys.stderr)
        return dbuser


def identity(payload):
    user_id = payload['identity']
    return user.User.query.filter_by(id=int(user_id)).first()


jwt = JWT(app, authenticate, identity)


@jwt.auth_response_handler
def custom_auth_response_callback(access_token, identity):
    del identity
    return jsonify({'token': 'JWT ' + access_token.decode('utf-8')})


# TODO: disable in production
if __name__ == '__main__':
    app.run(debug=True)
