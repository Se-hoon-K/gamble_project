"""
Stock Market Configuration
Defines stocks, sectors, and market parameters
"""

# Volatility ranges by risk level
VOLATILITY_RANGES = {
    'stable': (0.01, 0.02),      # 1-2% daily swings
    'moderate': (0.02, 0.035),   # 2-3.5% daily swings
    'volatile': (0.035, 0.05)    # 3.5-5% daily swings
}

# Trend ranges (long-term drift)
TREND_RANGE = (-0.002, 0.002)  # -0.2% to +0.2% per update

# Stock definitions
STOCKS = [
    # Technology sector
    {
        'symbol': 'TECH',
        'name': 'TechCorp Industries',
        'sector': 'Technology',
        'base_price': 150.00,
        'risk': 'moderate'
    },
    {
        'symbol': 'GAME',
        'name': 'GameWorld Inc',
        'sector': 'Technology',
        'base_price': 65.00,
        'risk': 'volatile'
    },
    {
        'symbol': 'CHIP',
        'name': 'ChipMaker Ltd',
        'sector': 'Technology',
        'base_price': 220.00,
        'risk': 'volatile'
    },

    # Food & Beverage sector
    {
        'symbol': 'FOOD',
        'name': 'FoodMart Corp',
        'sector': 'Food',
        'base_price': 45.00,
        'risk': 'stable'
    },
    {
        'symbol': 'BREW',
        'name': 'BrewCo Beverages',
        'sector': 'Food',
        'base_price': 78.00,
        'risk': 'stable'
    },

    # Healthcare sector
    {
        'symbol': 'HEAL',
        'name': 'HealthPlus Medical',
        'sector': 'Healthcare',
        'base_price': 180.00,
        'risk': 'moderate'
    },
    {
        'symbol': 'PHRM',
        'name': 'PharmaCure Inc',
        'sector': 'Healthcare',
        'base_price': 95.00,
        'risk': 'volatile'
    },

    # Energy sector
    {
        'symbol': 'ENRG',
        'name': 'EnergyMax Power',
        'sector': 'Energy',
        'base_price': 85.00,
        'risk': 'moderate'
    },
    {
        'symbol': 'SOLAR',
        'name': 'SolarBright Corp',
        'sector': 'Energy',
        'base_price': 42.00,
        'risk': 'volatile'
    },

    # Finance sector
    {
        'symbol': 'BANK',
        'name': 'MegaBank Financial',
        'sector': 'Finance',
        'base_price': 120.00,
        'risk': 'stable'
    },
    {
        'symbol': 'INVT',
        'name': 'InvestPro Holdings',
        'sector': 'Finance',
        'base_price': 200.00,
        'risk': 'moderate'
    },

    # Retail sector
    {
        'symbol': 'SHOP',
        'name': 'ShopMart Retail',
        'sector': 'Retail',
        'base_price': 55.00,
        'risk': 'stable'
    },
]

# Risk level display
RISK_DISPLAY = {
    'stable': {'label': 'STABLE', 'color': (46, 204, 113)},      # Green
    'moderate': {'label': 'MODERATE', 'color': (241, 196, 15)},  # Yellow
    'volatile': {'label': 'VOLATILE', 'color': (231, 76, 60)}    # Red
}

# Market event templates
EVENT_TEMPLATES = {
    'positive': {
        'Technology': [
            "{name} unveils breakthrough AI technology!",
            "{name} secures major cloud computing contract!",
            "{name} patents revolutionary tech!",
            "{name}'s new product exceeds expectations!",
        ],
        'Food': [
            "{name} expands to new markets!",
            "{name} reports record quarterly sales!",
            "{name} wins major restaurant chain contract!",
        ],
        'Healthcare': [
            "{name} gets FDA approval for new drug!",
            "{name}'s clinical trial shows promise!",
            "{name} announces breakthrough treatment!",
        ],
        'Energy': [
            "{name} discovers major new reserve!",
            "{name} announces renewable energy expansion!",
            "{name} signs long-term supply contract!",
        ],
        'Finance': [
            "{name} posts record profits!",
            "{name} expands digital banking platform!",
            "{name} announces share buyback program!",
        ],
        'Retail': [
            "{name} reports record holiday sales!",
            "{name} expands e-commerce platform!",
            "{name}'s same-store sales exceed targets!",
        ],
    },
    'negative': {
        'Technology': [
            "{name} delays product launch due to bugs!",
            "{name} faces data breach concerns!",
            "{name} misses revenue targets!",
        ],
        'Food': [
            "{name} recalls products over contamination!",
            "{name} faces supply chain disruption!",
            "{name} reports disappointing earnings!",
        ],
        'Healthcare': [
            "{name}'s drug trial fails safety test!",
            "{name} faces regulatory investigation!",
            "{name} recalls medical device!",
        ],
        'Energy': [
            "{name} faces environmental lawsuit!",
            "{name} cuts production amid low prices!",
            "{name} reports pipeline leak!",
        ],
        'Finance': [
            "{name} reports higher loan defaults!",
            "{name} faces fraud investigation!",
            "{name} cuts dividend amid losses!",
        ],
        'Retail': [
            "{name} closes underperforming stores!",
            "{name} reports weak foot traffic!",
            "{name} faces increased competition!",
        ],
    }
}

# Market update interval (milliseconds)
MARKET_UPDATE_INTERVAL = 2000  # Update prices every 2 seconds

# Event probability per update
EVENT_PROBABILITY = 0.03  # 3% chance per update

# Price history length for graph display
PRICE_HISTORY_LENGTH = 100
