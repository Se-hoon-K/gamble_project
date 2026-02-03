"""
Stock Market Engine
Handles stock price simulation and market events
"""

import random
import threading
import time
from queue import Queue
from shared.random_utils import random_normal, random_float, get_random_int
from stock_market.config import (
    STOCKS, VOLATILITY_RANGES, TREND_RANGE, RISK_DISPLAY,
    EVENT_TEMPLATES, EVENT_PROBABILITY, PRICE_HISTORY_LENGTH
)


class Stock:
    """
    Represents a single stock with price simulation
    """

    def __init__(self, symbol, name, sector, base_price, risk):
        self.symbol = symbol
        self.name = name
        self.sector = sector
        self.base_price = base_price
        self.current_price = base_price
        self.previous_price = base_price
        self.risk = risk

        # Get volatility range for this risk level
        vol_min, vol_max = VOLATILITY_RANGES[risk]
        self.volatility = random_float(vol_min, vol_max)

        # Random trend (slight bias up or down)
        self.trend = random_float(*TREND_RANGE)

        # Price history for charts
        self.price_history = [base_price]
        self.max_history = PRICE_HISTORY_LENGTH

        # Track daily change
        self.day_start_price = base_price

    def update_price(self):
        """
        Update price using Geometric Brownian Motion
        Returns the price change percentage
        """
        self.previous_price = self.current_price

        # Random factor from normal distribution
        random_factor = random_normal()

        # Calculate price change
        change = self.trend + (self.volatility * random_factor)

        # Apply change
        self.current_price = self.current_price * (1 + change)

        # Keep price positive (minimum $0.01)
        self.current_price = max(self.current_price, 0.01)

        # Update history
        self.price_history.append(self.current_price)
        if len(self.price_history) > self.max_history:
            self.price_history.pop(0)

        return change

    def apply_event_impact(self, impact):
        """Apply a market event impact to the price"""
        self.previous_price = self.current_price
        self.current_price = self.current_price * (1 + impact)
        self.current_price = max(self.current_price, 0.01)
        self.price_history.append(self.current_price)
        if len(self.price_history) > self.max_history:
            self.price_history.pop(0)

    def get_change_percent(self):
        """Get percentage change from previous price"""
        if self.previous_price == 0:
            return 0
        return ((self.current_price - self.previous_price) / self.previous_price) * 100

    def get_day_change_percent(self):
        """Get percentage change from day start"""
        if self.day_start_price == 0:
            return 0
        return ((self.current_price - self.day_start_price) / self.day_start_price) * 100

    def get_risk_display(self):
        """Get risk level display info"""
        return RISK_DISPLAY.get(self.risk, RISK_DISPLAY['moderate'])


class StockEngine:
    """
    Manages all stocks and market simulation
    """

    def __init__(self):
        self.stocks = []
        self.stocks_by_symbol = {}
        self.recent_events = []
        self.max_recent_events = 5

        self._initialize_stocks()

    def _initialize_stocks(self):
        """Create all stock objects"""
        for stock_data in STOCKS:
            stock = Stock(
                symbol=stock_data['symbol'],
                name=stock_data['name'],
                sector=stock_data['sector'],
                base_price=stock_data['base_price'],
                risk=stock_data['risk']
            )
            self.stocks.append(stock)
            self.stocks_by_symbol[stock.symbol] = stock

    def get_stock(self, symbol):
        """Get a stock by its symbol"""
        return self.stocks_by_symbol.get(symbol)

    def update_all_prices(self):
        """
        Update all stock prices
        Returns list of any triggered events
        """
        events = []

        for stock in self.stocks:
            stock.update_price()

        # Check for random event
        if random_float(0, 1) < EVENT_PROBABILITY:
            event = self._trigger_random_event()
            if event:
                events.append(event)

        return events

    def _trigger_random_event(self):
        """Trigger a random market event"""
        # Pick random stock
        stock = random.choice(self.stocks)

        # Decide positive or negative (slightly biased by stock trend)
        positive_chance = 0.5 + (stock.trend * 50)  # Trend influences direction
        is_positive = random_float(0, 1) < positive_chance

        # Get event template
        event_type = 'positive' if is_positive else 'negative'
        templates = EVENT_TEMPLATES.get(event_type, {}).get(stock.sector, [])

        if not templates:
            return None

        template = random.choice(templates)
        message = template.format(name=stock.name)

        # Calculate impact based on volatility
        if is_positive:
            impact = random_float(0.05, 0.15) * (stock.volatility / 0.03)
        else:
            impact = random_float(-0.12, -0.05) * (stock.volatility / 0.03)

        # Apply impact
        stock.apply_event_impact(impact)

        # Create event record
        event = {
            'stock': stock,
            'message': message,
            'impact': impact,
            'is_positive': is_positive
        }

        # Store in recent events
        self.recent_events.insert(0, event)
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events.pop()

        return event

    def get_stocks_sorted_by_change(self):
        """Get stocks sorted by price change (best performers first)"""
        return sorted(self.stocks, key=lambda s: s.get_day_change_percent(), reverse=True)

    def get_hot_stocks(self, count=3):
        """Get the top performing stocks"""
        sorted_stocks = self.get_stocks_sorted_by_change()
        return sorted_stocks[:count]

    def reset_day(self):
        """Reset day start prices (for a new trading day)"""
        for stock in self.stocks:
            stock.day_start_price = stock.current_price


