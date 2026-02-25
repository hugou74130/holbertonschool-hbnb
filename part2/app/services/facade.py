from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ----------------- user operations -----------------
    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_users(self):
        return self.user_repo.get_all()

    def create_user(self, user_data):
        """Create a new user and persist it.

        Raises ValueError for missing fields or duplicate email.
        """
        email = user_data.get('email')
        password = user_data.get('password')
        if not email or not password:
            raise ValueError('email and password are required')
        # check uniqueness
        existing = self.user_repo.get_by_attribute('email', email)
        if existing:
            raise ValueError('email already in use')
        from app.models.user import User
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def update_user(self, user_id, data):
        user = self.get_user(user_id)
        if not user:
            return None
        # prevent email changes through this endpoint
        data = {k: v for k, v in data.items() if k != 'email'}
        user.update(data)
        return user

    # Placeholder method for fetching a place by ID
    def get_place(self, place_id):
        # Logic will be implemented in later tasks
        pass