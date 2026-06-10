CREATE DATABASE estate;

USE estate;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    phone VARCHAR(30),
    role ENUM('customer','agent','admin'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE properties (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT,
    title VARCHAR(255),
    description TEXT,
    price DECIMAL(12,2),
    city VARCHAR(100),
    address VARCHAR(255),
    bedrooms INT,
    bathrooms INT,
    area INT,
    property_type ENUM('house','apartment','villa','land'),
    status ENUM('available','sold','rented'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (agent_id)
    REFERENCES users(id)
);

CREATE TABLE property_images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    property_id INT,
    image_path VARCHAR(255),

    FOREIGN KEY (property_id)
    REFERENCES properties(id)
);

CREATE TABLE favorites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    property_id INT,

    FOREIGN KEY (user_id)
    REFERENCES users(id),

    FOREIGN KEY (property_id)
    REFERENCES properties(id)
);

CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    property_id INT,
    booking_date DATETIME,
    status ENUM('pending','approved','rejected'),

    FOREIGN KEY(user_id)
    REFERENCES users(id),

    FOREIGN KEY(property_id)
    REFERENCES properties(id)
);