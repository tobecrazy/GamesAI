import sqlite3
import os
import datetime
import json

class TetrisDatabase:
    def __init__(self, db_path="tetris_scores.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Ensure database directory exists (skip if path is in current directory)
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directories if path contains them
            os.makedirs(db_dir, exist_ok=True)
        
        # Connect and initialize database
        self.initialize_database()
        
    def initialize_database(self):
        """Initialize database connection and tables with retries."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not self.connect():
                    continue
                    
                # Verify tables exist or create them
                if not self.verify_tables():
                    if not self.create_tables():
                        continue
                        
                # If we get here, everything succeeded
                return
                
            except Exception as e:
                print(f"Database initialization attempt {attempt + 1} failed: {e}")
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                    
        raise Exception("Failed to initialize database after multiple attempts")
    
    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
        return True
    
    def verify_tables(self):
        """Check if required tables exist."""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scores'")
            if not self.cursor.fetchone():
                return False
                
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saves'")
            if not self.cursor.fetchone():
                return False
                
            return True
        except sqlite3.Error:
            return False

    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        try:
            with self.conn:
                # Create scores table
                self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT DEFAULT 'Anonymous',
                    score INTEGER NOT NULL,
                    level INTEGER NOT NULL,
                    lines_cleared INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    date_time TEXT NOT NULL
                )''')
                
                # Create saves table
                self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS saves (
                    player_name TEXT PRIMARY KEY,
                    game_state TEXT NOT NULL,
                    save_time TEXT NOT NULL
                )''')
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            return False
        return True
    
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
    
    def save_game(self, player_name, game_state):
        """Save the current game state."""
        try:
            save_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            game_state_json = json.dumps(game_state)
            
            self.cursor.execute('''
            INSERT OR REPLACE INTO saves (player_name, game_state, save_time)
            VALUES (?, ?, ?)
            ''', (player_name, game_state_json, save_time))
            
            self.conn.commit()
            return True
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, player_name):
        """Load a saved game state with detailed error handling."""
        try:
            print(f"Attempting to load game for player: {player_name}")
            
            # Verify player exists in saves table
            self.cursor.execute('''
            SELECT COUNT(*) FROM saves WHERE player_name = ?
            ''', (player_name,))
            if not self.cursor.fetchone()[0]:
                print(f"No save found for player: {player_name}")
                return None
                
            # Get the saved game state
            self.cursor.execute('''
            SELECT game_state FROM saves WHERE player_name = ?
            ''', (player_name,))
            
            result = self.cursor.fetchone()
            if not result:
                print("Unexpected error: No data returned for existing player")
                return None
                
            try:
                game_state = json.loads(result[0])
                print("Successfully loaded game state")
                return game_state
            except json.JSONDecodeError as e:
                print(f"Failed to parse game state JSON: {e}")
                return None
                
        except sqlite3.Error as e:
            print(f"Database error during load: {e}")
            return None
            return None

    def get_saved_games(self):
        """Get list of all saved games."""
        try:
            self.cursor.execute('''
            SELECT player_name, save_time FROM saves ORDER BY save_time DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving saved games: {e}")
            return []

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
