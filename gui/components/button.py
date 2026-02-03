"""
Reusable button component for Pygame GUI
"""

import pygame
from gui.components.colors import BUTTON_IDLE, BUTTON_HOVER, BUTTON_PRESSED, WHITE, GOLD


class Button:
    """
    A clickable button with hover effects

    Usage:
        button = Button(x, y, width, height, "Click Me")

        # In game loop:
        button.draw(screen)
        if button.is_clicked(mouse_pos, mouse_pressed):
            print("Button clicked!")
    """

    def __init__(self, x, y, width, height, text, font_size=36):
        """
        Create a button

        Args:
            x, y: Position of top-left corner
            width, height: Button size
            text: Text to display on button
            font_size: Size of text
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)

        # State
        self.hovered = False
        self.pressed = False
        self.was_pressed = False  # Track previous frame

        # Colors
        self.color_idle = BUTTON_IDLE
        self.color_hover = BUTTON_HOVER
        self.color_pressed = BUTTON_PRESSED
        self.text_color = WHITE
        self.border_color = GOLD

    def draw(self, screen):
        """Draw the button on screen"""
        # Determine color based on state
        if self.pressed:
            color = self.color_pressed
        elif self.hovered:
            color = self.color_hover
        else:
            color = self.color_idle

        # Draw button rectangle
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        # Draw border
        pygame.draw.rect(screen, self.border_color, self.rect, width=3, border_radius=10)

        # Draw text centered on button
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        """
        Check if button was clicked (released after being pressed)

        Args:
            mouse_pos: Tuple of (x, y) mouse position
            mouse_pressed: Tuple of mouse button states from pygame.mouse.get_pressed()

        Returns:
            True if button was clicked this frame
        """
        is_over = self.rect.collidepoint(mouse_pos)
        is_mouse_down = mouse_pressed[0]

        # Detect click on release
        clicked = False
        if is_over and self.was_pressed and not is_mouse_down:
            clicked = True

        # Update pressed state
        self.pressed = is_over and is_mouse_down
        self.was_pressed = self.pressed

        return clicked
