from flask import request
from flask_restx import Namespace, Resource

from app.services.facade import facade

api = Namespace("reviews", description="Review operations")


@api.route("/")
class ReviewsCollection(Resource):
    def get(self):
        return [facade.serialize_review(review) for review in facade.list_reviews()], 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        try:
            review = facade.create_review(payload)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return facade.serialize_review(review), 201


@api.route("/<string:review_id>")
class ReviewItem(Resource):
    def get(self, review_id: str):
        review = facade.get_review(review_id)
        if review is None:
            return {"error": "Review not found"}, 404
        return facade.serialize_review(review), 200

    def put(self, review_id: str):
        payload = request.get_json(silent=True) or {}
        try:
            review = facade.update_review(review_id, payload)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        if review is None:
            return {"error": "Review not found"}, 404
        return facade.serialize_review(review), 200

    def delete(self, review_id: str):
        deleted = facade.delete_review(review_id)
        if not deleted:
            return {"error": "Review not found"}, 404
        return "", 204