class PortfolioManager:
    """
    Manages player's stock holdings
    """

    def __init__(self, save_manager):
        self.save_manager = save_manager
        self.holdings = save_manager.get_portfolio()

    def buy_stock(self, stock, shares, balance_manager):
        """
        Buy shares of a stock

        Returns:
            dict with 'success', 'message', 'total_cost'
        """
        total_cost = stock.current_price * shares

        if not balance_manager.can_afford(total_cost):
            return {
                'success': False,
                'message': 'Insufficient funds!',
                'total_cost': total_cost
            }

        # Deduct money
        balance_manager.deduct(total_cost)

        # Update holdings
        if stock.symbol in self.holdings:
            # Average the buy price
            existing = self.holdings[stock.symbol]
            total_shares = existing['shares'] + shares
            total_value = (existing['shares'] * existing['avg_price']) + total_cost
            avg_price = total_value / total_shares

            self.holdings[stock.symbol] = {
                'shares': total_shares,
                'avg_price': avg_price
            }
        else:
            self.holdings[stock.symbol] = {
                'shares': shares,
                'avg_price': stock.current_price
            }

        # Save
        self.save_manager.data['portfolio'] = self.holdings
        self.save_manager.save()

        # Update stats
        self.save_manager.increment_stat('stock_market', 'total_trades')

        return {
            'success': True,
            'message': f'Bought {shares} shares of {stock.symbol}!',
            'total_cost': total_cost
        }

    def sell_stock(self, stock, shares, balance_manager):
        """
        Sell shares of a stock

        Returns:
            dict with 'success', 'message', 'total_value', 'profit'
        """
        if stock.symbol not in self.holdings:
            return {
                'success': False,
                'message': 'You don\'t own this stock!',
                'total_value': 0,
                'profit': 0
            }

        holding = self.holdings[stock.symbol]

        if holding['shares'] < shares:
            return {
                'success': False,
                'message': f'You only own {holding["shares"]} shares!',
                'total_value': 0,
                'profit': 0
            }

        # Calculate profit/loss
        total_value = stock.current_price * shares
        cost_basis = holding['avg_price'] * shares
        profit = total_value - cost_basis

        # Add money
        balance_manager.add(total_value)

        # Update holdings
        holding['shares'] -= shares
        if holding['shares'] <= 0:
            del self.holdings[stock.symbol]
        else:
            self.holdings[stock.symbol] = holding

        # Save
        self.save_manager.data['portfolio'] = self.holdings
        self.save_manager.save()

        # Update stats
        self.save_manager.increment_stat('stock_market', 'total_trades')
        self.save_manager.increment_stat('stock_market', 'total_profit', profit)

        if profit > 0:
            self.save_manager.increment_stat('stock_market', 'profitable_trades')
            current_best = self.save_manager.get_stats('stock_market').get('biggest_gain', 0)
            if profit > current_best:
                self.save_manager.update_stat('stock_market', 'biggest_gain', profit)
        else:
            current_worst = self.save_manager.get_stats('stock_market').get('biggest_loss', 0)
            if abs(profit) > current_worst:
                self.save_manager.update_stat('stock_market', 'biggest_loss', abs(profit))

        self.save_manager.save()

        return {
            'success': True,
            'message': f'Sold {shares} shares of {stock.symbol}!',
            'total_value': total_value,
            'profit': profit
        }

    def get_holding(self, symbol):
        """Get holding info for a stock"""
        return self.holdings.get(symbol)

    def get_total_value(self, stock_engine):
        """Get total portfolio value at current prices"""
        total = 0
        for symbol, holding in self.holdings.items():
            stock = stock_engine.get_stock(symbol)
            if stock:
                total += stock.current_price * holding['shares']
        return total

    def get_total_profit(self, stock_engine):
        """Get total unrealized profit/loss"""
        total_profit = 0
        for symbol, holding in self.holdings.items():
            stock = stock_engine.get_stock(symbol)
            if stock:
                current_value = stock.current_price * holding['shares']
                cost_basis = holding['avg_price'] * holding['shares']
                total_profit += current_value - cost_basis
        return total_profit


class BackgroundStockEngine:
    """
    Thread-safe stock engine that runs price updates in the background.
    Stocks update even when viewing other screens.
    """

    def __init__(self, update_interval=2.0):
        """
        Args:
            update_interval: Seconds between price updates
        """
        self.engine = StockEngine()
        self.update_interval = update_interval

        # Thread control
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

        # Event queue (thread-safe)
        self.event_queue = Queue()

    def start(self):
        """Start the background update thread"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the background thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _update_loop(self):
        """Background loop that updates prices"""
        while self._running:
            # Update prices (thread-safe)
            with self._lock:
                events = self.engine.update_all_prices()

                # Queue any events for the UI to display
                for event in events:
                    self.event_queue.put(event)

            # Wait for next update
            time.sleep(self.update_interval)

    def get_stock(self, symbol):
        """Thread-safe access to a single stock"""
        with self._lock:
            return self.engine.get_stock(symbol)

    def get_recent_events(self):
        """Get and clear any pending events"""
        events = []
        while not self.event_queue.empty():
            try:
                events.append(self.event_queue.get_nowait())
            except:
                break
        return events

    @property
    def stocks(self):
        """Thread-safe access to stocks list"""
        with self._lock:
            return self.engine.stocks

    @property
    def stocks_by_symbol(self):
        """Thread-safe access to stocks dict"""
        with self._lock:
            return self.engine.stocks_by_symbol
