-- Delete existing tables to apply the new structure
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_saved_jobs;

-- Create the new, more detailed users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    age INTEGER,
    city TEXT,
    college TEXT,
    degree TEXT,
    skills TEXT -- Will store a comma-separated list of skills
);

-- The saved jobs table remains the same
CREATE TABLE user_saved_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_title TEXT NOT NULL,
    job_company TEXT NOT NULL,
    job_location TEXT,
    job_description TEXT,
    job_link TEXT NOT NULL,
    job_source TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, job_link)
);