# HBnB Application - Architecture Explanation

## Overview
This document explains the three-layer architecture of the HBnB application and how the Facade Pattern facilitates communication between these layers.

---

## Presentation Layer

### Role
The Presentation Layer serves as the interface between users and the application. It handles all incoming HTTP requests and outgoing responses.

### Components
- **API REST**: Exposes RESTful endpoints for client applications
- **Routes/Endpoints**: Defines URL patterns for different operations
  - `/users` - User management
  - `/places` - Place listings management
  - `/reviews` - Review management
  - `/amenities` - Amenity management
- **HTTP Requests**: Processes GET, POST, PUT, DELETE requests from clients

### Responsibilities
- Receive and validate user requests
- Format and return JSON responses
- Handle authentication and authorization
- Route requests to the appropriate business logic through the Facade

---

## Business Logic Layer

### Role
The Business Logic Layer contains the core functionality and rules of the application. It processes data according to business requirements and coordinates operations between the Presentation and Persistence layers.

### Components

#### Facade Pattern
The Facade provides a simplified interface for the Presentation Layer to interact with the Business Logic. It acts as a single entry point, hiding the complexity of the underlying system.

**Key Methods:**
- `createUser()` - Handles user registration with validation
- `createPlace()` - Manages place creation with business rules
- `createReview()` - Processes review submissions with validation
- `manageAmenities()` - Handles amenity operations

#### Models
The core entities that represent the business domain:

- **User**: Represents registered users who can list places or write reviews
  - Attributes: id, email, password, first_name, last_name
  - Methods: register(), login()

- **Place**: Represents properties available for rent
  - Attributes: id, title, description, price, location, owner
  - Methods: add_amenity(), update_details()

- **Review**: Represents user feedback on places
  - Attributes: id, text, rating, user_id, place_id
  - Methods: validate_rating(), submit()

- **Amenity**: Represents facilities and services available at places
  - Attributes: id, name, description
  - Methods: associate_to_place()

### Responsibilities
- Apply business rules and validation
- Coordinate complex operations across multiple entities
- Ensure data integrity before persistence
- Transform data between layers

---

## Persistence Layer

### Role
The Persistence Layer is responsible for data storage and retrieval. It manages all interactions with the database, ensuring data is saved and retrieved correctly.

### Components
- **Repositories**: Data access objects for each entity
  - `UserRepository` - Handles User data operations
  - `PlaceRepository` - Handles Place data operations
  - `ReviewRepository` - Handles Review data operations
  - `AmenityRepository` - Handles Amenity data operations

- **Database Access**: Manages database connections and transactions

- **SQL Queries**: Executes CRUD operations (Create, Read, Update, Delete)

### Responsibilities
- Store entities in the database
- Retrieve data based on queries
- Update existing records
- Delete records when required
- Manage database transactions and ensure data consistency

---

## Facade Pattern Implementation

### Purpose
The Facade Pattern simplifies communication between the Presentation Layer and the Business Logic Layer by providing a unified interface.

### Benefits
1. **Reduced Complexity**: The Presentation Layer doesn't need to know the details of the Business Logic implementation
2. **Loose Coupling**: Changes in the Business Logic don't directly impact the Presentation Layer
3. **Centralized Control**: All business operations go through a single point, making it easier to add logging, security, or caching
4. **Improved Maintainability**: Easier to modify or extend functionality without affecting multiple parts of the system

### How It Works
```
User Request (API) 
    → Facade 
    → Business Logic (Models) 
    → Persistence (Database)
    ← Response flows back through the same path
```

Instead of the API directly calling multiple model classes and repositories, it simply calls the Facade, which orchestrates all necessary operations internally.

---

## Communication Flow Example

**Scenario**: A user creates a new place listing

1. **Presentation Layer**: API receives POST request to `/places`
2. **Facade**: `createPlace()` method is called with place data
3. **Business Logic**: 
   - Validates the place data
   - Checks if the user is authorized
   - Creates a Place object
4. **Persistence Layer**: 
   - `PlaceRepository.save()` stores the place in the database
5. **Response**: Success confirmation flows back through Facade → API → User

---

## Design Decisions

### Why Three Layers?
- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Each layer can be tested independently
- **Scalability**: Layers can be scaled separately based on needs
- **Flexibility**: Easy to swap implementations (e.g., change database without affecting business logic)

### Why Facade Pattern?
- Simplifies the API layer implementation
- Provides a stable interface even when internal implementation changes
- Makes the codebase easier to understand and maintain

---

## Conclusion

This three-layer architecture with the Facade Pattern provides a solid foundation for the HBnB application. It ensures clean separation of concerns, maintainability, and scalability while keeping the codebase organized and understandable.
