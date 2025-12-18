# Gambling App - Python Prototype

A beginner-friendly Python project to practice your skills while building slot machine and stock market game logic!

## What You'll Build

- **Slot Machine** - 5-reel slot with paylines, win detection, and payouts
- **Stock Market** - Realistic stock price simulation using Geometric Brownian Motion
- **Portfolio Management** - Buy/sell stocks, track gains/losses
- **CLI Interface** - Interactive command-line to play and test everything
- **Unit Tests** - Validate your code works correctly

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python main.py
   ```

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

## Step-by-Step Implementation Guide

Follow these steps to build the project. Code each file carefully and test as you go!

### Phase 1: Shared Utilities (Foundation)

These files provide core functionality used by both slot machine and stock market.

#### ✅ Step 1: Create `shared/random_utils.py`

**What it does:** Provides random number functions for the games.

**Key functions:**
- `get_random_int(min, max)` - Random integer
- `random_normal()` - Normal distribution (for stock prices)
- `random_float(min, max)` - Random decimal number

**Test it:**
```python
from shared.random_utils import get_random_int, random_normal
print(get_random_int(1, 10))  # Should print 1-10
print(random_normal())  # Should print a decimal around 0
```

---

#### ✅ Step 2: Create `shared/balance_manager.py`

**What it does:** Manages the player's virtual currency (shared between slots and stocks).

**Key methods:**
- `get_balance()` - Check current balance
- `add(amount)` - Add money (from winnings)
- `deduct(amount)` - Remove money (for bets/purchases)
- `can_afford(amount)` - Check if player has enough money

**Test it:**
```python
from shared.balance_manager import BalanceManager
balance = BalanceManager(1000)
print(balance)  # Balance: $1000.00
balance.deduct(100)
print(balance)  # Balance: $900.00
```

---

### Phase 2: Slot Machine Logic

Build the slot machine game engine step by step.

#### ✅ Step 3: Create `slot_machine/config.py`

**What it does:** Defines all slot machine constants (symbols, paylines, payouts).

**Important parts:**
- `SYMBOLS` - List of 6 symbol types
- `REEL_STRIPS` - 5 virtual reels with 30 symbols each
- `PAYLINES` - 5 different winning patterns
- `PAYTABLE` - How much each symbol pays

**No testing needed** - this is just configuration data.

---

#### ✅ Step 4: Create `slot_machine/reel_controller.py`

**What it does:** Spins the reels and generates random symbols.

**Key methods:**
- `spin()` - Spin all 5 reels, return 5x3 grid of symbols
- `get_random_stop_position()` - Pick random position on a reel
- `get_visible_symbols()` - Get 3 visible symbols from stop position
- `display_reels()` - Print reels in nice format

**Test it:**
```python
from slot_machine.reel_controller import ReelController
controller = ReelController()
symbols = controller.spin()
controller.display_reels(symbols)
# Should show a 5x3 grid of symbols
```

---

#### ✅ Step 5: Create `slot_machine/payline_calculator.py`

**What it does:** Checks if the player won and calculates payouts.

**Key methods:**
- `check_all_paylines()` - Check all 5 paylines for wins
- `check_payline()` - Check a single payline
- Returns total payout and winning line details

**Test it:**
```python
from slot_machine.payline_calculator import PaylineCalculator
calc = PaylineCalculator()

# Create a winning grid (all cherries on middle row)
winning_grid = [
    ['lemon', 'cherry', 'grape'],
    ['bar', 'cherry', 'lemon'],
    ['grape', 'cherry', 'bar'],
    ['lemon', 'cherry', 'grape'],
    ['bar', 'cherry', 'lemon']
]

