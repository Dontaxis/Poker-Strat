"""
Strategy Engine
Provides poker strategy recommendations based on hand strength, position, and opponent tendencies
"""

from poker_evaluator import Card

class StrategyEngine:
    """Generate strategy recommendations for 4-handed Texas Hold'em"""

    # Position values (4-handed)
    POSITIONS = ['SB', 'BB', 'BTN', 'CO']  # Small Blind, Big Blind, Button, Cutoff

    def __init__(self):
        self.opponent_tightness = 0.5  # 0 = very loose, 1 = very tight
        self.opponent_aggression = 0.5  # 0 = very passive, 1 = very aggressive

    def update_opponent_tendencies(self, tightness, aggression):
        """
        Update opponent playing tendencies
        tightness: 0.0 (loose) to 1.0 (tight)
        aggression: 0.0 (passive) to 1.0 (aggressive)
        """
        self.opponent_tightness = max(0.0, min(1.0, tightness))
        self.opponent_aggression = max(0.0, min(1.0, aggression))

    def get_recommendation(self, equity_data, position, num_opponents, street, facing_bet=False):
        """
        Get strategy recommendation

        Args:
            equity_data: Dictionary from EquityCalculator
            position: Player position ('SB', 'BB', 'BTN', 'CO')
            num_opponents: Number of opponents still in hand
            street: 'preflop', 'flop', 'turn', 'river'
            facing_bet: Whether you're facing a bet/raise

        Returns:
            Dictionary with recommendation and reasoning
        """
        equity = equity_data['equity']
        win_pct = equity_data['win_pct']
        current_hand = equity_data['current_hand']

        # Position strength (BTN and CO are stronger in 4-handed)
        position_strength = self._get_position_strength(position)

        # Adjust equity based on position
        adjusted_equity = equity + position_strength

        # Adjust for opponent tendencies
        if self.opponent_tightness > 0.6:
            # Against tight players, be more aggressive (they fold more)
            adjusted_equity += 5
        elif self.opponent_tightness < 0.4:
            # Against loose players, tighten up (they call more)
            adjusted_equity -= 5

        if self.opponent_aggression > 0.6 and facing_bet:
            # Against aggressive players when facing a bet, need stronger hands
            adjusted_equity -= 8
        elif self.opponent_aggression < 0.4 and facing_bet:
            # Against passive players, can be more aggressive
            adjusted_equity += 3

        # Get base recommendation
        if facing_bet:
            action, reasoning = self._recommend_facing_bet(adjusted_equity, win_pct, street, num_opponents)
        else:
            action, reasoning = self._recommend_no_bet(adjusted_equity, win_pct, street, position, num_opponents)

        # Add context to reasoning
        full_reasoning = self._build_reasoning(
            reasoning, equity, win_pct, current_hand, position,
            num_opponents, street, facing_bet
        )

        return {
            'action': action,
            'reasoning': full_reasoning,
            'equity': equity,
            'adjusted_equity': round(adjusted_equity, 1),
            'hand_strength': equity_data['hand_strength']
        }

    def _get_position_strength(self, position):
        """Get position advantage modifier"""
        # In 4-handed, position is critical
        position_values = {
            'BTN': 8,   # Button is best position
            'CO': 5,    # Cutoff (2nd to act) is good
            'SB': -3,   # Small blind is worst position
            'BB': 0     # Big blind is neutral (already invested)
        }
        return position_values.get(position, 0)

    def _recommend_facing_bet(self, adjusted_equity, win_pct, street, num_opponents):
        """Recommend action when facing a bet"""

        # Aggressive thresholds for 4-handed play
        if adjusted_equity >= 55:
            return 'RAISE', 'Strong hand, raise for value'
        elif adjusted_equity >= 45:
            if street == 'preflop':
                return 'CALL', 'Good equity, call to see flop'
            else:
                return 'CALL', 'Decent equity, call to see next card'
        elif adjusted_equity >= 35:
            if street == 'river':
                return 'FOLD', 'Not enough equity on river'
            else:
                return 'CALL', 'Marginal hand, but has potential'
        else:
            return 'FOLD', 'Insufficient equity to continue'

    def _recommend_no_bet(self, adjusted_equity, win_pct, street, position, num_opponents):
        """Recommend action when no bet to you"""

        # Very aggressive 4-handed strategy
        if adjusted_equity >= 55:
            return 'RAISE', 'Strong hand, bet for value'
        elif adjusted_equity >= 40:
            if position in ['BTN', 'CO']:
                return 'RAISE', 'Good hand with position, be aggressive'
            else:
                return 'CALL/CHECK', 'Good hand, can call or check'
        elif adjusted_equity >= 30:
            if position == 'BTN' and street == 'preflop':
                return 'RAISE', 'Button steal opportunity'
            else:
                return 'CHECK', 'Marginal hand, see free card'
        else:
            if position == 'BTN' and num_opponents == 1 and street == 'preflop':
                return 'RAISE', 'Heads-up on button, stay aggressive'
            else:
                return 'FOLD/CHECK', 'Weak hand, fold if bet or check if free'

    def _build_reasoning(self, base_reasoning, equity, win_pct, hand, position, opponents, street, facing_bet):
        """Build detailed reasoning string"""
        parts = [base_reasoning]

        # Add equity info
        parts.append(f"Win probability: {win_pct}%")
        parts.append(f"Current hand: {hand}")

        # Position context
        if position == 'BTN':
            parts.append("⚡ Button advantage - play aggressive")
        elif position == 'SB':
            parts.append("⚠ Out of position - be cautious")

        # Opponent count context
        if opponents == 1:
            parts.append("🎯 Heads-up - widen your range")
        elif opponents == 3:
            parts.append("👥 Multi-way - need stronger hands")

        # Street-specific advice
        if street == 'preflop':
            parts.append("Pre-flop: Position is key")
        elif street == 'flop':
            parts.append("Flop: Evaluate draws and pairs")
        elif street == 'turn':
            parts.append("Turn: Pot is getting bigger")
        elif street == 'river':
            parts.append("River: No more cards coming")

        # Opponent tendency hints
        if self.opponent_tightness > 0.6:
            parts.append("💡 Opponents playing tight - bluff more")
        elif self.opponent_tightness < 0.4:
            parts.append("💡 Opponents playing loose - value bet more")

        if self.opponent_aggression > 0.6 and facing_bet:
            parts.append("💡 Facing aggression - need solid hand")

        return "\n".join(parts)

    def get_preflop_hand_strength(self, hole_cards):
        """
        Quick pre-flop hand strength evaluation for UI feedback
        Returns a score 0-100
        """
        if len(hole_cards) != 2:
            return 0

        c1, c2 = hole_cards[0], hole_cards[1]
        r1, r2 = c1.rank_value, c2.rank_value

        # Pocket pairs
        if r1 == r2:
            score = 50 + (r1 * 3)  # AA=89, KK=86, etc.
            return min(100, score)

        # High cards
        high = max(r1, r2)
        low = min(r1, r2)

        # Suited adds value
        suited_bonus = 5 if c1.suit == c2.suit else 0

        # Connected cards (potential straight)
        gap = abs(r1 - r2)
        if gap <= 1:
            connected_bonus = 5  # Directly connected
        elif gap == 2:
            connected_bonus = 3  # One gap
        else:
            connected_bonus = 0

        # Gap penalty for large gaps (trash hands)
        gap_penalty = 0
        if gap > 5:
            gap_penalty = 5

        # Base score from high card
        score = 15 + (high * 4) + (low * 2) + suited_bonus + connected_bonus - gap_penalty

        # Premium hands boost
        if high >= 11:  # King or Ace
            if low >= 9:  # T or better
                score += 15

        return min(100, max(0, score))
