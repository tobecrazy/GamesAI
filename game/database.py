import sqlite3
import os
import datetime

class TetrisDatabase:
    def __init__(self, db_path="tetris_scores.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT DEFAULT 'Anonymous',
                score INTEGER NOT NULL,
                level INTEGER NOT NULL,
                lines_cleared INTEGER NOT NULL,
                grade TEXT NOT NULL,
                date_time TEXT NOT NULL
            )
            ''')
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_states (
                player_name TEXT PRIMARY KEY,
                game_state TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
    
    def calculate_grade(self, score, level):
        """Calculate a grade based on score and level."""
        # Simple grading system based on score and level
        if score >= 10000:
            return "S"
        elif score >= 7500:
            return "A"
        elif score >= 5000:
            return "B"
        elif score >= 2500:
            return "C"
        elif score >= 1000:
            return "D"
        else:
            return "F"
    
    def save_score(self, player_name, score, level, lines_cleared):
        """Save a game score to the database."""
        try:
            grade = self.calculate_grade(score, level)
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute('''
            INSERT INTO scores (player_name, score, level, lines_cleared, grade, date_time)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (player_name, score, level, lines_cleared, grade, date_time))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving score: {e}")
            return False
    
    def get_high_scores(self, limit=10):
        """Get the top scores from the database."""
        try:
            self.cursor.execute('''
            SELECT player_name, score, level, lines_cleared, grade, date_time
            FROM scores
            ORDER BY score DESC
            LIMIT ?
            ''', (limit,))
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving high scores: {e}")
            return []
    
    def get_player_scores(self, player_name, limit=10):
        """Get scores for a specific player."""
        try:
            self.cursor.execute('''
            SELECT player_name, score, level, lines_cleared, grade, date_time
            FROM scores
            WHERE player_name = ?
            ORDER BY score DESC
            LIMIT ?
            ''', (player_name, limit))
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving player scores: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def save_game_state(self, player_name, game_state_json):
        """Save a game state to the database."""
        try:
            if not self.conn or not self.cursor:
                self.connect()
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute('''
            INSERT OR REPLACE INTO game_states (player_name, game_state, timestamp)
            VALUES (?, ?, ?)
            ''', (player_name, game_state_json, timestamp))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving game state: {e}")
            return False

    def load_game_state(self, player_name):
        """Load a game state from the database."""
        try:
            if not self.conn or not self.cursor:
                self.connect()
            
            self.cursor.execute('''
            SELECT game_state FROM game_states WHERE player_name = ?
            ''', (player_name,))
            
            row = self.cursor.fetchone()
            if row:
                return row[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error loading game state: {e}")
            return None
