from __future__ import annotations

from typing import Any

from app.models.entities import Amenity, Place, Review, User


from app.persistence.repository import InMemoryRepository


class HBnBFacade:
    """Business logic facade backed by repositories.

    All methods previously implemented with in-memory dicts have been
    updated to use :class:`InMemoryRepository`.  This centralizes data
    access and makes it easier to swap out the storage implementation in
    the future.
    """

    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # --- user operations -------------------------------------------------

    def create_user(self, user_data: dict[str, Any]) -> User:
        """Create a new user and persist it.

        Raises ValueError for missing fields or duplicate email.
        """
        email = user_data.get("email")
        password = user_data.get("password")
        if not email or not password:
            raise ValueError("email and password are required")
        existing = self.user_repo.get_by_attribute("email", email)
        if existing:
            raise ValueError("email already in use")
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def list_users(self) -> list[User]:
        return self.user_repo.get_all()

    def get_user(self, user_id: str) -> User | None:
        return self.user_repo.get(user_id)

    def update_user(self, user_id: str, data: dict[str, Any]) -> User | None:
        user = self.get_user(user_id)
        if not user:
            return None
        # email should not be changed through this method
        data = {k: v for k, v in data.items() if k != "email"}
        user.update(data)
        return user

    # --- amenity operations ------------------------------------------------

    def create_amenity(self, data: dict[str, Any]) -> Amenity:
        amenity = Amenity(**data)
        self.amenity_repo.add(amenity)
        return amenity

    def list_amenities(self) -> list[Amenity]:
        return self.amenity_repo.get_all()

    def get_amenity(self, amenity_id: str) -> Amenity | None:
        return self.amenity_repo.get(amenity_id)

    # --- place operations --------------------------------------------------

    def create_place(self, data: dict[str, Any]) -> Place:
        owner = self.get_user(data.get("owner_id", ""))
        if owner is None:
            raise ValueError("owner_id does not reference an existing user")

        amenity_ids = data.get("amenity_ids", [])
        for amenity_id in amenity_ids:
            if self.get_amenity(amenity_id) is None:
                raise ValueError(f"amenity_id '{amenity_id}' was not found")

        place = Place(**data)
        self.place_repo.add(place)
        return place

    def list_places(self) -> list[Place]:
        return self.place_repo.get_all()

    def get_place(self, place_id: str) -> Place | None:
        return self.place_repo.get(place_id)

    # --- review operations -------------------------------------------------

    def create_review(self, data: dict[str, Any]) -> Review:
        user_id = data.get("user_id", "")
        place_id = data.get("place_id", "")
        if self.get_user(user_id) is None:
            raise ValueError("user_id does not reference an existing user")
        place = self.get_place(place_id)
        if place is None:
            raise ValueError("place_id does not reference an existing place")

        review = Review(**data)
        self.review_repo.add(review)
        # update the place object as before
        place.review_ids.append(review.id)
        place.touch()
        return review

    def list_reviews(self) -> list[Review]:
        return self.review_repo.get_all()

    def list_reviews_by_place(self, place_id: str) -> list[Review]:
        place = self.get_place(place_id)
        if place is None:
            raise ValueError("place was not found")
        return [
            self.review_repo.get(review_id)
            for review_id in place.review_ids
            if self.review_repo.get(review_id)
        ]

    def get_review(self, review_id: str) -> Review | None:
        return self.review_repo.get(review_id)

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
        self.review_repo.delete(review_id)
        return True

    # --- serialization helpers -------------------------------------------

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
            self.serialize_review(self.review_repo.get(review_id))
            for review_id in place.review_ids
            if self.review_repo.get(review_id)
        ]
        return data


# single shared facade instance
facade = HBnBFacade()
