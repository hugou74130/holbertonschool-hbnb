from flask import request
from flask_restx import Namespace, Resource

from app.services.facade import facade

api = Namespace("places", description="Place operations")


@api.route("/")
class PlacesCollection(Resource):
    def get(self):
        return [facade.serialize_place(place) for place in facade.list_places()], 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        try:
            place = facade.create_place(payload)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return facade.serialize_place(place), 201


@api.route("/<string:place_id>")
class PlaceItem(Resource):
    def get(self, place_id: str):
        place = facade.get_place(place_id)
        if place is None:
            return {"error": "Place not found"}, 404
        return facade.serialize_place(place), 200


@api.route("/<string:place_id>/reviews")
class PlaceReviewCollection(Resource):
    def get(self, place_id: str):
        try:
            reviews = facade.list_reviews_by_place(place_id)
        except ValueError:
            return {"error": "Place not found"}, 404
        return [facade.serialize_review(review) for review in reviews], 200