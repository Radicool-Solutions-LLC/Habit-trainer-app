import os
import sqlite3
from datetime import datetime, time, timedelta
import pathlib

class HabitTracker:
    def __init__(self):
        """Initialize the habit tracker with SQLite databases in the script directory."""
        # Get the directory of the current script
        self.script_dir = pathlib.Path(__file__).parent.absolute()
        
        # Define database file paths relative to script directory
        self.habits_db_file = os.path.join(self.script_dir, "habits_data.db")
        self.completions_db_file = os.path.join(self.script_dir, "habit_completions.db")  # Initialize completions_db_file
        
        # Initialize databases
        self._init_habits_database()
        self._init_completions_database()  

    def _init_habits_database(self):
        """Initialize SQLite database for storing habits, bonus codes, and accounts."""
        conn = sqlite3.connect(self.habits_db_file)
        cursor = conn.cursor()
        
        # Create habits table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            frequency_type TEXT NOT NULL,
            frequency_count INTEGER NOT NULL,
            duration_seconds INTEGER,
            streak INTEGER DEFAULT 1,
            reward_balance REAL DEFAULT 0.0,
            created_at TIMESTAMP NOT NULL,
            last_completed TIMESTAMP
        )
        ''')
        
        # Create preferred times table with foreign key relationship
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferred_times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
        )
        ''')
        
        # Create bonus codes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bonus_codes (
            code TEXT PRIMARY KEY,
            value REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP NOT NULL,
            expiry_date TIMESTAMP,
            used BOOLEAN DEFAULT 0,
            used_at TIMESTAMP
        )
        ''')
        
        # Create accounts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        conn.close()
    
    def add_account(self, email):
        """Add a new account to the database."""
        conn = sqlite3.connect(self.habits_db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO accounts (email) VALUES (?)
            ''', (email,))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"Account with email '{email}' already exists.")
        finally:
            conn.close()
    
    def check_account_exists(self):
        """Check if any accounts exist in the database."""
        conn = sqlite3.connect(self.habits_db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM accounts")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0



    def _init_completions_database(self):
        """Initialize SQLite database for tracking habit completions."""
        conn = sqlite3.connect(self.completions_db_file)
        cursor = conn.cursor()
        
        # Create completions table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completion_time TIMESTAMP NOT NULL,
            duration_seconds INTEGER,
            notes TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, email):
        """
        Add a new user account.
        
        Args:
            email (str): Email address of the user
            
        Returns:
            dict: The newly created user account or None if the email already exists
        """
        conn = sqlite3.connect(self.habits_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO user_accounts (email, created_at) VALUES (?, ?)",
                (email, now)
            )
            conn.commit()
            
            cursor.execute("SELECT * FROM user_accounts WHERE email = ?", (email,))
            user = dict(cursor.fetchone())
            return user
        except sqlite3.IntegrityError:
            # Email already exists
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email):
        """
        Get a user account by email.
        
        Args:
            email (str): Email address of the user
            
        Returns:
            dict: The user account or None if not found
        """
        conn = sqlite3.connect(self.habits_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user_accounts WHERE email = ?", (email,))
        user_row = cursor.fetchone()
        
        conn.close()
        
        if user_row:
            return dict(user_row)
        return None
    
    def user_exists(self, email):
        """
        Check if a user with the given email exists.
        
        Args:
            email (str): Email address to check
            
        Returns:
            bool: True if the user exists, False otherwise
        """
        user = self.get_user_by_email(email)
        return user is not None
    
    def add_habit(self, name, frequency_type, frequency_count, duration_seconds=0, 
                  preferred_times=None, description=""):
        """
        Add a new habit to track.
        
        Args:
            name (str): Name of the habit
            frequency_type (str): 'daily', 'weekly', 'monthly', or 'yearly'
            frequency_count (int): Number of times per frequency_type
            duration_seconds (int, optional): How long the habit takes in seconds
            preferred_times (list, optional): List of preferred times of day in 'HH:MM' format
            description (str, optional): Optional description of the habit
        
        Returns:
            dict: The newly created habit
        """
        # Validate frequency type
        valid_frequency_types = ['daily', 'weekly', 'monthly', 'yearly']
        if frequency_type not in valid_frequency_types:
            raise ValueError(f"Frequency type must be one of {valid_frequency_types}")
        
        # Process preferred times if provided
        if preferred_times is None:
            preferred_times = []
        else:
            # Validate time strings
            for time_str in preferred_times:
                try:
                    datetime.strptime(time_str, "%H:%M").time()
                except ValueError:
                    raise ValueError(f"Time '{time_str}' is not in valid 'HH:MM' format")
        
        conn = sqlite3.connect(self.habits_db_file)
        cursor = conn.cursor()
        
        try:
            # Insert the habit
            now = datetime.now().isoformat()
            cursor.execute('''
            INSERT INTO habits 
            (name, description, frequency_type, frequency_count, duration_seconds, created_at, streak)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, frequency_type, frequency_count, duration_seconds, now, 1))
            
            # Get the inserted habit's ID
            habit_id = cursor.lastrowid
            
            # Insert preferred times
            for time_str in preferred_times:
                cursor.execute('''
                INSERT INTO preferred_times (habit_id, time)
                VALUES (?, ?)
                ''', (habit_id, time_str))
            
            conn.commit()
            
            # Return the newly created habit
            return self.get_habit(habit_id)
            
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"Habit '{name}' already exists.")
        finally:
            conn.close()
    
    def get_habits(self):
        """Get all habits with their preferred times."""
        conn = sqlite3.connect(self.habits_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all habits
        cursor.execute("SELECT * FROM habits ORDER BY id")
        habits_rows = cursor.fetchall()
        
        habits = []
        for habit_row in habits_rows:
            habit = dict(habit_row)
            
            # Get preferred times for this habit
            cursor.execute("SELECT time FROM preferred_times WHERE habit_id = ?", (habit['id'],))
            preferred_times = [row['time'] for row in cursor.fetchall()]
            habit['preferred_times'] = preferred_times
            
            habits.append(habit)
        
        conn.close()
        return habits
    
    def get_habit(self, habit_id):
        """Get a specific habit by ID with its preferred times."""
        conn = sqlite3.connect(self.habits_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get the habit
        cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        habit_row = cursor.fetchone()
        
        if not habit_row:
            conn.close()
            return None
        
        habit = dict(habit_row)
        
        # Get preferred times for this habit
        cursor.execute("SELECT time FROM preferred_times WHERE habit_id = ?", (habit_id,))
        preferred_times = [row['time'] for row in cursor.fetchall()]
        habit['preferred_times'] = preferred_times
        
        conn.close()
        return habit
    
    def update_habit(self, habit_id, **kwargs):
        """Update a habit's attributes."""
        habit = self.get_habit(habit_id)
        if not habit:
            raise ValueError(f"Habit with ID {habit_id} not found.")
        
        conn = sqlite3.connect(self.habits_db_file)
        cursor = conn.cursor()
        
        try:
            # Special handling for preferred_times
            if 'preferred_times' in kwargs:
                preferred_times = kwargs['preferred_times']
                # Validate time strings
                for time_str in preferred_times:
                    try:
                        datetime.strptime(time_str, "%H:%M").time()
                    except ValueError:
                        raise ValueError(f"Time '{time_str}' is not in valid 'HH:MM' format")
                
                # Delete existing preferred times
                cursor.execute("DELETE FROM preferred_times WHERE habit_id = ?", (habit_id,))
                
                # Insert new preferred times
                for time_str in preferred_times:
                    cursor.execute('''
                    INSERT INTO preferred_times (habit_id, time)
                    VALUES (?, ?)
                    ''', (habit_id, time_str))
                
                del kwargs['preferred_times']
            
            # Update other allowed fields in the habits table
            allowed_fields = ['name', 'frequency_type', 'frequency_count', 
                             'description', 'duration_seconds']
            
            if any(key in allowed_fields for key in kwargs):
                update_parts = []
                update_values = []
                
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        update_parts.append(f"{key} = ?")
                        update_values.append(value)
                
                if update_parts:
                    query = f"UPDATE habits SET {', '.join(update_parts)} WHERE id = ?"
                    update_values.append(habit_id)
                    cursor.execute(query, update_values)
            
            conn.commit()
            
            # Return the updated habit
            return self.get_habit(habit_id)
            
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"Update failed. Name may already be in use.")
        finally:
            conn.close()
    
    def delete_habit(self, habit_id):
        """Delete a habit and all associated records."""
        habit = self.get_habit(habit_id)
        if not habit:
            raise ValueError(f"Habit with ID {habit_id} not found.")
        
        # Delete from habits database
        conn_habits = sqlite3.connect(self.habits_db_file)
        cursor_habits = conn_habits.cursor()
        
        try:
            # Foreign key constraints will cascade delete preferred times
            cursor_habits.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
            conn_habits.commit()
        except Exception as e:
            conn_habits.rollback()
            raise e
        finally:
            conn_habits.close()
        
        # Delete associated completions from completions database
        conn_completions = sqlite3.connect(self.completions_db_file)
        cursor_completions = conn_completions.cursor()
        
        try:
            cursor_completions.execute("DELETE FROM habit_completions WHERE habit_id = ?", (habit_id,))
            conn_completions.commit()
            return True
        except Exception as e:
            conn_completions.rollback()
            raise e
        finally:
            conn_completions.close()
    
    def record_completion(self, habit_id, duration_seconds=None, notes=""):
        """
        Record a completion of a habit and update streak.
        Also updates the reward balance.
        
        Args:
            habit_id (int): The ID of the habit
            duration_seconds (int, optional): How long the habit took to complete
            notes (str, optional): Optional notes about this completion
        
        Returns:
            dict: The updated habit
        """
        habit = self.get_habit(habit_id)
        if not habit:
            raise ValueError(f"Habit with ID {habit_id} not found.")
        
        # Use default duration if not provided
        if duration_seconds is None:
            duration_seconds = habit['duration_seconds']
        
        # Get current time
        now = datetime.now()
        completion_time = now.isoformat()
        
        # Record the completion in the completions database
        conn_completions = sqlite3.connect(self.completions_db_file)
        cursor_completions = conn_completions.cursor()
        
        try:
            cursor_completions.execute(
                "INSERT INTO habit_completions (habit_id, completion_time, duration_seconds, notes) VALUES (?, ?, ?, ?)",
                (habit_id, completion_time, duration_seconds, notes)
            )
            conn_completions.commit()
        except Exception as e:
            conn_completions.rollback()
            raise e
        finally:
            conn_completions.close()
        
        # Update the habit in the habits database
        conn_habits = sqlite3.connect(self.habits_db_file)
        cursor_habits = conn_habits.cursor()
        
        try:
            # Check if completed two days in a row. If yes: increases streak value. Otherwise, new_streak will be 1 (ie, reset)
            new_streak = 1
            if habit['last_completed']:
                last_time = datetime.fromisoformat(habit['last_completed'])
                
                if self._is_consecutive(last_time, now, habit['frequency_type']):
                    new_streak = habit['streak'] + 1

            # Update the habit's streak, last_completed, and reward_balance
            cursor_habits.execute(
                "UPDATE habits SET streak = ?, last_completed = ?, reward_balance = reward_balance + 0.25 WHERE id = ?",
                (new_streak, completion_time, habit_id)
            )
            
            conn_habits.commit()
            
            # Return the updated habit
            return self.get_habit(habit_id)
            
        except Exception as e:
            conn_habits.rollback()
            raise e
        finally:
            conn_habits.close()
    
    def _is_consecutive(self, last_time, current_time, frequency_type):
        """
        Determine if a completion is consecutive based on frequency type.
        This is a simplified version - you'll need to enhance this based on
        your specific streak calculation requirements.
        """
        delta = current_time - last_time
        
        if frequency_type == 'daily':
            # Within 24-48 hours for daily habits
            return delta.days <= 1
        elif frequency_type == 'weekly':
            # Within 5-9 days for weekly habits
            return 5 <= delta.days <= 9
        elif frequency_type == 'monthly':
            # Within 25-35 days for monthly habits
            return 25 <= delta.days <= 35
        elif frequency_type == 'yearly':
            # Within 350-380 days for yearly habits
            return 350 <= delta.days <= 380
        
        return False
    
    def update_reward_balance(self, habit_id, amount):
        """
        Update the reward balance for a habit.
        Positive amount adds to balance, negative reduces.
        """
        habit = self.get_habit(habit_id)
        if not habit:
            raise ValueError(f"Habit with ID {habit_id} not found.")
        
        conn = sqlite3.connect(self.habits_db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE habits SET reward_balance = reward_balance + ? WHERE id = ?",
                (amount, habit_id)
            )
            conn.commit()
            
            return self.get_habit(habit_id)
        finally:
            conn.close()
    
    def get_completions(self, habit_id, start_date=None, end_date=None):
        """
        Get all completions for a specific habit with optional date filtering.
        
        Args:
            habit_id (int): The ID of the habit
            start_date (str, optional): ISO format date string for filtering (inclusive)
            end_date (str, optional): ISO format date string for filtering (inclusive)
        
        Returns:
            list: List of completion records
        """
        conn = sqlite3.connect(self.completions_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM habit_completions WHERE habit_id = ?"
        params = [habit_id]
        
        if start_date:
            query += " AND completion_time >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND completion_time <= ?"
            params.append(end_date)
        
        query += " ORDER BY completion_time DESC"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_all_completions(self):
        """
        Get all habit completions from the database.
        
        Returns:
            list: List of completion records for all habits
        """
        conn = sqlite3.connect(self.completions_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fetch all completions
        cursor.execute("SELECT * FROM habit_completions ORDER BY completion_time DESC")
        completions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return completions



    # Bonus Codes Management
    def add_bonus_code(self, code, value, description="", expiry_date=None):
        """
        Add a new bonus code.
        
        Args:
            code (str): The unique bonus code
            value (float): The reward value of the bonus code
            description (str, optional): Description of the bonus code
            expiry_date (str, optional): ISO format date string for expiry
        
        Returns:
            dict: The newly created bonus code
        """
        conn = sqlite3.connect(self.habits_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        
        try:
            cursor.execute(
                "INSERT INTO bonus_codes (code, value, description, created_at, expiry_date, used) VALUES (?, ?, ?, ?, ?, ?)",
                (code, value, description, created_at, expiry_date, False)
            )
            conn.commit()
            
            cursor.execute("SELECT * FROM bonus_codes WHERE code = ?", (code,))
            bonus_code = dict(cursor.fetchone())
            
            return bonus_code
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"Bonus code '{code}' already exists.")
        finally:
            conn.close()
    
    def use_bonus_code(self, code, habit_id=None):
        """
        Use a bonus code and apply its value.
        
        Args:
            code (str): The bonus code to use
            habit_id (int, optional): The habit to apply the reward to.
                                     If None, creates a general reward credit.
        
        Returns:
            dict: Result with success status and details
        """
        conn = sqlite3.connect(self.habits_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if the bonus code exists
        cursor.execute("SELECT * FROM bonus_codes WHERE code = ?", (code,))
        bonus_row = cursor.fetchone()
        
        if not bonus_row:
            conn.close()
            return {'success': False, 'message': f"Bonus code '{code}' doesn't exist."}
        
        bonus_code = dict(bonus_row)
        
        if bonus_code['used']:
            conn.close()
            return {'success': False, 'message': f"Bonus code '{code}' has already been used."}
        
        if bonus_code['expiry_date']:
            expiry = datetime.fromisoformat(bonus_code['expiry_date'])
            if datetime.now() > expiry:
                conn.close()
                return {'success': False, 'message': f"Bonus code '{code}' has expired."}
        
        try:
            # Mark as used
            used_at = datetime.now().isoformat()
            cursor.execute(
                "UPDATE bonus_codes SET used = ?, used_at = ? WHERE code = ?",
                (True, used_at, code)
            )
            
            # Apply to specific habit if requested
            if habit_id is not None:
                # Check if the habit exists
                cursor.execute("SELECT name FROM habits WHERE id = ?", (habit_id,))
                habit_row = cursor.fetchone()
                
                if not habit_row:
                    conn.rollback()
                    conn.close()
                    return {'success': False, 'message': f"Habit with ID {habit_id} not found."}
                
                habit_name = habit_row['name']
                
                # Apply bonus to habit
                cursor.execute(
                    "UPDATE habits SET reward_balance = reward_balance + ? WHERE id = ?",
                    (bonus_code['value'], habit_id)
                )
                
                result = {
                    'success': True, 
                    'message': f"Applied bonus code '{code}' worth ${bonus_code['value']} to habit '{habit_name}'.",
                    'habit': habit_name,
                    'value': bonus_code['value']
                }
            else:
                # Could implement a general credit system here
                result = {
                    'success': True, 
                    'message': f"Redeemed bonus code '{code}' worth ${bonus_code['value']}.",
                    'value': bonus_code['value']
                }
            
            conn.commit()
            return result
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_bonus_codes(self, include_used=False):
        """
        Get all bonus codes, optionally including used ones.
        
        Args:
            include_used (bool): Whether to include used bonus codes
            
        Returns:
            list: List of bonus code dictionaries
        """
        conn = sqlite3.connect(self.habits_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if include_used:
            cursor.execute("SELECT * FROM bonus_codes")
        else:
            cursor.execute("SELECT * FROM bonus_codes WHERE used = 0")
            
        bonus_codes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return bonus_codes
    
    def minutes_to_seconds(self, minutes):
        """Utility method to convert minutes to seconds."""
        return int(minutes * 60)
    
    def get_current_user(self):
        """Get the current user's email"""
               
        # Example implementation that gets the first account from the database
        conn = sqlite3.connect(self.habit_tracker.habits_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT email FROM accounts LIMIT 1")
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return row['email']
        return 1  # Default fallback ID
    