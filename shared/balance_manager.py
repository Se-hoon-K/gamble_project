"""
Balance Manager - Handles in-game currency
Works with SaveManager for persistence
"""

from shared.save_manager import SaveManager


class BalanceManager:
    """
    Manages player balance during gameplay
    Auto-saves after each transaction

    Usage:
        balance = BalanceManager()
        balance.deduct(10)  # Bet $10
        balance.add(25)     # Win $25
    """

    def __init__(self, save_manager=None):
        """
        Initialize balance manager

        Args:
            save_manager: SaveManager instance (creates new if None)
        """
        self.save_manager = save_manager or SaveManager()
        self._balance = self.save_manager.get_balance()

    def get_balance(self):
        """Get current balance"""
        return self._balance

    def add(self, amount):
        """
        Add money to balance

        Args:
            amount: Amount to add (must be positive)
        """
        if amount < 0:
            raise ValueError("Amount must be positive. Use deduct() to remove money.")

        self._balance += amount
        self._sync_save()

    def deduct(self, amount):
        """
        Remove money from balance

        Args:
            amount: Amount to remove (must be positive)

        Returns:
            True if successful, False if insufficient funds
        """
        if amount < 0:
            raise ValueError("Amount must be positive.")

        if not self.can_afford(amount):
            return False

        self._balance -= amount
        self._sync_save()
        return True

    def can_afford(self, amount):
        """Check if player has enough balance"""
        return self._balance >= amount

    def set_balance(self, amount):
        """Set balance to specific amount (for admin/testing)"""
        self._balance = amount
        self._sync_save()

    def _sync_save(self):
        """Sync balance to save manager"""
        self.save_manager.set_balance(self._balance)
        self.save_manager.save()
