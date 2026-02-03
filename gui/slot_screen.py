"""
Slot Machine GUI Screen
Displays animated slot machine with spinning reels
"""

import pygame
import time
from gui.components.colors import DARK_GREEN, WHITE, GOLD, RED, GREEN, BLACK
from gui.components.button import Button
from slot_machine.slot_engine import SlotEngine
from slot_machine.config import SYMBOLS, REEL_STRIPS, PAYOUTS, PAYLINE_PATTERNS, FULL_SCREEN_PAYOUTS


class SlotMachineScreen:
    """
    Slot machine screen with animated reels
    """

    def __init__(self, screen, balance_manager, save_manager):
        """
        Initialize slot machine screen

        Args:
            screen: Pygame screen surface
            balance_manager: Shared balance manager instance
            save_manager: Save manager for stats
        """
        self.screen = screen
        self.balance = balance_manager
        self.save_manager = save_manager
        self.engine = SlotEngine()

        # Screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Fonts
        self.font_huge = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_symbol = pygame.font.Font(None, 42)
        self.font_paytable = pygame.font.Font(None, 28)

        # Reel display settings
        self.reel_width = 120
        self.reel_height = 360
        self.reel_spacing = 15
        self.reels_start_x = (self.width - (5 * self.reel_width + 4 * self.reel_spacing)) // 2
        self.reels_y = 180
        self.symbol_height = self.reel_height // 3

        # Reel strips from config
        self.reel_strips = REEL_STRIPS

        # Animation state per reel (position-based, not speed-based)
        self.reel_offsets = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.reel_start_offsets = [0.0, 0.0, 0.0, 0.0, 0.0]  # Where each reel started
        self.reel_stopped = [True, True, True, True, True]
        self.final_stop_positions = [0, 0, 0, 0, 0]  # Target positions (always integers)

        # Animation parameters
        self.spin_duration = 2.5  # Total spin time for first reel
        self.cascade_delay = 0.3  # Delay between each reel stopping

        # Spinning animation state
        self.spinning = False
        self.spin_start_time = 0
        self.final_result = None

        # Bet amount
        self.bet_amount = 10

        # Last result
        self.last_payout = 0
        self.show_win_message = False
        self.win_message_time = 0

        # Message
        self.message = ""
        self.message_color = WHITE

        # Buttons
        self.create_buttons()

    def ease_out_cubic(self, t):
        """Easing function for smooth deceleration"""
        return 1 - pow(1 - t, 3)

    def create_buttons(self):
        """Create all buttons for this screen"""
        button_y = self.height - 100

        # Spin button (center)
        self.spin_button = Button(
            self.width // 2 - 120,
            button_y,
            240, 70,
            f"SPIN ${self.bet_amount}",
            font_size=48
        )
        self.spin_button.color_idle = (180, 50, 50)
        self.spin_button.color_hover = (220, 70, 70)
        self.spin_button.color_pressed = (140, 30, 30)

        # Back button (left)
        self.back_button = Button(
            30,
            button_y,
            120, 60,
            "BACK",
            font_size=32
        )

        # Bet adjustment buttons
        self.bet_minus_button = Button(
            self.width // 2 - 280,
            button_y + 5,
            50, 50,
            "-",
            font_size=48
        )

        self.bet_plus_button = Button(
            self.width // 2 + 230,
            button_y + 5,
            50, 50,
            "+",
            font_size=48
        )

    def draw_reel(self, reel_index, scroll_offset=None):
        """
        Draw a single reel with scrolling animation

        Args:
            reel_index: Index of reel (0-4)
            scroll_offset: Current scroll offset (None = use reel_offsets)
        """
        x = self.reels_start_x + reel_index * (self.reel_width + self.reel_spacing)
        y = self.reels_y

        # Draw reel background
        reel_rect = pygame.Rect(x, y, self.reel_width, self.reel_height)
        pygame.draw.rect(self.screen, WHITE, reel_rect)

        # Get scroll offset
        offset = scroll_offset if scroll_offset is not None else self.reel_offsets[reel_index]

        # Get reel strip
        reel_strip = self.reel_strips[reel_index]
        num_symbols = len(reel_strip)

        # Calculate which symbols are visible based on offset
        base_index = int(offset) % num_symbols
        fractional_offset = (offset % 1.0) * self.symbol_height

        # Set clip rect to only draw within reel bounds
        self.screen.set_clip(reel_rect)

        # Draw 4 symbols (one extra for smooth scrolling)
        for i in range(-1, 4):
            symbol_index = (base_index + i) % num_symbols
            symbol = reel_strip[symbol_index]

            # Calculate y position with scroll offset
            symbol_y = y + (i * self.symbol_height) - fractional_offset

            # Draw the symbol
            self.draw_symbol(symbol, x, symbol_y, self.reel_width, self.symbol_height)

        # Remove clip rect
        self.screen.set_clip(None)

        # Draw reel border
        pygame.draw.rect(self.screen, GOLD, reel_rect, width=4)

        # Draw payline indicators (all 3 rows are active)
        for row in range(3):
            line_y = y + row * self.symbol_height + self.symbol_height // 2
            pygame.draw.line(
                self.screen, (150, 50, 50),
                (x - 5, line_y),
                (x + self.reel_width + 5, line_y),
                width=1
            )

    def draw_symbol(self, symbol, x, y, width, height):
        """
        Draw a single symbol

        Args:
            symbol: Symbol name (e.g., 'cherry')
            x, y: Top-left position
            width, height: Size of symbol area
        """
        # Get symbol config
        symbol_config = SYMBOLS.get(symbol, {'display': '?', 'color': WHITE})

        # Draw symbol text
        text = symbol_config['display']
        color = symbol_config['color']

        symbol_surface = self.font_symbol.render(text, True, color)
        symbol_rect = symbol_surface.get_rect(
            center=(x + width // 2, y + height // 2)
        )
        self.screen.blit(symbol_surface, symbol_rect)

    def draw_paytable(self):
        """Draw payout table to the right of the reels"""
        reels_end_x = self.reels_start_x + 5 * self.reel_width + 4 * self.reel_spacing
        panel_x = reels_end_x + 20
        panel_y = self.reels_y
        row_height = 32
        panel_width = self.width - panel_x - 15

        # Panel background
        panel_height = 11 * row_height + 40
        bg_rect = pygame.Rect(panel_x - 10, panel_y, panel_width + 20, panel_height)
        pygame.draw.rect(self.screen, (0, 40, 0), bg_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD, bg_rect, width=2, border_radius=8)

        # Title
        y = panel_y + 10
        title = self.font_paytable.render("PAYOUTS", True, GOLD)
        title_rect = title.get_rect(centerx=panel_x + panel_width // 2, top=y)
        self.screen.blit(title, title_rect)

        # Column positions (with wider gaps to prevent overlap)
        col_name = panel_x
        col_3 = panel_x + 110
        col_4 = panel_x + 160
        col_5 = panel_x + 210

        # Column headers
        y += row_height + 2
        for text, cx in [("3x", col_3), ("4x", col_4), ("5x", col_5)]:
            surf = self.font_paytable.render(text, True, (180, 180, 180))
            self.screen.blit(surf, (cx, y))

        # Divider line
        y += row_height - 4
        pygame.draw.line(self.screen, GOLD, (panel_x - 4, y), (panel_x + panel_width + 4, y), 1)
        y += 8

        # Symbols ordered highest to lowest payout
        symbol_order = ['diamond', 'seven', 'bar', 'grape', 'orange', 'lemon', 'cherry']

        for symbol_name in symbol_order:
            symbol_config = SYMBOLS[symbol_name]
            payouts = PAYOUTS[symbol_name]

            # Symbol name (colored)
            name_surf = self.font_paytable.render(symbol_config['display'], True, symbol_config['color'])
            self.screen.blit(name_surf, (col_name, y))

            # Payout multipliers
            for val, cx in [(payouts[3], col_3), (payouts[4], col_4), (payouts[5], col_5)]:
                val_surf = self.font_paytable.render(str(val), True, WHITE)
                self.screen.blit(val_surf, (cx, y))

            y += row_height

        # Notes at bottom
        y += 6
        note1 = self.font_paytable.render("multiply x bet", True, (140, 140, 140))
        note1_rect = note1.get_rect(centerx=panel_x + panel_width // 2, top=y)
        self.screen.blit(note1, note1_rect)
        y += 18
        note2 = self.font_paytable.render("5 lines: 3 rows + V +", True, (140, 140, 140))
        note2_rect = note2.get_rect(centerx=panel_x + panel_width // 2, top=y)
        self.screen.blit(note2, note2_rect)
        # Render the Λ separately (inverted V symbol)
        lambda_surf = self.font_paytable.render(" \u039b", True, (140, 140, 140))
        self.screen.blit(lambda_surf, (note2_rect.right - 2, y))
        y += 20
        note3 = self.font_paytable.render("Full screen: 50x-2500x", True, (140, 140, 140))
        note3_rect = note3.get_rect(centerx=panel_x + panel_width // 2, top=y)
        self.screen.blit(note3, note3_rect)

    def draw(self):
        """Draw the entire slot machine screen"""
        # Background
        self.screen.fill(DARK_GREEN)

        # Title
        title = self.font_large.render("SLOT MACHINE", True, GOLD)
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)

        # Balance display
        balance_color = GREEN if self.balance.get_balance() > 0 else RED
        balance_text = self.font_medium.render(
            f"Balance: ${self.balance.get_balance():.2f}",
            True, balance_color
        )
        balance_rect = balance_text.get_rect(center=(self.width // 2, 110))
        self.screen.blit(balance_text, balance_rect)

        # Draw reels
        current_time = time.time()

        if self.spinning:
            elapsed = current_time - self.spin_start_time
            all_stopped = True

            for i in range(5):
                if not self.reel_stopped[i]:
                    all_stopped = False

                    # Each reel has its own duration (cascade effect)
                    reel_duration = self.spin_duration + i * self.cascade_delay
                    progress = min(elapsed / reel_duration, 1.0)

                    # Position-based interpolation: lerp from start to end using easing
                    # This guarantees we land exactly on the target
                    eased = self.ease_out_cubic(progress)
                    start = self.reel_start_offsets[i]
                    end = self.final_stop_positions[i]
                    self.reel_offsets[i] = start + (end - start) * eased

                    if progress >= 1.0:
                        # Ensure exact integer position
                        self.reel_offsets[i] = float(end)
                        self.reel_stopped[i] = True

                # Draw the reel
                self.draw_reel(i)

            # Check if all reels stopped
            if all_stopped:
                self.spinning = False
                if self.final_result and self.final_result['payout'] > 0:
                    # Credit winnings now that animation is done
                    self.balance.add(self.final_result['payout'])

                    # Update win stats
                    self.save_manager.increment_stat('slot_machine', 'total_won', self.final_result['payout'])
                    current_biggest = self.save_manager.get_stats('slot_machine').get('biggest_win', 0)
                    if self.final_result['payout'] > current_biggest:
                        self.save_manager.update_stat('slot_machine', 'biggest_win', self.final_result['payout'])
                    if not self.save_manager.has_achievement('first_win'):
                        self.save_manager.unlock_achievement('first_win')
                    self.save_manager.save()

                    self.show_win_message = True
                    self.win_message_time = current_time
                    self.last_payout = self.final_result['payout']
        else:
            # Not spinning - draw static reels
            for i in range(5):
                self.draw_reel(i)

        # Paytable (right side)
        self.draw_paytable()

        # Win message and winning line highlights
        if self.show_win_message and current_time - self.win_message_time < 2.5:
            winning_lines = 0
            is_full_screen = self.final_result and self.final_result.get('full_screen')

            # Highlight winning paylines across all reels
            if self.final_result and 'line_results' in self.final_result:
                for lr in self.final_result['line_results']:
                    if lr['payout'] > 0:
                        winning_lines += 1
                        rows = lr['rows']
                        # Build points through each reel center at the pattern's row
                        points = []
                        for reel in range(5):
                            px = self.reels_start_x + reel * (self.reel_width + self.reel_spacing) + self.reel_width // 2
                            py = self.reels_y + rows[reel] * self.symbol_height + self.symbol_height // 2
                            points.append((px, py))
                        # Extend slightly beyond first/last reel
                        extended = [(points[0][0] - 15, points[0][1])] + points + [(points[4][0] + 15, points[4][1])]
                        pygame.draw.lines(self.screen, GOLD, False, extended, width=4)

            # Full screen golden border effect
            if is_full_screen:
                all_reels_rect = pygame.Rect(
                    self.reels_start_x - 12, self.reels_y - 12,
                    5 * self.reel_width + 4 * self.reel_spacing + 24,
                    self.reel_height + 24
                )
                pygame.draw.rect(self.screen, GOLD, all_reels_rect, width=6, border_radius=8)

            # Win text
            if is_full_screen:
                win_label = f"FULL SCREEN! ${self.last_payout:.0f}!"
            elif winning_lines > 1:
                win_label = f"{winning_lines} LINES - WIN ${self.last_payout:.0f}!"
            else:
                win_label = f"WIN ${self.last_payout:.0f}!"
            win_text = self.font_huge.render(win_label, True, GOLD)
            win_rect = win_text.get_rect(center=(self.width // 2, self.height // 2 + 50))

            # Draw background for text
            bg_rect = win_rect.inflate(60, 30)
            pygame.draw.rect(self.screen, BLACK, bg_rect, border_radius=15)
            pygame.draw.rect(self.screen, GOLD, bg_rect, width=5, border_radius=15)

            self.screen.blit(win_text, win_rect)
        elif current_time - self.win_message_time >= 2.5:
            self.show_win_message = False

        # Message display
        if self.message:
            msg_text = self.font_small.render(self.message, True, self.message_color)
            msg_rect = msg_text.get_rect(center=(self.width // 2, 150))
            self.screen.blit(msg_text, msg_rect)

        # Bet amount display
        bet_text = self.font_small.render(
            f"Bet: ${self.bet_amount}",
            True, WHITE
        )
        bet_rect = bet_text.get_rect(center=(self.width // 2, self.height - 140))
        self.screen.blit(bet_text, bet_rect)

        # Draw buttons
        self.spin_button.draw(self.screen)
        self.back_button.draw(self.screen)
        self.bet_minus_button.draw(self.screen)
        self.bet_plus_button.draw(self.screen)

        # Stats display (positioned above bet text with enough spacing)
        stats = self.save_manager.get_stats('slot_machine')
        stats_text = self.font_small.render(
            f"Spins: {stats.get('total_spins', 0)}  |  Best Win: ${stats.get('biggest_win', 0):,.0f}",
            True, WHITE
        )
        stats_rect = stats_text.get_rect(center=(self.width // 2, self.height - 180))
        self.screen.blit(stats_text, stats_rect)

    def handle_spin(self):
        """Handle spin button click"""
        if self.spinning:
            return  # Already spinning

        if not self.balance.can_afford(self.bet_amount):
            self.message = "Not enough balance!"
            self.message_color = RED
            return

        # Clear message
        self.message = ""

        # Deduct bet
        self.balance.deduct(self.bet_amount)

        # Update stats
        self.save_manager.increment_stat('slot_machine', 'total_spins')
        self.save_manager.increment_stat('slot_machine', 'total_wagered', self.bet_amount)

        # Execute spin
        result = self.engine.spin(self.bet_amount)
        self.final_result = result

        # Calculate final stop positions for each reel
        # Use the exact stop_positions from the engine for perfect alignment
        for i in range(5):
            reel_strip = self.reel_strips[i]
            reel_length = len(reel_strip)

            # The engine's stop_position is where the TOP symbol lands
            # Our draw_reel uses: base_index = int(offset) % num_symbols
            # So we need int(final_offset) % reel_length == stop_position
            target_pos = result['stop_positions'][i]

            # Record where this reel is starting from
            self.reel_start_offsets[i] = self.reel_offsets[i]
            current_offset = self.reel_offsets[i]
            min_rotations = 3 + i  # More rotations for later reels

            # Calculate a target that's at least min_rotations full spins ahead
            # Must be an integer so we land exactly on a symbol
            base_target = target_pos
            while base_target < current_offset + (min_rotations * reel_length):
                base_target += reel_length

            self.final_stop_positions[i] = base_target

        # Reset animation state
        self.reel_stopped = [False, False, False, False, False]
        self.spinning = True
        self.spin_start_time = time.time()
        self.show_win_message = False

        self.save_manager.save()

    def update(self, events):
        """
        Update screen state

        Args:
            events: List of pygame events

        Returns:
            String indicating screen change ('menu', 'stock', None)
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Update button hover states
        self.spin_button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        self.bet_minus_button.update(mouse_pos)
        self.bet_plus_button.update(mouse_pos)

        # Handle button clicks
        if self.spin_button.is_clicked(mouse_pos, mouse_pressed):
            self.handle_spin()

        if self.back_button.is_clicked(mouse_pos, mouse_pressed):
            return 'menu'

        if self.bet_minus_button.is_clicked(mouse_pos, mouse_pressed):
            self.bet_amount = max(1, self.bet_amount - 5)
            self.spin_button.text = f"SPIN ${self.bet_amount}"

        if self.bet_plus_button.is_clicked(mouse_pos, mouse_pressed):
            self.bet_amount = min(100, self.bet_amount + 5)
            self.spin_button.text = f"SPIN ${self.bet_amount}"

        # Handle keyboard
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.spinning:
                    self.handle_spin()

        return None
