-- HBnB Project SQL Schema and Initial Data
-- Drop tables if they exist (for testing purposes)
DROP TABLE IF EXISTS place_amenities CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS places CASCADE;
DROP TABLE IF EXISTS amenities CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Amenities table
CREATE TABLE amenities (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Places table
CREATE TABLE places (
    id UUID PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL CHECK (price > 0),
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude >= -90.0 AND latitude <= 90.0),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude >= -180.0 AND longitude <= 180.0),
    max_guests INTEGER NOT NULL DEFAULT 1 CHECK (max_guests >= 1),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews table
CREATE TABLE reviews (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    place_id UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL CHECK (LENGTH(comment) >= 10 AND LENGTH(comment) <= 500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Place-Amenities junction table
CREATE TABLE place_amenities (
    place_id UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    amenity_id UUID NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (place_id, amenity_id)
);

-- Insert initial admin user
INSERT INTO users (id, first_name, last_name, email, password, is_admin)
VALUES ('00000000-0000-0000-0000-000000000001', 'Admin', 'User', 'admin@hbnb.com', 'admin_hashed_password', TRUE);

-- Insert initial amenities
INSERT INTO amenities (id, name, description) VALUES
    ('00000000-0000-0000-0000-000000000101', 'Wi-Fi', 'Wireless Internet access'),
    ('00000000-0000-0000-0000-000000000102', 'Parking', 'Private parking spot'),
    ('00000000-0000-0000-0000-000000000103', 'Pool', 'Swimming pool'),
    ('00000000-0000-0000-0000-000000000104', 'Air Conditioning', 'AC in all rooms');

-- Example CRUD operations (for testing)
-- CREATE: Insert a place
-- INSERT INTO places (id, owner_id, title, description, price, latitude, longitude, max_guests, is_available)
-- VALUES ('00000000-0000-0000-0000-000000001001', '00000000-0000-0000-0000-000000000001', 'Cozy Loft', 'A nice place', 120.00, 48.8566, 2.3522, 2, TRUE);

-- READ: Select all places
-- SELECT * FROM places;

-- UPDATE: Change price
-- UPDATE places SET price = 150.00 WHERE id = '00000000-0000-0000-0000-000000001001';

-- DELETE: Remove a review
-- DELETE FROM reviews WHERE id = 'some-review-uuid';
