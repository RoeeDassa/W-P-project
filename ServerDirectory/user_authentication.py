# Import necessary modules and classes from other files
import sqlite3
from dassabase import DatabaseManager

"""
Name: user_authentication
Author: Roee Dassa
Explanation: file contains functions used
to authenticate user
"""


# Class definition for UserAuthentication
class UserAuthentication:
    def __init__(self):
        # Create instance of DatabaseManager
        self.db_manager = DatabaseManager()

    def get_banned_sites(self, username):
        # Retrieve the user_id based on the provided username
        user_id = self.get_user_id(username)
        if user_id:
            with self.db_manager.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT site FROM banned_sites WHERE user_id = ?',
                    (user_id,))
                banned_sites = cursor.fetchall()

                if not banned_sites:
                    print(f"{username} doesn't have any banned sites.")
                    return []  # Ensure always returning a list, even if
                    # empty.
                else:
                    return [site[0] for site in
                            banned_sites]  # Extract sites from tuples.

    def add_banned_site(self, username, site):
        user_id = self.get_user_id(username)
        if user_id:
            with self.db_manager.create_connection() as conn:
                conn.execute(
                    'INSERT INTO banned_sites (user_id, site) VALUES (?, ?)',
                    (user_id, site))
                conn.commit()

    def remove_banned_site(self, username, site):
        user_id = self.get_user_id(username)
        if user_id:
            with self.db_manager.create_connection() as conn:
                conn.execute(
                    'DELETE FROM banned_sites WHERE user_id = ? AND site = ?',
                    (user_id, site))
                conn.commit()

    def get_user_id(self, username):
        with self.db_manager.create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
            user_id = cursor.fetchone()
            return user_id[0] if user_id else None

    def receive_banned_data(self, username, site):
        user_id = self.get_user_id(username)

        if user_id is not None:
            return user_id, site
        else:
            print("User not found.")
            return None

    def check_user_exists(self, username, password):
        # Check if the user exists in the database
        with self.db_manager.create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = ? AND password = ?',
                (username, password))
            return bool(cursor.fetchone())

    def is_info_legal(self, username, password):
        # Check if the username and password are legal
        if not DatabaseManager.is_name_legal(username):
            return False

        # Check if user already exists
        if self.check_user_exists(username, password):
            return False

        # Check if the password is legal
        if not DatabaseManager.is_password_legal(password):
            return False

        return True

    def create_user_data(self, username, password):
        # Check if the username is legal and not already taken
        if not DatabaseManager.is_name_legal(username):
            print("Error: Username "
                  "must consist of "
                  "alphabetical characters "
                  "only.")
            return

        new_user_data = None

        try:
            # Check if user already exists
            if self.check_user_exists(username, password):
                print("Error: Username already taken.")
                return

            # Check if the password is legal
            if not DatabaseManager.is_password_legal(password):
                print(
                    "Error: Password must be at "
                    "least 8 characters long and include "
                    "letters, numbers, and "
                    "special characters.")
                return

            # Insert the new user into the database
            with self.db_manager.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, password))
                conn.commit()

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

        return new_user_data
