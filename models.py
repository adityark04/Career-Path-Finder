# models.py
from flask_login import UserMixin
import sqlite3

class User(UserMixin):
    # Add all the new attributes from the database schema
    def __init__(self, id, username, password_hash, full_name, age, city, college, degree, skills):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.age = age
        self.city = city
        self.college = college
        self.degree = degree
        self.skills = skills

def get_user_by_id(user_id):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    user_row = connection.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    connection.close()
    if user_row:
        # Make sure to pass all the new fields to the User object
        return User(id=user_row['id'], username=user_row['username'], password_hash=user_row['password_hash'], 
                    full_name=user_row['full_name'], age=user_row['age'], city=user_row['city'],
                    college=user_row['college'], degree=user_row['degree'], skills=user_row['skills'])
    return None

def get_user_by_username(username):
    # This function also needs to be updated to return the full user object
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    user_row = connection.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    connection.close()
    if user_row:
        return User(id=user_row['id'], username=user_row['username'], password_hash=user_row['password_hash'], 
                    full_name=user_row['full_name'], age=user_row['age'], city=user_row['city'],
                    college=user_row['college'], degree=user_row['degree'], skills=user_row['skills'])
    return None