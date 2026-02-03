"""
Slot Machine Engine
Handles spinning reels and calculating payouts
"""

import random
from shared.random_utils import get_random_int, random_float
from slot_machine.config import REEL_STRIPS, PAYOUTS, VISIBLE_ROWS, PITY_TIERS, PAYLINE_PATTERNS, FULL_SCREEN_PAYOUTS


class SlotEngine:
    """
    Core slot machine logic

    Usage:
        engine = SlotEngine()
        result = engine.spin(bet_amount=10)
        print(result['payout'])
    """

    def __init__(self):
        """Initialize slot engine with reel strips"""
        self.reel_strips = REEL_STRIPS
        self.num_reels = len(REEL_STRIPS)

        # Pity system: track consecutive losses
        self.losing_streak = 0

    def spin(self, bet_amount):
        """
        Execute a spin and calculate results

        Args:
            bet_amount: Amount wagered on this spin

        Returns:
            dict with keys:
                - symbols: 2D list of visible symbols [reel][row]
                - paylines: List of 3 paylines (top, middle, bottom)
                - line_results: Per-line match and payout details
                - payout: Total payout across all lines
                - win: Boolean indicating if any line won
        """
        # Check if pity system should trigger
        pity_result = self._check_pity()
        if pity_result:
            stop_positions = self._get_pity_stops(pity_result)
        else:
            stop_positions = self._get_random_stops()

        # Get visible symbols for each reel
        symbols = self._get_visible_symbols(stop_positions)

        # Check all paylines from pattern definitions
        total_payout = 0
        line_results = []

        for name, rows in PAYLINE_PATTERNS:
            payline = [symbols[reel][rows[reel]] for reel in range(self.num_reels)]
            matches = self._calculate_matches(payline)
            payout = self._calculate_payout(matches, bet_amount)
            line_results.append({
                'name': name,
                'rows': rows,
                'payline': payline,
                'matches': matches,
                'payout': payout,
            })
            total_payout += payout

        # Check full screen bonus (all 15 symbols identical)
        full_screen_symbol = self._check_full_screen(symbols)
        full_screen_payout = 0
        if full_screen_symbol:
            full_screen_payout = FULL_SCREEN_PAYOUTS.get(full_screen_symbol, 0) * bet_amount
            total_payout += full_screen_payout

        # Update losing streak
        if total_payout > 0:
            self.losing_streak = 0
        else:
            self.losing_streak += 1

        return {
            'symbols': symbols,
            'line_results': line_results,
            'payout': total_payout,
            'win': total_payout > 0,
            'bet': bet_amount,
            'stop_positions': stop_positions,
            'full_screen': full_screen_symbol,
            'full_screen_payout': full_screen_payout,
        }

    def _check_pity(self):
        """
        Check if a pity win should trigger based on losing streak.
        Returns list of eligible symbols if triggered, None otherwise.

        Uses tiered probability: longer streaks = higher chance + better symbols.
        """
        # Walk tiers in reverse to find the highest applicable tier
        for min_losses, chance, symbols in reversed(PITY_TIERS):
            if self.losing_streak >= min_losses:
                if random_float(0, 1) < chance:
                    return symbols
                return None  # Failed the roll, no lower tier applies
        return None

    def _get_random_stops(self):
        """Get random stop position for each reel"""
        stops = []
        for reel_strip in self.reel_strips:
            max_pos = len(reel_strip) - 1
            stops.append(get_random_int(0, max_pos))
        return stops

    def _get_pity_stops(self, eligible_symbols):
        """
        Force a 3-of-a-kind win using one of the eligible symbols.
        Finds stop positions where the first 3 reels share the same payline symbol.
        """
        target_symbol = random.choice(eligible_symbols)

        stops = []
        for i in range(self.num_reels):
            reel_strip = self.reel_strips[i]

            if i < 3:
                # First 3 reels: find a position where target is on the payline
                # Payline is row 1, so we need reel_strip[(stop + 1) % len] == target
                candidates = []
                for pos in range(len(reel_strip)):
                    payline_pos = (pos + 1) % len(reel_strip)
                    if reel_strip[payline_pos] == target_symbol:
                        candidates.append(pos)

                stops.append(random.choice(candidates))
            else:
                # Reels 4-5: random (avoids giving 4 or 5 of a kind for free)
                max_pos = len(reel_strip) - 1
                stops.append(get_random_int(0, max_pos))

        return stops

    def _get_visible_symbols(self, stop_positions):
        """
        Get the visible symbols for each reel based on stop positions

        Returns 2D list: symbols[reel_index][row_index]
        """
        symbols = []

        for reel_index, stop_pos in enumerate(stop_positions):
            reel_strip = self.reel_strips[reel_index]
            reel_length = len(reel_strip)

            # Get 3 visible symbols (wrapping around if needed)
            visible = []
            for row in range(VISIBLE_ROWS):
                pos = (stop_pos + row) % reel_length
                visible.append(reel_strip[pos])

            symbols.append(visible)

        return symbols

    def _calculate_matches(self, payline):
        """
        Calculate matching symbols on payline
        Any 3+ of the same symbol counts as a win regardless of position

        Args:
            payline: List of 5 symbols (one from each reel)

        Returns:
            dict: {symbol: count} for the best match
        """
        if not payline:
            return {}

        # Count occurrences of each symbol
        counts = {}
        for symbol in payline:
            counts[symbol] = counts.get(symbol, 0) + 1

        # Find the symbol with the most matches (must be 3+)
        best_symbol = None
        best_count = 0
        for symbol, count in counts.items():
            if count >= 3 and count > best_count:
                best_count = count
                best_symbol = symbol

        if best_symbol:
            return {best_symbol: best_count}

        return {}

    def _check_full_screen(self, symbols):
        """Check if all visible symbols are the same (full screen bonus)"""
        first = symbols[0][0]
        for reel in symbols:
            for symbol in reel:
                if symbol != first:
                    return None
        return first

    def _calculate_payout(self, matches, bet_amount):
        """
        Calculate payout based on matches

        Args:
            matches: Dict of {symbol: count}
            bet_amount: Amount wagered

        Returns:
            Payout amount (0 if no win)
        """
        if not matches:
            return 0

        total_payout = 0

        for symbol, count in matches.items():
            if symbol in PAYOUTS and count in PAYOUTS[symbol]:
                multiplier = PAYOUTS[symbol][count]
                total_payout += bet_amount * multiplier

        return total_payout


# Quick test
if __name__ == "__main__":
    engine = SlotEngine()

    print("Testing Slot Engine...")
    print("=" * 40)

    for i in range(5):
        result = engine.spin(10)
        print(f"\nSpin {i+1}:")
        for lr in result['line_results']:
            if lr['payout'] > 0:
                print(f"  {lr['name']}: {lr['payline']} -> ${lr['payout']}")
        if result['full_screen']:
            print(f"  FULL SCREEN: {result['full_screen']} -> ${result['full_screen_payout']}")
        print(f"  Total Payout: ${result['payout']}")
        print(f"  Win: {result['win']}")