result = calc.check_all_paylines(winning_grid, bet_amount=10)
print(result)  # Should show a win!
```

---

#### ✅ Step 6: Create `slot_machine/slot_engine.py`

**What it does:** Combines reel spinning and win checking - the complete slot machine!

**Key methods:**
- `spin(bet_amount)` - Execute a complete spin
- `display_result()` - Show results nicely

**Test it:**
```python
from slot_machine.slot_engine import SlotEngine
engine = SlotEngine()
result = engine.spin(bet_amount=10)
engine.display_result(result)
# Should show reels and any wins!
```

---

### Phase 3: Stock Market Logic

Build the stock market simulation.

#### ✅ Step 7: Create `stock_market/config.py`

**What it does:** Defines 12 fictional stocks with prices and sectors.

**Important parts:**
- `STOCKS` - List of 12 companies
- `MIN_PRICE` / `MAX_PRICE` - Price bounds ($1 - $10,000)
- `MIN_VOLATILITY` / `MAX_VOLATILITY` - How much prices jump
- `MIN_TREND` / `MAX_TREND` - Long-term price drift

**No testing needed** - just configuration.

---

#### ✅ Step 8: Create `stock_market/stock_engine.py`

**What it does:** Simulates realistic stock prices using Geometric Brownian Motion (the math behind real stocks!).

**Key classes:**
- `Stock` - Represents one stock with price, volatility, trend
- `StockEngine` - Manages all 12 stocks

**Key methods:**
- `update_price()` - Calculate new price using random walk
- `update_all_prices()` - Update entire market
- `display_market()` - Show all stocks in a table

**Test it:**
```python
from stock_market.stock_engine import StockEngine
engine = StockEngine()
engine.display_market()  # Show initial prices

# Simulate price movement
for i in range(5):
    engine.update_all_prices()
    print(f"\n--- After {i+1} updates ---")
    engine.display_market()
# Prices should change realistically!
```

---

#### ✅ Step 9: Create `stock_market/portfolio_manager.py`

**What it does:** Manages buying/selling stocks and tracks your holdings.

**Key methods:**
- `buy_stock()` - Purchase shares, calculate average price
- `sell_stock()` - Sell shares, return proceeds
- `get_portfolio_stats()` - Calculate total value, gains/losses
- `display_portfolio()` - Show all holdings in a table

**Test it:**
```python
from stock_market.stock_engine import StockEngine
from stock_market.portfolio_manager import PortfolioManager

engine = StockEngine()
portfolio = PortfolioManager()

# Buy some stocks
portfolio.buy_stock('TECH', 10, 150.0)
portfolio.buy_stock('GAME', 5, 65.0)

# View portfolio
portfolio.display_portfolio(engine)

