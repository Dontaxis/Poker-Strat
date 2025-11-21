"""
Poker Hand Evaluator
Evaluates Texas Hold'em poker hands and calculates hand strength
"""

from collections import Counter
from itertools import combinations

class Card:
    """Represents a playing card"""
    RANKS = '23456789TJQKA'
    SUITS = 'hdcs'  # hearts, diamonds, clubs, spades

    def __init__(self, rank, suit):
        self.rank = rank.upper()
        self.suit = suit.lower()
        self.rank_value = self.RANKS.index(self.rank)

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

class HandEvaluator:
    """Evaluates poker hands and determines winner"""

    # Hand rankings (higher is better)
    HAND_RANKINGS = {
        'Royal Flush': 10,
        'Straight Flush': 9,
        'Four of a Kind': 8,
        'Full House': 7,
        'Flush': 6,
        'Straight': 5,
        'Three of a Kind': 4,
        'Two Pair': 3,
        'One Pair': 2,
        'High Card': 1
    }

    @staticmethod
    def evaluate_hand(hole_cards, community_cards):
        """
        Evaluate the best 5-card hand from hole cards + community cards
        Returns: (hand_name, hand_rank, tiebreakers)
        """
        all_cards = hole_cards + community_cards

        if len(all_cards) < 5:
            return ('Incomplete Hand', 0, [])

        # Find best 5-card combination
        best_hand = None
        best_rank = 0
        best_tiebreakers = []

        for five_cards in combinations(all_cards, 5):
            hand_name, rank, tiebreakers = HandEvaluator._evaluate_five_cards(list(five_cards))

            # Compare hands
            if rank > best_rank or (rank == best_rank and tiebreakers > best_tiebreakers):
                best_hand = hand_name
                best_rank = rank
                best_tiebreakers = tiebreakers

        return (best_hand, best_rank, best_tiebreakers)

    @staticmethod
    def _evaluate_five_cards(cards):
        """Evaluate a specific 5-card hand"""
        ranks = sorted([c.rank_value for c in cards], reverse=True)
        suits = [c.suit for c in cards]
        rank_counts = Counter(ranks)

        is_flush = len(set(suits)) == 1
        is_straight = HandEvaluator._is_straight(ranks)

        # Royal Flush
        if is_flush and is_straight and ranks[0] == 12:  # Ace high
            return ('Royal Flush', 10, ranks)

        # Straight Flush
        if is_flush and is_straight:
            return ('Straight Flush', 9, ranks)

        # Four of a Kind
        if 4 in rank_counts.values():
            quad = [r for r, c in rank_counts.items() if c == 4][0]
            kicker = [r for r in ranks if r != quad][0]
            return ('Four of a Kind', 8, [quad, kicker])

        # Full House
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            trips = [r for r, c in rank_counts.items() if c == 3][0]
            pair = [r for r, c in rank_counts.items() if c == 2][0]
            return ('Full House', 7, [trips, pair])

        # Flush
        if is_flush:
            return ('Flush', 6, ranks)

        # Straight
        if is_straight:
            return ('Straight', 5, ranks)

        # Three of a Kind
        if 3 in rank_counts.values():
            trips = [r for r, c in rank_counts.items() if c == 3][0]
            kickers = sorted([r for r in ranks if r != trips], reverse=True)
            return ('Three of a Kind', 4, [trips] + kickers)

        # Two Pair
        pairs = [r for r, c in rank_counts.items() if c == 2]
        if len(pairs) == 2:
            pairs = sorted(pairs, reverse=True)
            kicker = [r for r in ranks if r not in pairs][0]
            return ('Two Pair', 3, pairs + [kicker])

        # One Pair
        if len(pairs) == 1:
            pair = pairs[0]
            kickers = sorted([r for r in ranks if r != pair], reverse=True)
            return ('One Pair', 2, [pair] + kickers)

        # High Card
        return ('High Card', 1, ranks)

    @staticmethod
    def _is_straight(ranks):
        """Check if ranks form a straight"""
        # Check regular straight
        if ranks[0] - ranks[4] == 4 and len(set(ranks)) == 5:
            return True

        # Check wheel (A-2-3-4-5)
        if sorted(ranks) == [0, 1, 2, 3, 12]:
            return True

        return False

    @staticmethod
    def hand_strength_category(hand_name):
        """Return a category for UI display"""
        rank = HandEvaluator.HAND_RANKINGS.get(hand_name, 0)

        if rank >= 8:
            return "MONSTER"
        elif rank >= 6:
            return "STRONG"
        elif rank >= 4:
            return "DECENT"
        elif rank >= 2:
            return "WEAK"
        else:
            return "VERY WEAK"


def create_deck():
    """Create a standard 52-card deck"""
    return [Card(rank, suit) for rank in Card.RANKS for suit in Card.SUITS]


def parse_card(card_str):
    """Parse a card string like 'Ah' into a Card object"""
    if len(card_str) != 2:
        raise ValueError(f"Invalid card string: {card_str}")
    return Card(card_str[0], card_str[1])
