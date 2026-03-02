from __future__ import annotations

from typing import Any

from app.models.entities import Amenity, Place, Review, User


class HBnBFacade:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.amenities: dict[str, Amenity] = {}
        self.places: dict[str, Place] = {}
        self.reviews: dict[str, Review] = {}

    def create_user(self, data: dict[str, Any]) -> User:
        user = User(**data)
        self.users[user.id] = user
        return user

    def list_users(self) -> list[User]:
        return list(self.users.values())

    def get_user(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    def create_amenity(self, data: dict[str, Any]) -> Amenity:
        amenity = Amenity(**data)
        self.amenities[amenity.id] = amenity
        return amenity

    def list_amenities(self) -> list[Amenity]:
        return list(self.amenities.values())

    def get_amenity(self, amenity_id: str) -> Amenity | None:
        return self.amenities.get(amenity_id)

    def create_place(self, data: dict[str, Any]) -> Place:
        owner = self.get_user(data.get("owner_id", ""))
        if owner is None:
            raise ValueError("owner_id does not reference an existing user")

        amenity_ids = data.get("amenity_ids", [])
        for amenity_id in amenity_ids:
            if amenity_id not in self.amenities:
                raise ValueError(f"amenity_id '{amenity_id}' was not found")

        place = Place(**data)
        self.places[place.id] = place
        return place

    def list_places(self) -> list[Place]:
        return list(self.places.values())

    def get_place(self, place_id: str) -> Place | None:
        return self.places.get(place_id)

    def create_review(self, data: dict[str, Any]) -> Review:
        user_id = data.get("user_id", "")
        place_id = data.get("place_id", "")
        if user_id not in self.users:
            raise ValueError("user_id does not reference an existing user")
        place = self.get_place(place_id)
        if place is None:
            raise ValueError("place_id does not reference an existing place")

        review = Review(**data)
        self.reviews[review.id] = review
        place.review_ids.append(review.id)
        place.touch()
        return review

    def list_reviews(self) -> list[Review]:
        return list(self.reviews.values())

    def list_reviews_by_place(self, place_id: str) -> list[Review]:
        place = self.get_place(place_id)
        if place is None:
            raise ValueError("place was not found")
        return [self.reviews[review_id] for review_id in place.review_ids if review_id in self.reviews]

    def get_review(self, review_id: str) -> Review | None:
        return self.reviews.get(review_id)

    def update_review(self, review_id: str, data: dict[str, Any]) -> Review | None:
        review = self.get_review(review_id)
        if review is None:
            return None
        text = data.get("text")
        if text is not None:
            if not text.strip():
                raise ValueError("text is required")
            review.text = text
            review.touch()
        return review

    def delete_review(self, review_id: str) -> bool:
        review = self.get_review(review_id)
        if review is None:
            return False
        place = self.get_place(review.place_id)
        if place and review.id in place.review_ids:
            place.review_ids.remove(review.id)
            place.touch()
        del self.reviews[review_id]
        return True

    def serialize_review(self, review: Review) -> dict[str, Any]:
        data = review.to_dict()
        user = self.get_user(review.user_id)
        place = self.get_place(review.place_id)
        data["user"] = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
        } if user else None
        data["place"] = {
            "id": place.id,
            "title": place.title,
        } if place else None
        return data

    def serialize_place(self, place: Place) -> dict[str, Any]:
        data = place.to_dict()
        owner = self.get_user(place.owner_id)
        data["owner"] = {
            "id": owner.id,
            "first_name": owner.first_name,
            "last_name": owner.last_name,
        } if owner else None
        data["amenities"] = [
            amenity.to_dict()
            for amenity_id in place.amenity_ids
            if (amenity := self.get_amenity(amenity_id))
        ]
        data["reviews"] = [
            self.serialize_review(self.reviews[review_id])
            for review_id in place.review_ids
            if review_id in self.reviews
        ]
        return data


facade = HBnBFacade()