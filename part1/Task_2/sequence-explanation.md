# Sequence Diagrams - API Calls Explanation

## Overview
This document explains the interaction flow for four key API operations in the HBnB application. Each sequence diagram illustrates how different layers communicate to fulfill user requests.

---

## 1. User Registration

### Purpose
Allows a new user to create an account on the platform.

### API Endpoint
**POST /users**

### Request Data
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Flow Description

1. **User → API**: User submits registration data via POST request
2. **API → Facade**: API calls `createUser()` with the user data
3. **Facade → UserModel**: Facade validates the data (email format, password strength)
4. **UserModel → Facade**: Returns validation confirmation
5. **Facade → UserModel**: Creates a new User instance with validated data
6. **UserModel → Repository**: Calls `save()` to persist the user
7. **Repository → Database**: Executes INSERT query to add user to database
8. **Database → Repository**: Confirms successful insertion with user_id
9. **Repository → UserModel**: Confirms user has been saved
10. **UserModel → Facade**: Returns the complete User object with generated id
11. **Facade → API**: Returns success response
12. **API → User**: Sends HTTP 201 Created with user details

### Key Validations
- Email format validation
- Password strength requirements
- Unique email constraint (checked at database level)

### Response
**201 Created**
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "email": "user@example.com",
  "created_at": "2024-02-08T10:30:00Z"
}
```

---

## 2. Place Creation

### Purpose
Allows an authenticated user to create a new place listing.

### API Endpoint
**POST /places**

### Request Data
```json
{
  "title": "Cozy Paris Apartment",
  "description": "Beautiful 2-bedroom apartment in central Paris",
  "price": 150.00,
  "latitude": 48.8566,
  "longitude": 2.3522,
  "owner_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

### Flow Description

1. **User → API**: User submits place data via POST request
2. **API → Facade**: API calls `createPlace()` with place data
3. **Facade → PlaceModel**: Facade validates data (title, price, coordinates)
4. **PlaceModel → Facade**: Returns validation confirmation
5. **Facade → Repository**: Verifies that the owner (user) exists
6. **Repository → Database**: Queries users table to verify owner_id
7. **Database → Repository**: Returns user record
8. **Repository → Facade**: Confirms user exists
9. **Facade → PlaceModel**: Creates new Place instance
10. **PlaceModel → Repository**: Calls `save()` to persist the place
11. **Repository → Database**: Executes INSERT query
12. **Database → Repository**: Confirms insertion with place_id
13. **Repository → PlaceModel**: Confirms place has been saved
14. **PlaceModel → Facade**: Returns complete Place object
15. **Facade → API**: Returns success response
16. **API → User**: Sends HTTP 201 Created with place details

### Key Validations
- Title not empty
- Price is positive number
- Valid geographic coordinates
- Owner (user_id) exists in database

### Response
**201 Created**
```json
{
  "id": "a3bb189e-8bf9-3888-9912-ace4e6543002",
  "title": "Cozy Paris Apartment",
  "price": 150.00,
  "owner_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

---

## 3. Review Submission

### Purpose
Allows a user to submit a review for a place they visited.

### API Endpoint
**POST /reviews**

### Request Data
```json
{
  "text": "Amazing stay! Clean and comfortable.",
  "rating": 5,
  "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "place_id": "a3bb189e-8bf9-3888-9912-ace4e6543002"
}
```

### Flow Description

1. **User → API**: User submits review data via POST request
2. **API → Facade**: API calls `createReview()` with review data
3. **Facade → Repository**: Verifies that the place exists
4. **Repository → Database**: Queries places table
5. **Database → Repository**: Returns place record
6. **Repository → Facade**: Confirms place exists
7. **Facade → ReviewModel**: Validates rating value (1-5 range)
8. **ReviewModel → Facade**: Returns validation confirmation
9. **Facade → ReviewModel**: Creates new Review instance
10. **ReviewModel → Repository**: Calls `save()` to persist the review
11. **Repository → Database**: Executes INSERT query
12. **Database → Repository**: Confirms insertion with review_id
13. **Repository → ReviewModel**: Confirms review has been saved
14. **ReviewModel → Facade**: Returns complete Review object
15. **Facade → API**: Returns success response
16. **API → User**: Sends HTTP 201 Created with review details

### Key Validations
- Rating must be between 1 and 5
- Text not empty
- Place (place_id) must exist
- User (user_id) must exist
- Optional: User cannot review the same place twice

### Response
**201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Amazing stay! Clean and comfortable.",
  "rating": 5,
  "place_id": "a3bb189e-8bf9-3888-9912-ace4e6543002"
}
```

---

## 4. Fetching a List of Places

### Purpose
Retrieves a filtered list of available places based on search criteria.

### API Endpoint
**GET /places**

### Query Parameters
```
?location=Paris&max_price=200
```

### Flow Description

1. **User → API**: User sends GET request with optional filters
2. **API → Facade**: API calls `getPlaces()` with criteria
3. **Facade → Repository**: Calls `findAll()` with filter parameters
4. **Repository → Database**: Executes SELECT query with WHERE clause
5. **Database → Repository**: Returns list of matching place records
6. **Repository → Facade**: Returns array of Place objects
7. **Facade → Facade**: Formats data for response (optional processing)
8. **Facade → API**: Returns list of places
9. **API → User**: Sends HTTP 200 OK with places array

### Query Building
The Repository dynamically builds the SQL query based on provided filters:
```sql
SELECT * FROM places 
WHERE location LIKE '%Paris%' 
AND price <= 200
```

### Key Features
- Supports multiple filter criteria
- Returns empty array if no matches found
- Can include pagination (limit, offset)
- Results can be sorted by price, rating, etc.

### Response
**200 OK**
```json
[
  {
    "id": "a3bb189e-8bf9-3888-9912-ace4e6543002",
    "title": "Cozy Paris Apartment",
    "price": 150.00
  },
  {
    "id": "b4cc290f-9cf0-4999-a023-bdf5f7654113",
    "title": "Paris Studio",
    "price": 120.00
  }
]
```

---

## Common Patterns Across All Diagrams

### Layer Interaction Flow
All API calls follow the same general pattern:
```
User → API → Facade → Model/Repository → Database → (reverse flow)
```

### Error Handling
Although not shown in the diagrams, each step can return errors:
- **API Layer**: 400 Bad Request (invalid input)
- **Facade/Model**: Validation errors
- **Repository**: 404 Not Found (resource doesn't exist)
- **Database**: 500 Internal Server Error (connection issues)

### Facade Pattern Benefits
The Facade centralizes business logic and provides:
- Single entry point for API layer
- Consistent validation and error handling
- Abstraction of complex operations
- Easier testing and maintenance

### Database Operations
- **Create operations**: Use INSERT queries
- **Read operations**: Use SELECT queries
- **Foreign key validation**: Ensures referential integrity

---

## Technical Notes

### Asynchronous vs Synchronous
These diagrams show synchronous operations (blocking calls). In production, some operations might be asynchronous for better performance.

### Transaction Management
Create operations (User, Place, Review) should be wrapped in database transactions to ensure data consistency.

### Caching
For the "Fetching Places" operation, results could be cached to improve performance for repeated queries.

### Authentication
In a real implementation, all endpoints except User Registration would require authentication tokens (not shown in diagrams for clarity).

---

## Conclusion

These sequence diagrams illustrate the complete request-response cycle for key operations in the HBnB application. The consistent layered architecture ensures:
- Clear separation of concerns
- Maintainable and testable code
- Scalable design
- Predictable behavior across all API endpoints
