from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services import facade

api = Namespace('places', description='Place operations')

# Model for input data validation (POST / PUT)
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'amenities': fields.List(fields.String, required=False, description="List of amenities ID's")
})


@api.route('/')
class PlaceList(Resource):

    @jwt_required()
    @api.expect(place_model, validate=True)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    def post(self):
        """Register a new place"""
        current = get_jwt()
        is_admin = current.get('is_admin', False)
        user_id = get_jwt_identity()

        place_data = api.payload
        # Ensure regular users can only create places they own
        if not is_admin and place_data.get('owner_id') != user_id:
            return {'error': 'Unauthorized action'}, 403

        # api.payload contains the JSON sent by the client

        # Check that the place creation method is available in the facade
        create_place_fn = getattr(facade, "create_place", None)
        if create_place_fn is None:
            # Feature not yet implemented in the service/facade layer
            return {'error': 'Place creation not implemented in service layer'}, 501

        try:
            new_place = create_place_fn(place_data)
            # The facade validates owner_id, price, latitude, longitude
            # and raises ValueError if something is invalid
        except ValueError as e:
            return {'message': str(e)}, 400
            # Return the error with a 400 Bad Request code

        return {
            'id': new_place.id,
            'title': new_place.title,
            'description': new_place.description,
            'price': new_place.price,
            'latitude': new_place.latitude,
            'longitude': new_place.longitude,
            'owner_id': new_place.owner.id
            # Return the owner id, not the full object
        }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        if not hasattr(facade, 'get_all_places'):
            # The method is not yet implemented in the facade
            return {'error': 'Listing places is not implemented in the service layer'}, 501
        places = facade.get_all_places()
        # get_all_places() returns a list of all Place objects

        return [
            {
                'id': place.id,
                'title': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude
                # The list returns only essential information
                # Full details are available via GET /<place_id>
            }
            for place in places
            # List comprehension: transforms each Place into a dict
        ], 200


@api.route('/<place_id>')
class PlaceResource(Resource):

    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID including owner and amenities"""
        try:
            place = facade.get_place(place_id)
        except NotImplementedError:
            # The place retrieval service is not yet implemented
            return {'error': 'Place retrieval not implemented'}, 501
        # get_place() returns None if the place does not exist

        if not place:
            api.abort(404, 'Place not found')

        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                # Return the full owner object (not just the id)
                # The specification requires first_name, last_name, email
                'id': place.owner.id,
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name,
                'email': place.owner.email
            },
            'amenities': [
                # Return the full list of amenities (id + name)
                {
                    'id': amenity.id,
                    'name': amenity.name
                }
                for amenity in place.amenities
                # List comprehension: transforms each Amenity into a dict
            ]
        }, 200

    @jwt_required()
    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information"""
        current = get_jwt()
        is_admin = current.get('is_admin', False)
        user_id = get_jwt_identity()

        try:
            place = facade.get_place(place_id)
        except NotImplementedError:
            return {'error': 'Place retrieval not implemented'}, 501

        if not place:
            return {'message': 'Place not found'}, 404

        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        place_data = api.payload
        # api.payload contains the JSON sent by the client

        try:
            updated_place = facade.update_place(place_id, place_data)
            # update_place() returns None if the place does not exist
        except ValueError as e:
            return {'message': str(e)}, 400

        if not updated_place:
            return {'message': 'Place not found'}, 404

        return {'message': 'Place updated successfully'}, 200

    @jwt_required()
    @api.response(200, 'Place deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    def delete(self, place_id):
        """Delete a place"""
        current = get_jwt()
        is_admin = current.get('is_admin', False)
        user_id = get_jwt_identity()

        try:
            place = facade.get_place(place_id)
        except NotImplementedError:
            return {'error': 'Place retrieval not implemented'}, 501

        if not place:
            return {'message': 'Place not found'}, 404

        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        facade.place_repo.delete(place_id)
        return {'message': 'Place deleted successfully'}, 200
