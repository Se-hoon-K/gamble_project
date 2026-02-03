"""
Slot Machine Configuration
Defines symbols, payouts, and reel strips
"""

# Symbol definitions with their display and color
SYMBOLS = {
    'cherry': {'display': 'CHERRY', 'color': (220, 20, 60)},
    'lemon': {'display': 'LEMON', 'color': (255, 255, 0)},
    'orange': {'display': 'ORANGE', 'color': (255, 140, 0)},
    'grape': {'display': 'GRAPE', 'color': (128, 0, 128)},
    'bar': {'display': 'BAR', 'color': (169, 169, 169)},
    'seven': {'display': '7', 'color': (255, 215, 0)},
    'diamond': {'display': 'DIAMOND', 'color': (0, 191, 255)}
}

# Payout multipliers (matching symbols on payline)
# Format: {symbol: {count: multiplier}}
PAYOUTS = {
    'cherry': {3: 2, 4: 5, 5: 10},
    'lemon': {3: 3, 4: 8, 5: 15},
    'orange': {3: 4, 4: 10, 5: 20},
    'grape': {3: 5, 4: 15, 5: 30},
    'bar': {3: 10, 4: 25, 5: 50},
    'seven': {3: 20, 4: 50, 5: 100},
    'diamond': {3: 50, 4: 100, 5: 250}
}

# Reel strips - defines what symbols are on each reel
# More common symbols appear more times
REEL_STRIPS = [
    # Reel 1
    ['cherry', 'lemon', 'orange', 'cherry', 'grape', 'lemon', 'bar',
     'cherry', 'orange', 'lemon', 'grape', 'cherry', 'seven', 'lemon',
     'orange', 'cherry', 'bar', 'lemon', 'grape', 'diamond'],

    # Reel 2
    ['lemon', 'cherry', 'grape', 'orange', 'lemon', 'cherry', 'bar',
     'lemon', 'grape', 'cherry', 'orange', 'seven', 'lemon', 'cherry',
     'grape', 'bar', 'lemon', 'orange', 'cherry', 'diamond'],

    # Reel 3
    ['orange', 'lemon', 'cherry', 'grape', 'bar', 'lemon', 'cherry',
     'orange', 'grape', 'lemon', 'seven', 'cherry', 'bar', 'orange',
     'lemon', 'grape', 'cherry', 'diamond', 'lemon', 'orange'],

    # Reel 4
    ['grape', 'orange', 'lemon', 'cherry', 'bar', 'grape', 'lemon',
     'cherry', 'orange', 'seven', 'grape', 'lemon', 'bar', 'cherry',
     'orange', 'lemon', 'diamond', 'grape', 'cherry', 'lemon'],

    # Reel 5
    ['lemon', 'grape', 'orange', 'cherry', 'lemon', 'bar', 'grape',
     'cherry', 'seven', 'orange', 'lemon', 'grape', 'bar', 'cherry',
     'diamond', 'lemon', 'orange', 'grape', 'cherry', 'lemon']
]

# Number of visible symbols per reel
VISIBLE_ROWS = 3

# Payline patterns - defines which row each reel contributes to each payline
# Format: (name, [row_for_reel_0, row_for_reel_1, ..., row_for_reel_4])
PAYLINE_PATTERNS = [
    ('top',    [0, 0, 0, 0, 0]),   # Top row
    ('middle', [1, 1, 1, 1, 1]),   # Middle row
    ('bottom', [2, 2, 2, 2, 2]),   # Bottom row
    ('v',      [0, 1, 2, 1, 0]),   # V shape
    ('inv_v',  [2, 1, 0, 1, 2]),   # Inverted V (Λ)
]

# Full screen bonus - all 15 visible symbols are the same
# Multiplier applied to bet amount (on top of line wins)
FULL_SCREEN_PAYOUTS = {
    'cherry': 50,
    'lemon': 75,
    'orange': 100,
    'grape': 200,
    'bar': 500,
    'seven': 1000,
    'diamond': 2500,
}

# Default bet amount
DEFAULT_BET = 10
MIN_BET = 1
MAX_BET = 100

# Pity system - scales with consecutive losses
# Each tier: (min_losses, trigger_chance, eligible_symbols)
# Chance is checked each spin once min_losses is reached
# Better symbols unlock at higher streaks
PITY_TIERS = [
    (5,  0.15, ['cherry']),                          # 15% chance, 2x payout
    (8,  0.25, ['cherry', 'lemon']),                  # 25% chance, up to 3x
    (11, 0.40, ['cherry', 'lemon', 'orange']),        # 40% chance, up to 4x
    (14, 0.60, ['lemon', 'orange', 'grape']),         # 60% chance, up to 5x
    (17, 0.80, ['orange', 'grape', 'bar']),           # 80% chance, up to 10x
    (20, 1.00, ['grape', 'bar', 'seven']),            # Guaranteed, up to 20x
]
