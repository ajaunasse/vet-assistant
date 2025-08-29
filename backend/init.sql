-- Initialize database for NeuroVet application
-- This file is executed when the MySQL container starts for the first time

-- Ensure the database exists
CREATE DATABASE IF NOT EXISTS neurovet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user if not exists (user is already created by environment variables)
-- GRANT ALL PRIVILEGES ON neurovet_db.* TO 'neurovet'@'%';
-- FLUSH PRIVILEGES;

USE neurovet_db;

-- The tables will be created by Alembic migrations