"""
Monte Carlo Equity Calculator
Simulates poker hands to calculate win probability
"""

import random
from poker_evaluator import Card, HandEvaluator, create_deck

class EquityCalculator:
    """Calculate hand equity using Monte Carlo simulation"""

    def __init__(self, simulations=1000):
        """
        Initialize equity calculator
        simulations: Number of Monte Carlo simulations to run (more = more accurate but slower)
        """
        self.simulations = simulations

    def calculate_equity(self, hole_cards, community_cards, num_opponents):
        """
        Calculate win probability for your hand

        Args:
            hole_cards: List of 2 Card objects (your hole cards)
            community_cards: List of Card objects (flop/turn/river cards shown)
            num_opponents: Number of opponents still in the hand

        Returns:
            Dictionary with win%, tie%, lose%, and hand analysis
        """
        if len(hole_cards) != 2:
            raise ValueError("Must have exactly 2 hole cards")

        wins = 0
        ties = 0
        losses = 0

        # Create available cards (deck minus known cards)
        known_cards = set(hole_cards + community_cards)
        available_cards = [c for c in create_deck() if c not in known_cards]

        # How many community cards still to come
        cards_to_deal = 5 - len(community_cards)

        for _ in range(self.simulations):
            # Shuffle available cards
            random.shuffle(available_cards)

            # Complete the board
            simulated_board = community_cards + available_cards[:cards_to_deal]

            # Deal opponent hands
            opponent_cards_start = cards_to_deal
            opponent_hands = []

            for i in range(num_opponents):
                opp_hole = available_cards[opponent_cards_start + i*2:opponent_cards_start + i*2 + 2]
                opponent_hands.append(opp_hole)

            # Evaluate your hand
            your_hand = HandEvaluator.evaluate_hand(hole_cards, simulated_board)

            # Evaluate opponent hands
            opponent_evals = [
                HandEvaluator.evaluate_hand(opp_hole, simulated_board)
                for opp_hole in opponent_hands
            ]

            # Compare hands
            result = self._compare_hands(your_hand, opponent_evals)

            if result == 'win':
                wins += 1
            elif result == 'tie':
                ties += 1
            else:
                losses += 1

        # Calculate percentages
        total = self.simulations
        win_pct = (wins / total) * 100
        tie_pct = (ties / total) * 100
        lose_pct = (losses / total) * 100

        # Evaluate current hand (with current board)
        current_hand_name, current_rank, _ = HandEvaluator.evaluate_hand(hole_cards, community_cards)

        return {
            'win_pct': round(win_pct, 1),
            'tie_pct': round(tie_pct, 1),
            'lose_pct': round(lose_pct, 1),
            'equity': round(win_pct + tie_pct/2, 1),  # Equity = win% + tie%/2
            'current_hand': current_hand_name,
            'hand_strength': HandEvaluator.hand_strength_category(current_hand_name)
        }

    def _compare_hands(self, your_hand, opponent_hands):
        """
        Compare your hand against opponent hands
        Returns: 'win', 'tie', or 'lose'
        """
        your_rank, your_tiebreakers = your_hand[1], your_hand[2]

        better_hands = 0
        tied_hands = 0

        for opp_hand in opponent_hands:
            opp_rank, opp_tiebreakers = opp_hand[1], opp_hand[2]

            if opp_rank > your_rank:
                better_hands += 1
            elif opp_rank == your_rank:
                # Compare tiebreakers
                if opp_tiebreakers > your_tiebreakers:
                    better_hands += 1
                elif opp_tiebreakers == your_tiebreakers:
                    tied_hands += 1

        if better_hands > 0:
            return 'lose'
        elif tied_hands > 0:
            return 'tie'
        else:
            return 'win'

    def quick_equity(self, hole_cards, community_cards, num_opponents, simulations=500):
        """Faster equity calculation with fewer simulations (for real-time updates)"""
        old_sims = self.simulations
        self.simulations = simulations
        result = self.calculate_equity(hole_cards, community_cards, num_opponents)
        self.simulations = old_sims
        return result
