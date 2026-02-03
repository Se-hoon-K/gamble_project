"""
Stock Market GUI Screen
Displays stocks, prices, and trading interface
"""

import pygame
import time
from gui.components.colors import (
    DARK_GREEN, WHITE, GOLD, RED, GREEN, BLACK,
    BG_DARK, BG_MEDIUM, BLUE, YELLOW
)
from gui.components.button import Button


class StockMarketScreen:
    """
    Stock market trading screen
    """

    def __init__(self, screen, balance_manager, save_manager, stock_engine, portfolio):
        self.screen = screen
        self.balance = balance_manager
        self.save_manager = save_manager

        # Use shared stock engine (runs in background thread)
        self.engine = stock_engine
        self.portfolio = portfolio

        # Screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Fonts
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 22)

        # Selected stock for trading
        self.selected_stock = None
        self.trade_quantity = 1

        # Scroll offset for stock list
        self.scroll_offset = 0
        self.max_visible_stocks = 6

        # Message display
        self.message = ""
        self.message_color = WHITE
        self.message_time = 0

        # Recent event display
        self.current_event = None
        self.event_display_time = 0

        # Create buttons
        self.create_buttons()

    def create_buttons(self):
        """Create all buttons"""
        # Back button
        self.back_button = Button(30, self.height - 55, 100, 45, "BACK", font_size=28)

        # Buy/Sell buttons (will be positioned near selected stock)
        self.buy_button = Button(0, 0, 80, 40, "BUY", font_size=24)
        self.buy_button.color_idle = (40, 120, 40)
        self.buy_button.color_hover = (60, 160, 60)

        self.sell_button = Button(0, 0, 80, 40, "SELL", font_size=24)
        self.sell_button.color_idle = (120, 40, 40)
        self.sell_button.color_hover = (160, 60, 60)

        # Quantity buttons
        self.qty_minus = Button(0, 0, 40, 40, "-", font_size=28)
        self.qty_plus = Button(0, 0, 40, 40, "+", font_size=28)

        # Quick buy buttons
        self.buy_1 = Button(0, 0, 50, 35, "1", font_size=22)
        self.buy_5 = Button(0, 0, 50, 35, "5", font_size=22)
        self.buy_10 = Button(0, 0, 50, 35, "10", font_size=22)
        self.buy_max = Button(0, 0, 60, 35, "MAX", font_size=22)

    def draw(self):
        """Draw the stock market screen"""
        self.screen.fill(BG_DARK)

        # Title
        title = self.font_large.render("STOCK MARKET", True, GOLD)
        title_rect = title.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title, title_rect)

        # Balance and portfolio value
        self.draw_header_stats()

        # Event ticker
        self.draw_event_ticker()

        # Stock list
        self.draw_stock_list()

        # Trading panel (right side)
        self.draw_trading_panel()

        # Price history graph (right side, below trading)
        self.draw_price_graph()

        # Portfolio panel (bottom)
        self.draw_portfolio_panel()

        # Message (centered above buttons with background for visibility)
        if self.message and time.time() - self.message_time < 3:
            msg = self.font_small.render(self.message, True, self.message_color)
            msg_rect = msg.get_rect(center=(self.width // 2, self.height - 58))
            # Draw background for visibility
            bg_rect = msg_rect.inflate(20, 8)
            pygame.draw.rect(self.screen, BG_DARK, bg_rect)
            pygame.draw.rect(self.screen, self.message_color, bg_rect, width=1)
            self.screen.blit(msg, msg_rect)

        # Back button
        self.back_button.draw(self.screen)

    def draw_header_stats(self):
        """Draw balance and portfolio stats"""
        y = 70

        # Use smaller font for stats to prevent overlap with large numbers
        # Balance
        balance_text = f"Cash: ${self.balance.get_balance():,.2f}"
        balance_surf = self.font_small.render(balance_text, True, GREEN)
        self.screen.blit(balance_surf, (20, y))

        # Portfolio value
        portfolio_value = self.portfolio.get_total_value(self.engine)
        portfolio_text = f"Stocks: ${portfolio_value:,.2f}"
        portfolio_surf = self.font_small.render(portfolio_text, True, BLUE)
        self.screen.blit(portfolio_surf, (220, y))

        # Total worth
        total = self.balance.get_balance() + portfolio_value
        total_text = f"Total: ${total:,.2f}"
        total_surf = self.font_small.render(total_text, True, GOLD)
        self.screen.blit(total_surf, (440, y))

        # Profit/Loss
        profit = self.portfolio.get_total_profit(self.engine)
        profit_color = GREEN if profit >= 0 else RED
        profit_sign = "+" if profit >= 0 else ""
        profit_text = f"P/L: {profit_sign}${abs(profit):,.2f}"
        profit_surf = self.font_small.render(profit_text, True, profit_color)
        self.screen.blit(profit_surf, (660, y))

    def draw_event_ticker(self):
        """Draw recent market event"""
        y = 105

        # Background bar
        pygame.draw.rect(self.screen, BG_MEDIUM, (0, y, self.width, 35))

        if self.current_event and time.time() - self.event_display_time < 5:
            event = self.current_event
            color = GREEN if event['is_positive'] else RED
            icon = "+" if event['is_positive'] else "-"
            impact_pct = abs(event['impact'] * 100)

            text = f"  {icon} {event['message']} ({impact_pct:.1f}%)"
            text_surf = self.font_small.render(text, True, color)
            self.screen.blit(text_surf, (10, y + 5))

    def draw_stock_list(self):
        """Draw the list of stocks"""
        start_y = 150
        stock_height = 55
        list_width = 620

        # Header
        pygame.draw.rect(self.screen, BG_MEDIUM, (20, start_y - 25, list_width, 25))
        headers = [("Symbol", 30), ("Name", 120), ("Price", 320), ("Change", 430), ("Risk", 530)]
        for text, x in headers:
            surf = self.font_tiny.render(text, True, WHITE)
            self.screen.blit(surf, (x, start_y - 22))

        # Stocks
        visible_stocks = self.engine.stocks[self.scroll_offset:self.scroll_offset + self.max_visible_stocks]

        for i, stock in enumerate(visible_stocks):
            y = start_y + i * stock_height

            # Background (highlight if selected)
            if self.selected_stock and self.selected_stock.symbol == stock.symbol:
                bg_color = (60, 80, 60)
            else:
                bg_color = BG_MEDIUM if i % 2 == 0 else BG_DARK

            pygame.draw.rect(self.screen, bg_color, (20, y, list_width, stock_height - 2))

            # Click area (stored for hit detection)
            stock.click_rect = pygame.Rect(20, y, list_width, stock_height - 2)

            # Symbol
            symbol_surf = self.font_medium.render(stock.symbol, True, GOLD)
            self.screen.blit(symbol_surf, (30, y + 8))

            # Name (truncated)
            name = stock.name[:18] + "..." if len(stock.name) > 18 else stock.name
            name_surf = self.font_small.render(name, True, WHITE)
            self.screen.blit(name_surf, (120, y + 12))

            # Price
            price_surf = self.font_medium.render(f"${stock.current_price:.2f}", True, WHITE)
            self.screen.blit(price_surf, (320, y + 8))

            # Change
            change = stock.get_day_change_percent()
            change_color = GREEN if change >= 0 else RED
            change_sign = "+" if change >= 0 else ""
            change_surf = self.font_small.render(f"{change_sign}{change:.1f}%", True, change_color)
            self.screen.blit(change_surf, (430, y + 12))

            # Risk indicator
            risk_info = stock.get_risk_display()
            risk_surf = self.font_tiny.render(risk_info['label'], True, risk_info['color'])
            self.screen.blit(risk_surf, (530, y + 15))

            # Owned shares indicator
            holding = self.portfolio.get_holding(stock.symbol)
            if holding:
                owned_surf = self.font_tiny.render(f"Own: {holding['shares']}", True, BLUE)
                self.screen.blit(owned_surf, (30, y + 35))

        # Scroll indicators (positioned to avoid overlaps)
        if self.scroll_offset > 0:
            up_surf = self.font_tiny.render("^ More above", True, WHITE)
            self.screen.blit(up_surf, (550, start_y - 22))  # In header row

        if self.scroll_offset + self.max_visible_stocks < len(self.engine.stocks):
            down_surf = self.font_tiny.render("v More below", True, WHITE)
            # Position at bottom of stock list, above portfolio panel
            down_y = start_y + self.max_visible_stocks * stock_height - 18
            self.screen.blit(down_surf, (550, down_y))

    def draw_trading_panel(self):
        """Draw the trading panel on the right"""
        panel_x = 660
        panel_y = 150
        panel_width = 340
        panel_height = 300

        # Panel background
        pygame.draw.rect(self.screen, BG_MEDIUM, (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, GOLD, (panel_x, panel_y, panel_width, panel_height), width=2, border_radius=10)

        # Title
        title = self.font_medium.render("TRADE", True, GOLD)
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 25))
        self.screen.blit(title, title_rect)

        if self.selected_stock:
            stock = self.selected_stock
            y = panel_y + 55

            # Stock info
            symbol_surf = self.font_medium.render(stock.symbol, True, WHITE)
            self.screen.blit(symbol_surf, (panel_x + 20, y))

            price_surf = self.font_medium.render(f"${stock.current_price:.2f}", True, GREEN)
            self.screen.blit(price_surf, (panel_x + 150, y))

            y += 40

            # Quantity selector
            qty_label = self.font_small.render("Quantity:", True, WHITE)
            self.screen.blit(qty_label, (panel_x + 20, y + 8))

            # Position quantity buttons
            self.qty_minus.rect.x = panel_x + 120
            self.qty_minus.rect.y = y
            self.qty_minus.draw(self.screen)

            qty_surf = self.font_medium.render(str(self.trade_quantity), True, GOLD)
            qty_rect = qty_surf.get_rect(center=(panel_x + 185, y + 20))
            self.screen.blit(qty_surf, qty_rect)

            self.qty_plus.rect.x = panel_x + 210
            self.qty_plus.rect.y = y
            self.qty_plus.draw(self.screen)

            y += 50

            # Quick quantity buttons
            quick_x = panel_x + 20
            self.buy_1.rect.topleft = (quick_x, y)
            self.buy_5.rect.topleft = (quick_x + 60, y)
            self.buy_10.rect.topleft = (quick_x + 120, y)
            self.buy_max.rect.topleft = (quick_x + 180, y)

            self.buy_1.draw(self.screen)
            self.buy_5.draw(self.screen)
            self.buy_10.draw(self.screen)
            self.buy_max.draw(self.screen)

            y += 50

            # Cost preview
            total_cost = stock.current_price * self.trade_quantity
            cost_surf = self.font_small.render(f"Total: ${total_cost:.2f}", True, WHITE)
            self.screen.blit(cost_surf, (panel_x + 20, y))

            y += 35

            # Buy/Sell buttons
            self.buy_button.rect.topleft = (panel_x + 40, y)
            self.sell_button.rect.topleft = (panel_x + 180, y)

            self.buy_button.draw(self.screen)
            self.sell_button.draw(self.screen)

            y += 55

            # Holding info
            holding = self.portfolio.get_holding(stock.symbol)
            if holding:
                holding_text = f"You own: {holding['shares']} @ ${holding['avg_price']:.2f}"
                holding_surf = self.font_small.render(holding_text, True, BLUE)
                self.screen.blit(holding_surf, (panel_x + 20, y))

                current_val = stock.current_price * holding['shares']
                cost_basis = holding['avg_price'] * holding['shares']
                pl = current_val - cost_basis
                pl_color = GREEN if pl >= 0 else RED
                pl_sign = "+" if pl >= 0 else ""
                pl_text = f"P/L: {pl_sign}${pl:.2f}"
                pl_surf = self.font_small.render(pl_text, True, pl_color)
                self.screen.blit(pl_surf, (panel_x + 20, y + 25))
        else:
            # No stock selected
            hint = self.font_small.render("Click a stock to trade", True, WHITE)
            hint_rect = hint.get_rect(center=(panel_x + panel_width // 2, panel_y + 150))
            self.screen.blit(hint, hint_rect)

    def draw_price_graph(self):
        """Draw price history line chart for the selected stock"""
        panel_x = 660
        panel_y = 460
        panel_w = self.width - panel_x - 20
        panel_h = 170

        # Panel background
        rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, (0, 40, 0), rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD, rect, width=2, border_radius=8)

        if not self.selected_stock:
            hint = self.font_small.render("Select a stock to view chart", True, WHITE)
            hint_rect = hint.get_rect(center=(panel_x + panel_w // 2, panel_y + panel_h // 2))
            self.screen.blit(hint, hint_rect)
            return

        # Thread safety: copy the list
        history = list(self.selected_stock.price_history)

        if len(history) < 2:
            hint = self.font_small.render("Collecting data...", True, WHITE)
            hint_rect = hint.get_rect(center=(panel_x + panel_w // 2, panel_y + panel_h // 2))
            self.screen.blit(hint, hint_rect)
            return

        # Graph area (inset for labels)
        margin_left = 60
        margin_right = 15
        margin_top = 25
        margin_bottom = 20

        graph_x = panel_x + margin_left
        graph_y = panel_y + margin_top
        graph_w = panel_w - margin_left - margin_right
        graph_h = panel_h - margin_top - margin_bottom

        # Auto-scale Y axis
        min_price = min(history)
        max_price = max(history)
        price_range = max_price - min_price

        if price_range < 0.01:
            padding = max(max_price * 0.05, 0.50)
        else:
            padding = price_range * 0.10

        y_min = min_price - padding
        y_max = max_price + padding
        y_range = max(y_max - y_min, 0.01)

        # Horizontal grid lines with price labels
        num_grid = 4
        for i in range(num_grid + 1):
            frac = i / num_grid
            line_y = graph_y + graph_h - (frac * graph_h)
            price_val = y_min + frac * y_range

            pygame.draw.line(self.screen, (0, 60, 0),
                             (graph_x, int(line_y)), (graph_x + graph_w, int(line_y)), 1)

            label = self.font_tiny.render(f"${price_val:.2f}", True, (150, 150, 150))
            self.screen.blit(label, (panel_x + 3, int(line_y) - 8))

        # Price line
        line_color = GREEN if history[-1] >= history[0] else RED

        points = []
        for i, price in enumerate(history):
            px = graph_x + (i / (len(history) - 1)) * graph_w
            py = graph_y + graph_h - ((price - y_min) / y_range) * graph_h
            points.append((int(px), int(py)))

        if len(points) >= 2:
            pygame.draw.lines(self.screen, line_color, False, points, width=2)

        # Current price dot
        if points:
            pygame.draw.circle(self.screen, WHITE, points[-1], 4)

        # Title: symbol + price + change
        stock = self.selected_stock
        change = stock.get_day_change_percent()
        title_color = GREEN if change >= 0 else RED
        change_sign = "+" if change >= 0 else ""
        title_text = f"{stock.symbol}  ${stock.current_price:.2f}  {change_sign}{change:.1f}%"
        title_surf = self.font_small.render(title_text, True, title_color)
        self.screen.blit(title_surf, (graph_x, panel_y + 4))

        # X-axis labels
        old_label = self.font_tiny.render("oldest", True, (120, 120, 120))
        self.screen.blit(old_label, (graph_x, graph_y + graph_h + 3))

        now_label = self.font_tiny.render("now", True, (120, 120, 120))
        self.screen.blit(now_label, (graph_x + graph_w - 25, graph_y + graph_h + 3))

    def draw_portfolio_panel(self):
        """Draw owned stocks at the bottom"""
        panel_y = 640
        panel_height = 55

        # Background
        pygame.draw.rect(self.screen, BG_MEDIUM, (20, panel_y, self.width - 40, panel_height), border_radius=10)

        # Title
        title = self.font_small.render("YOUR PORTFOLIO", True, GOLD)
        self.screen.blit(title, (30, panel_y + 5))

        # Holdings (compact: symbol + value + P/L on one line)
        x = 30
        y = panel_y + 28

        if not self.portfolio.holdings:
            empty = self.font_tiny.render("No stocks owned yet. Buy some!", True, WHITE)
            self.screen.blit(empty, (x, y))
        else:
            for symbol, holding in list(self.portfolio.holdings.items())[:8]:
                stock = self.engine.get_stock(symbol)
                if not stock:
                    continue

                value = stock.current_price * holding['shares']
                cost = holding['avg_price'] * holding['shares']
                pl = value - cost
                pl_color = GREEN if pl >= 0 else RED
                pl_sign = "+" if pl >= 0 else ""

                text = f"{symbol}:{holding['shares']} ${value:.0f} ({pl_sign}${pl:.0f})"
                surf = self.font_tiny.render(text, True, pl_color)
                self.screen.blit(surf, (x, y))

                x += 150

    def update(self, events):
        """Update the screen"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Check for new events from background thread
        # (prices update automatically in background)
        new_events = self.engine.get_recent_events()
        if new_events:
            self.current_event = new_events[-1]  # Show most recent
            self.event_display_time = time.time()

        # Update buttons
        self.back_button.update(mouse_pos)

        if self.selected_stock:
            self.buy_button.update(mouse_pos)
            self.sell_button.update(mouse_pos)
            self.qty_minus.update(mouse_pos)
            self.qty_plus.update(mouse_pos)
            self.buy_1.update(mouse_pos)
            self.buy_5.update(mouse_pos)
            self.buy_10.update(mouse_pos)
            self.buy_max.update(mouse_pos)

        # Handle events
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_click(mouse_pos)
                elif event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.button == 5:  # Scroll down
                    max_scroll = max(0, len(self.engine.stocks) - self.max_visible_stocks)
                    self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

        # Handle button clicks
        if self.back_button.is_clicked(mouse_pos, mouse_pressed):
            return 'menu'

        if self.selected_stock:
            if self.buy_button.is_clicked(mouse_pos, mouse_pressed):
                self.handle_buy()
            if self.sell_button.is_clicked(mouse_pos, mouse_pressed):
                self.handle_sell()
            if self.qty_minus.is_clicked(mouse_pos, mouse_pressed):
                self.trade_quantity = max(1, self.trade_quantity - 1)
            if self.qty_plus.is_clicked(mouse_pos, mouse_pressed):
                self.trade_quantity = min(999, self.trade_quantity + 1)
            if self.buy_1.is_clicked(mouse_pos, mouse_pressed):
                self.trade_quantity = 1
            if self.buy_5.is_clicked(mouse_pos, mouse_pressed):
                self.trade_quantity = 5
            if self.buy_10.is_clicked(mouse_pos, mouse_pressed):
                self.trade_quantity = 10
            if self.buy_max.is_clicked(mouse_pos, mouse_pressed):
                max_affordable = int(self.balance.get_balance() / self.selected_stock.current_price)
                self.trade_quantity = max(1, max_affordable)

        return None

    def handle_click(self, pos):
        """Handle mouse click on stock list"""
        visible_stocks = self.engine.stocks[self.scroll_offset:self.scroll_offset + self.max_visible_stocks]

        for stock in visible_stocks:
            if hasattr(stock, 'click_rect') and stock.click_rect.collidepoint(pos):
                self.selected_stock = stock
                self.trade_quantity = 1
                break

    def handle_buy(self):
        """Handle buy button click"""
        if not self.selected_stock:
            return

        result = self.portfolio.buy_stock(
            self.selected_stock,
            self.trade_quantity,
            self.balance
        )

        self.message = result['message']
        self.message_color = GREEN if result['success'] else RED
        self.message_time = time.time()

    def handle_sell(self):
        """Handle sell button click"""
        if not self.selected_stock:
            return

        result = self.portfolio.sell_stock(
            self.selected_stock,
            self.trade_quantity,
            self.balance
        )

        self.message = result['message']
        self.message_color = GREEN if result['success'] else RED
        self.message_time = time.time()

        if result['success']:
            profit = result['profit']
            profit_sign = "+" if profit >= 0 else ""
            self.message += f" ({profit_sign}${profit:.2f})"
