from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_identity

from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST


blp = Blueprint('Users', 'users', description='Operations on users')


@blp.route('/login')
class UserLogin(MethodView):

    @blp.arguments(UserSchema)
    def post(self, parsed_data):
        user = UserModel.query.filter(UserModel.username == parsed_data['username']).first()
        if user and pbkdf2_sha256.verify(parsed_data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        abort(401, message='Invalid credentials.')


@blp.route('/refresh')
class TokenRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        refreshed_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {"access_token": refreshed_token}


@blp.route('/logout')
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}


@blp.route('/register')
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    def post(self, parsed_data):
        if UserModel.query.filter(UserModel.username == parsed_data['username']).first():
            abort(400, message="A user with that username already exits")
        user = UserModel(
            username=parsed_data['username'],
            password=pbkdf2_sha256.hash(parsed_data['password'])
        )
        db.session.add(user)
        db.session.commit()

        return {'message': "User created successfully"}, 201


@blp.route('/user/<int:user_id>')
class User(MethodView):

    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)

    @jwt_required(fresh=True)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {
            "message": "User deleted"
        }
