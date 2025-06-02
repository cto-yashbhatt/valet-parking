-- Initialize the database with any required setup
-- This file is executed when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- You can add any initial data or schema modifications here
-- For example, creating indexes, initial admin users, etc.

-- Note: Django migrations will handle the main schema creation
