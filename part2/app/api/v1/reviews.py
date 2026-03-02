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
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace("reviews", description="Review management operations")

review_input_model = api.model(
    "ReviewInput",
    {
        "text": fields.String(required=True),
        "rating": fields.Integer(required=True, min=1, max=5),
        "place_id": fields.String(required=True),
        "user_id": fields.String(required=True),
    },
)

review_update_model = api.model(
    "ReviewUpdate",
    {
        "text": fields.String(required=False),
        "rating": fields.Integer(required=False, min=1, max=5),
    },
)


@api.route("/")
class ReviewList(Resource):
    def get(self):
        reviews = facade.get_all_reviews()
        return [review.to_dict() for review in reviews], 200

    @api.expect(review_input_model)
    @api.response(201, "Review created")
    @api.response(400, "Bad request")
    def post(self):
        data = api.payload or {}
        try:
            review = facade.create_review(data)
        except ValueError as exc:
            api.abort(400, str(exc))
        return review.to_dict(), 201


@api.route("/<string:review_id>")
@api.param("review_id", "Review identifier")
class ReviewResource(Resource):
    @api.response(404, "Review not found")
    def get(self, review_id):
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")
        return review.to_dict(), 200

    @api.expect(review_update_model)
    @api.response(200, "Review updated")
    @api.response(404, "Review not found")
    @api.response(400, "Bad request")
    def put(self, review_id):
        data = api.payload or {}
        try:
            review = facade.update_review(review_id, data)
        except ValueError as exc:
            api.abort(400, str(exc))
        if not review:
            api.abort(404, "Review not found")
        return review.to_dict(), 200

    @api.response(204, "Review deleted")
    @api.response(404, "Review not found")
    def delete(self, review_id):
        deleted = facade.delete_review(review_id)
        if not deleted:
            api.abort(404, "Review not found")
        return "", 204
