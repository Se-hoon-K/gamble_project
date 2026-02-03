"""
Main menu screen
"""

import pygame
import sys
from gui.components.colors import DARK_GREEN, GOLD, WHITE, RED, GREEN, BLUE
from gui.components.button import Button


class MenuScreen:
    """Main menu with game selection"""

    def __init__(self, screen, balance_manager, save_manager, stock_engine=None, portfolio=None):
        self.screen = screen
        self.balance = balance_manager
        self.save_manager = save_manager

        # Optional: shared stock engine for live portfolio display
        self.stock_engine = stock_engine
        self.portfolio = portfolio

        self.width = screen.get_width()
        self.height = screen.get_height()

        # Fonts
        self.font_title = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 42)
        self.font_small = pygame.font.Font(None, 32)

        # Create buttons
        self.create_buttons()

    def create_buttons(self):
        """Create menu buttons"""
        center_x = self.width // 2

        # Slot Machine button
        self.slot_button = Button(
            center_x - 200,
            300,
            400, 80,
            "SLOT MACHINE",
            font_size=48
        )

        # Stock Market button
        self.stock_button = Button(
            center_x - 200,
            420,
            400, 80,
            "STOCK MARKET",
            font_size=48
        )

        # Reset button
        self.reset_button = Button(
            center_x - 150,
            540,
            300, 60,
            "NEW GAME",
            font_size=36
        )
        self.reset_button.color_idle = (100, 100, 100)
        self.reset_button.color_hover = (130, 130, 130)

        # Quit button
        self.quit_button = Button(
            center_x - 150,
            620,
            300, 60,
            "QUIT",
            font_size=42
        )
        self.quit_button.color_idle = (150, 50, 50)
        self.quit_button.color_hover = (200, 70, 70)

    def draw(self):
        """Draw menu screen"""
        self.screen.fill(DARK_GREEN)

        # Title
        title = self.font_title.render("GAMBLING APP", True, GOLD)
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_medium.render("Slots & Stocks", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)

        # Balance and portfolio display
        cash = self.balance.get_balance()

        if self.stock_engine and self.portfolio:
            # Show detailed breakdown with live portfolio value
            portfolio_value = self.portfolio.get_total_value(self.stock_engine)
            total_worth = cash + portfolio_value

            # Cash
            cash_text = self.font_small.render(f"Cash: ${cash:,.2f}", True, GREEN)
            cash_rect = cash_text.get_rect(center=(self.width // 2, 210))
            self.screen.blit(cash_text, cash_rect)

            # Stocks (live updating)
            stocks_text = self.font_small.render(f"Stocks: ${portfolio_value:,.2f}", True, BLUE)
            stocks_rect = stocks_text.get_rect(center=(self.width // 2, 240))
            self.screen.blit(stocks_text, stocks_rect)

            # Total
            total_text = self.font_large.render(
                f"Total: ${total_worth:,.2f}",
                True, GOLD if total_worth > 0 else RED
            )
            total_rect = total_text.get_rect(center=(self.width // 2, 280))
            self.screen.blit(total_text, total_rect)
        else:
            # Simple balance display (fallback)
            balance_text = self.font_large.render(
                f"Balance: ${cash:,.2f}",
                True, GOLD if cash > 0 else RED
            )
            balance_rect = balance_text.get_rect(center=(self.width // 2, 230))
            self.screen.blit(balance_text, balance_rect)

        # Buttons
        self.slot_button.draw(self.screen)
        self.stock_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    def update(self, events):
        """
        Update menu state

        Returns:
            String indicating screen change ('slot', 'stock', None)
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Update hover states
        self.slot_button.update(mouse_pos)
        self.stock_button.update(mouse_pos)
        self.reset_button.update(mouse_pos)
        self.quit_button.update(mouse_pos)

        # Handle clicks
        if self.slot_button.is_clicked(mouse_pos, mouse_pressed):
            return 'slot'

        if self.stock_button.is_clicked(mouse_pos, mouse_pressed):
            return 'stock'  # Will implement later

        if self.reset_button.is_clicked(mouse_pos, mouse_pressed):
            # Reset game
            self.save_manager.reset()
            self.balance.set_balance(1000.0)

        if self.quit_button.is_clicked(mouse_pos, mouse_pressed):
            pygame.quit()
            sys.exit()

        return None
