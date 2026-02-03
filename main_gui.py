"""
Main entry point for Pygame GUI version
Run this file to start the graphical gambling app!

Usage:
    python main_gui.py
"""

import pygame
import sys

# Initialize Pygame before importing screens (they need pygame.font)
pygame.init()

from shared.save_manager import SaveManager
from shared.balance_manager import BalanceManager
from stock_market.stock_engine import BackgroundStockEngine, PortfolioManager
from gui.menu_screen import MenuScreen
from gui.slot_screen import SlotMachineScreen
from gui.stock_screen import StockMarketScreen


# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Gambling App - Slots & Stocks"


def main():
    """Main game function"""
    # Create screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    # Create clock for FPS control
    clock = pygame.time.Clock()

    # Shared managers (persist across screens)
    save_manager = SaveManager()
    balance = BalanceManager(save_manager)

    # Create background stock engine (shared - updates even when on other screens)
    stock_engine = BackgroundStockEngine(update_interval=2.0)
    stock_engine.start()

    # Create shared portfolio manager
    portfolio = PortfolioManager(save_manager)

    # Create screens (pass shared stock engine and portfolio)
    screens = {
        'menu': MenuScreen(screen, balance, save_manager, stock_engine, portfolio),
        'slot': SlotMachineScreen(screen, balance, save_manager),
        'stock': StockMarketScreen(screen, balance, save_manager, stock_engine, portfolio),
    }

    current_screen_name = 'menu'

    # Main game loop
    running = True
    while running:
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            # ESC key to go back or quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_screen_name == 'menu':
                        running = False
                    else:
                        current_screen_name = 'menu'

        # Update current screen
        current_screen = screens[current_screen_name]
        screen_change = current_screen.update(events)

        # Handle screen transitions
        if screen_change and screen_change in screens:
            current_screen_name = screen_change

        # Draw current screen
        current_screen.draw()

        # Update display
        pygame.display.flip()

        # Control frame rate
        clock.tick(FPS)

    # Cleanup
    stock_engine.stop()  # Stop background thread
    save_manager.save()

    # Quit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
