"""
Save Manager - Handles saving/loading player data to JSON file
Single-player local storage for game sessions
"""

import json
import os
from datetime import datetime
from shared.user_data import INIT_USER_MONEY, SAVE_FOLDER, SAVE_FILE, GAME_VERSION


class SaveManager:
    """
    Manages persistent storage of player data to JSON file

    Usage:
        save_mgr = SaveManager()
        save_mgr.data['player']['balance'] = 1500.0
        save_mgr.save()
    """

    def __init__(self):
        """Initialize and load existing save or create new"""
        self.save_path = os.path.join(SAVE_FOLDER, SAVE_FILE)
        self.data = self.load()

    def get_default_data(self):
        """Default data structure for new players"""
        return {
            'version': GAME_VERSION,
            'created_at': datetime.now().isoformat(),
            'last_played': datetime.now().isoformat(),

            'player': {
                'balance': INIT_USER_MONEY
            },

            'portfolio': {
                # 'TECH': {'shares': 5, 'avg_price': 150.00}
            },

            'achievements': [
                # {'id': 'first_trade', 'unlocked_at': '2024-01-15T10:00:00'}
            ],

            'stats': {
                'slot_machine': {
                    'total_spins': 0,
                    'total_wagered': 0.0,
                    'total_won': 0.0,
                    'biggest_win': 0.0,
                    'win_streak': 0,
                    'best_streak': 0
                },
                'stock_market': {
                    'total_trades': 0,
                    'profitable_trades': 0,
                    'total_profit': 0.0,
                    'biggest_gain': 0.0,
                    'biggest_loss': 0.0
                }
            },

            'settings': {
                'sound_enabled': True,
                'music_volume': 0.7,
                'default_bet': 10
            }
        }

    def load(self):
        """Load save file or return defaults"""
        # Create save folder if it doesn't exist
        if not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)

        # Load existing save or create new
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                    # Update last played timestamp
                    data['last_played'] = datetime.now().isoformat()
                    return data
            except (json.JSONDecodeError, KeyError):
                # Corrupted save - start fresh
                print("Warning: Save file corrupted. Starting new game.")
                return self.get_default_data()
        else:
            return self.get_default_data()

    def save(self):
        """Save current data to JSON file"""
        self.data['last_played'] = datetime.now().isoformat()

        try:
            with open(self.save_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving game: {e}")
            return False

    def reset(self):
        """Reset to default data (new game)"""
        self.data = self.get_default_data()
        self.save()

    # Convenience methods
    def get_balance(self):
        return self.data['player']['balance']

    def set_balance(self, amount):
        self.data['player']['balance'] = amount

    def get_portfolio(self):
        return self.data['portfolio']

    def get_stats(self, game_type):
        return self.data['stats'].get(game_type, {})

    def update_stat(self, game_type, stat_name, value):
        """Update a specific stat"""
        if game_type in self.data['stats']:
            self.data['stats'][game_type][stat_name] = value

    def increment_stat(self, game_type, stat_name, amount=1):
        """Increment a stat by amount"""
        if game_type in self.data['stats']:
            current = self.data['stats'][game_type].get(stat_name, 0)
            self.data['stats'][game_type][stat_name] = current + amount

    def unlock_achievement(self, achievement_id):
        """Unlock an achievement if not already unlocked"""
        existing_ids = [a['id'] for a in self.data['achievements']]
        if achievement_id not in existing_ids:
            self.data['achievements'].append({
                'id': achievement_id,
                'unlocked_at': datetime.now().isoformat()
            })
            return True  # Newly unlocked
        return False  # Already had it

    def has_achievement(self, achievement_id):
        """Check if player has an achievement"""
        return achievement_id in [a['id'] for a in self.data['achievements']]
