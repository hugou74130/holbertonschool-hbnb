from flask import request
from flask_restx import Namespace, Resource

from app.services.facade import facade

api = Namespace("users", description="User operations")


@api.route("/")
class UsersCollection(Resource):
    def get(self):
        return [user.to_dict() for user in facade.list_users()], 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        try:
            user = facade.create_user(payload)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return user.to_dict(), 201


@api.route("/<string:user_id>")
class UserItem(Resource):
    def get(self, user_id: str):
        user = facade.get_user(user_id)
        if user is None:
            return {"error": "User not found"}, 404
        return user.to_dict(), 200