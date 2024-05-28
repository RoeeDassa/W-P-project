import sqlite3
import re
from server_constants import *

"""
DataBase file for user_authentication
Author: Roee Dassa
"""


class DatabaseManager:
    def __init__(self, db_name='unified_database.db'):
        # Initialize the UserDatabase class with the specified or default
        # database name
        self.db_name = db_name

    def create_users_table(self):
        with self.create_connection() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users
                             (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              username TEXT UNIQUE NOT NULL,
                              password TEXT NOT NULL)''')
            conn.commit()

    def create_banned_sites_table(self):
        with self.create_connection() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS banned_sites (
            site_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT 
            NULL, site TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(
            user_id))''')
            conn.commit()

    def create_connection(self):
        # Create a connection to the SQLite database
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def insert_user(self, user_data):
        # Insert user data into the 'users' table, handling IntegrityError
        # if user already exists
        try:
            with self.create_connection() as conn:
                self.create_users_table()  # Ensure 'users' table exists
                conn.execute('INSERT INTO users VALUES (?, ?, ?)', user_data)
        except sqlite3.IntegrityError:
            print(f"Error: User with user_id {user_data[0]} already exists.")

    @staticmethod
    def is_name_legal(user_name):
        # Check if the provided username is legal (contains only
        # alphabetical characters)
        return user_name.isalpha()

    @staticmethod
    def is_password_legal(password):
        # Check if the provided password is legal
        if len(password) < NUMBER_EIGHT:
            return False

        contains_letters = any(char.isalpha() for char in password)
        contains_numbers = any(char.isdigit() for char in password)
        contains_special_chars = bool(
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        return contains_letters and contains_numbers and contains_special_chars

    def insert_banned_site(self, banned_data):
        # Insert banned site data into the 'banned_sites' table
        try:
            with self.create_connection() as conn:
                self.create_banned_sites_table()  # Ensure 'banned_sites'
                # table exists
                conn.execute('INSERT INTO banned_sites VALUES (?, ?)',
                             (banned_data[0], banned_data[1]))
        except sqlite3.Error as e:
            print(f"SQLite error during insertion: {e}")

    def delete_banned_site(self, banned_data):
        # Delete a specific row from the 'banned_sites' table
        try:
            with self.create_connection() as conn:
                self.create_banned_sites_table()  # Ensure 'banned_sites'
                # table exists
                conn.execute(
                    'DELETE FROM banned_sites WHERE user_id = ? AND '
                    'sites = ?',
                    (banned_data[0], banned_data[1]))
        except sqlite3.Error as e:
            print(f"SQLite error during deletion: {e}")
