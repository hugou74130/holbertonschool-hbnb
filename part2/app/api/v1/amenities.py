from flask import request
from flask_restx import Namespace, Resource

from app.services.facade import facade

api = Namespace("amenities", description="Amenity operations")


@api.route("/")
class AmenitiesCollection(Resource):
    def get(self):
        return [amenity.to_dict() for amenity in facade.list_amenities()], 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        try:
            amenity = facade.create_amenity(payload)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return amenity.to_dict(), 201


@api.route("/<string:amenity_id>")
class AmenityItem(Resource):
    def get(self, amenity_id: str):
        amenity = facade.get_amenity(amenity_id)
        if amenity is None:
            return {"error": "Amenity not found"}, 404
        return amenity.to_dict(), 200