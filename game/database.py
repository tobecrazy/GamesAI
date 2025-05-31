import json
import datetime
# Attempt to import the 'js' module for JavaScript interoperability.
# This is common in Pyodide/Wasm environments.
try:
    import js
except ImportError:
    # Fallback for environments where 'js' module is not available (e.g., local testing)
    # This mock allows the script to be imported but will fail at runtime if js functions are called.
    print("Warning: 'js' module not found. localStorage functions will not work.")
    class MockJs:
        class MockLocalStorage:
            def setItem(self, key, value):
                print(f"MockLocalStorage: setItem({key}, {value})")
            def getItem(self, key):
                print(f"MockLocalStorage: getItem({key})")
                return None
            def removeItem(self, key):
                print(f"MockLocalStorage: removeItem({key})")
        localStorage = MockLocalStorage()
    js = MockJs()

class TetrisDatabase:
    def __init__(self, db_path=None):  # db_path is no longer used but kept for compatibility
        '''Initialize the database (no-op for localStorage).'''
        self.high_scores_key = "tetris_high_scores"
        self.saved_game_prefix = "tetris_saved_game_"
        # No connection or cursor needed for localStorage

    def connect(self):
        '''No-op for localStorage.'''
        pass

    def create_tables(self):
        '''No-op for localStorage.'''
        pass

    def close(self):
        '''No-op for localStorage.'''
        pass

    def _get_localStorage_item(self, key):
        try:
            return js.localStorage.getItem(key)
        except Exception as e:
            print(f"Error getting item from localStorage '{key}': {e}")
            return None

    def _set_localStorage_item(self, key, value):
        try:
            js.localStorage.setItem(key, value)
            return True
        except Exception as e:
            print(f"Error setting item in localStorage '{key}': {e}")
            return False

    def _remove_localStorage_item(self, key):
        try:
            js.localStorage.removeItem(key)
            return True
        except Exception as e:
            print(f"Error removing item from localStorage '{key}': {e}")
            return False

    def calculate_grade(self, score, level):
        '''Calculate a grade based on score and level. Remains unchanged.'''
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
        '''Save a game score to localStorage.'''
        try:
            grade = self.calculate_grade(score, level)
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            new_score_entry = {
                "player_name": player_name if player_name else "Anonymous",
                "score": score,
                "level": level,
                "lines_cleared": lines_cleared,
                "grade": grade,
                "date_time": date_time
            }

            high_scores_json = self._get_localStorage_item(self.high_scores_key)
            if high_scores_json:
                high_scores = json.loads(high_scores_json)
            else:
                high_scores = []

            high_scores.append(new_score_entry)
            high_scores.sort(key=lambda x: x["score"], reverse=True)
            high_scores = high_scores[:20]

            return self._set_localStorage_item(self.high_scores_key, json.dumps(high_scores))
        except Exception as e:
            print(f"Error saving score to localStorage: {e}")
            return False

    def get_high_scores(self, limit=10):
        '''Get the top scores from localStorage.'''
        try:
            high_scores_json = self._get_localStorage_item(self.high_scores_key)
            if high_scores_json:
                high_scores = json.loads(high_scores_json)
                formatted_scores = []
                for entry in high_scores:
                    formatted_scores.append((
                        entry["player_name"],
                        entry["score"],
                        entry["level"],
                        entry["lines_cleared"],
                        entry["grade"],
                        entry["date_time"]
                    ))
                return formatted_scores[:limit]
            return []
        except Exception as e:
            print(f"Error retrieving high scores from localStorage: {e}")
            return []

    def save_game_state(self, player_name, game_state_json):
        '''Save a game state to localStorage. game_state_json is already a JSON string.'''
        try:
            key = f"{self.saved_game_prefix}{player_name if player_name else 'Anonymous'}"
            return self._set_localStorage_item(key, game_state_json)
        except Exception as e:
            print(f"Error saving game state to localStorage: {e}")
            return False

    def load_game_state(self, player_name):
        '''Load a game state from localStorage. Returns a JSON string.'''
        try:
            key = f"{self.saved_game_prefix}{player_name if player_name else 'Anonymous'}"
            game_state_json = self._get_localStorage_item(key)
            return game_state_json
        except Exception as e:
            print(f"Error loading game state from localStorage: {e}")
            return None

def clear_tetris_localStorage_data():
    '''Helper function to clear data for testing.'''
    print("Attempting to clear Tetris data from localStorage...")
    try:
        db = TetrisDatabase()
        js.localStorage.removeItem(db.high_scores_key)
        js.localStorage.removeItem(f"{db.saved_game_prefix}Anonymous") # Example
        print("Cleared some Tetris data. Specific saved games need explicit removal by key.")
    except Exception as e:
        print(f"Error clearing localStorage: {e}")
