
--DB creation
CREATE DATABASE contacts_db;
-- This script sets up the database schema for the Contact Manager application.
-- It creates the 'users' and 'contacts' tables with appropriate constraints.

-- Drop tables in reverse order of dependency to avoid foreign key errors.
-- The CASCADE option will automatically remove any dependent objects.
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS users CASCADE;

-- Create the 'users' table to store user information.
CREATE TABLE users (
    id SERIAL PRIMARY KEY, -- Auto-incrementing integer for the primary key.
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL, -- Usernames must be unique.
    email VARCHAR(120) UNIQUE NOT NULL,    -- Emails must be unique.
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Records the time of user creation.
);

-- Create the 'contacts' table to store contact details.
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY, -- Auto-incrementing integer for the primary key.
    user_id INTEGER NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(120),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Records the time of contact creation.

    -- Define the foreign key relationship to the 'users' table.
    -- ON DELETE CASCADE ensures that if a user is deleted, all their contacts are also deleted.
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- Add an index on the user_id column in the contacts table for faster lookups of a user's contacts.
CREATE INDEX idx_contacts_user_id ON contacts(user_id);