# Update prices and check again
engine.update_all_prices()
portfolio.display_portfolio(engine)
# Should show profit/loss!
```

---

### Phase 4: CLI Interface

Make it playable with a command-line interface.

#### ✅ Step 10: Create `cli/slot_cli.py`

**What it does:** Interactive slot machine interface.

**Features:**
- Shows balance
- Lets user choose bet amount
- Spins reels
- Displays results
- Updates balance

**Test it:** You'll test this through the main menu.

---

#### ✅ Step 11: Create `cli/stock_cli.py`

**What it does:** Interactive stock trading interface.

**Features:**
- View market prices
- Buy stocks
- Sell stocks
- View portfolio
- Update prices (simulate time)

**Test it:** You'll test this through the main menu.

---

#### ✅ Step 12: Create `cli/main_menu.py`

**What it does:** Main menu that ties everything together.

**Options:**
1. Play Slot Machine
2. Stock Market
3. Reset Balance
4. Exit

**Test it:** You'll test this when you run main.py.

---

#### ✅ Step 13: Create `main.py`

**What it does:** Entry point to run the app.

**Just imports and runs the main menu.**

**Test it:**
```bash
python main.py
```

You should see the main menu and be able to play slots and trade stocks!

---

### Phase 5: Unit Tests

Write tests to validate your code.

#### ✅ Step 14: Create `tests/test_slot_machine.py`

**Tests:**
- Slot engine returns valid results
- Win detection works correctly
- No-win scenarios work correctly

**Run it:**
```bash
pytest tests/test_slot_machine.py -v
```

---

#### ✅ Step 15: Create `tests/test_stock_market.py`

**Tests:**
- Stock prices update
- Prices stay within bounds
- Portfolio buy/sell works
- Holdings track correctly

**Run it:**
```bash
pytest tests/test_stock_market.py -v
```

---

#### ✅ Step 16: Create `tests/test_balance.py`

**Tests:**
- Balance starts correctly
- Adding money works
- Deducting money works
- Insufficient funds handled correctly

**Run it:**
```bash
pytest tests/test_balance.py -v
```

---

## Python Concepts You'll Practice

By coding this project, you'll learn:

### ✅ Basics
- Variables and data types
- Functions with parameters
- Lists and dictionaries
- Loops (`for`, `while`)
- Conditionals (`if`, `else`)

### ✅ Object-Oriented Programming
- Classes and objects
- Methods and attributes
- `__init__` constructors
- `__str__` for printing

### ✅ Algorithms
- Random number generation
- Geometric Brownian Motion (stock prices!)
- Pattern matching (paylines)
- Financial calculations

### ✅ Software Engineering
- Code organization (modules)
- Unit testing with pytest
- Error handling
- User input validation

## Testing Your Code

### Manual Testing
```bash
python main.py
```

Play the game and verify:
- Slot machine spins correctly
- Wins are calculated properly
- Balance updates correctly
- Stocks can be bought/sold
- Prices change over time
- Portfolio shows gains/losses

### Automated Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_slot_machine.py -v

# Run with detailed output
pytest tests/ -vv
```

## Tips for Success

1. **Code one file at a time** - Don't rush ahead
2. **Test each file** before moving to the next
3. **Read the comments** in the code examples
4. **Experiment!** Try changing values and see what happens
5. **Use print statements** to debug
6. **Ask questions** if you get stuck

## Common Issues

**Import errors?**
- Make sure you're in the gamble_project directory
- Check that `__init__.py` files exist in each folder

**pytest not found?**
```bash
pip install pytest
```

**Module not found?**
- Run `python main.py` from the gamble_project directory
- Check your folder structure matches the layout

## Next Steps

Once you finish this Python prototype:

1. **You'll understand the game logic deeply**
2. **You can port it to JavaScript/TypeScript** for React Native
3. **You'll have working algorithms** to reference
4. **You'll feel confident** building the mobile app!

## Project Structure

```
gamble_project/
├── slot_machine/
│   ├── __init__.py              ✅ Done
│   ├── config.py                📝 You code this
│   ├── reel_controller.py       📝 You code this
│   ├── payline_calculator.py    📝 You code this
│   └── slot_engine.py           📝 You code this
│
├── stock_market/
│   ├── __init__.py              ✅ Done
│   ├── config.py                📝 You code this
│   ├── stock_engine.py          📝 You code this
│   └── portfolio_manager.py     📝 You code this
│
├── shared/
│   ├── __init__.py              ✅ Done
│   ├── balance_manager.py       📝 You code this
│   └── random_utils.py          📝 You code this
│
├── cli/
│   ├── __init__.py              ✅ Done
│   ├── main_menu.py             📝 You code this
│   ├── slot_cli.py              📝 You code this
│   └── stock_cli.py             📝 You code this
│
├── tests/
│   ├── test_slot_machine.py     📝 You code this
│   ├── test_stock_market.py     📝 You code this
│   └── test_balance.py          📝 You code this
│
├── main.py                      📝 You code this
├── requirements.txt             ✅ Done
└── README.md                    ✅ Done (this file!)
```

## Have Fun!

This project is designed to be fun AND educational. Enjoy coding and learning Python!

For detailed code examples of each file, check the plan file: `.claude/plans/toasty-bouncing-bunny.md`
