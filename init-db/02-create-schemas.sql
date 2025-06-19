-- Creating schemas for data organization
-- Connect to the main database
\c theblogs;

-- Schema for the main application
CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION postgres;

-- Set default schema for users
ALTER DATABASE theblogs SET search_path TO app, public;

-- Display information about schemas
\dn