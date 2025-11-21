"""
Test script to verify poker logic works correctly
"""

from poker_evaluator import Card, HandEvaluator, parse_card
from equity_calculator import EquityCalculator
from strategy_engine import StrategyEngine

def test_hand_evaluator():
    """Test hand evaluation"""
    print("=" * 50)
    print("TESTING HAND EVALUATOR")
    print("=" * 50)

    # Test Royal Flush
    hole = [Card('A', 'h'), Card('K', 'h')]
    board = [Card('Q', 'h'), Card('J', 'h'), Card('T', 'h')]
    hand_name, rank, _ = HandEvaluator.evaluate_hand(hole, board)
    print(f"✓ Royal Flush test: {hand_name} (rank: {rank})")
    assert hand_name == "Royal Flush", "Royal Flush not detected"

    # Test Full House
    hole = [Card('A', 'h'), Card('A', 's')]
    board = [Card('A', 'd'), Card('K', 'h'), Card('K', 's')]
    hand_name, rank, _ = HandEvaluator.evaluate_hand(hole, board)
    print(f"✓ Full House test: {hand_name} (rank: {rank})")
    assert hand_name == "Full House", "Full House not detected"

    # Test One Pair
    hole = [Card('7', 'h'), Card('2', 's')]
    board = [Card('7', 'd'), Card('K', 'h'), Card('9', 's')]
    hand_name, rank, _ = HandEvaluator.evaluate_hand(hole, board)
    print(f"✓ One Pair test: {hand_name} (rank: {rank})")
    assert hand_name == "One Pair", "One Pair not detected"

    print("\n✅ All hand evaluator tests passed!\n")


def test_equity_calculator():
    """Test equity calculation"""
    print("=" * 50)
    print("TESTING EQUITY CALCULATOR")
    print("=" * 50)

    calc = EquityCalculator(simulations=1000)

    # Test pocket aces pre-flop
    hole = [Card('A', 'h'), Card('A', 's')]
    board = []
    result = calc.quick_equity(hole, board, num_opponents=3, simulations=500)

    print(f"✓ Pocket Aces (AA) pre-flop vs 3 opponents:")
    print(f"  Win%: {result['win_pct']}%")
    print(f"  Equity: {result['equity']}%")
    print(f"  Hand: {result['current_hand']}")

    # Should have good equity with AA
    assert result['win_pct'] > 30, "AA should have >30% equity vs 3 opponents"

    # Test strong flop
    hole = [Card('A', 'h'), Card('K', 'h')]
    board = [Card('A', 's'), Card('K', 'd'), Card('2', 'c')]  # Two pair
    result = calc.quick_equity(hole, board, num_opponents=2, simulations=500)

    print(f"\n✓ Two Pair (AK on AK2 board) vs 2 opponents:")
    print(f"  Win%: {result['win_pct']}%")
    print(f"  Current hand: {result['current_hand']}")
    print(f"  Strength: {result['hand_strength']}")

    # Should have very good equity with two pair
    assert result['win_pct'] > 50, "Two pair should have >50% equity"

    print("\n✅ All equity calculator tests passed!\n")


def test_strategy_engine():
    """Test strategy recommendations"""
    print("=" * 50)
    print("TESTING STRATEGY ENGINE")
    print("=" * 50)

    strategy = StrategyEngine()

    # Test pre-flop hand strength
    hole_aa = [Card('A', 'h'), Card('A', 's')]
    strength_aa = strategy.get_preflop_hand_strength(hole_aa)
    print(f"✓ Pre-flop strength AA: {strength_aa}")
    assert strength_aa > 80, "AA should have high pre-flop strength"

    hole_72 = [Card('7', 'h'), Card('2', 's')]
    strength_72 = strategy.get_preflop_hand_strength(hole_72)
    print(f"✓ Pre-flop strength 72o: {strength_72}")
    assert strength_72 < 40, "72o should have low pre-flop strength"

    # Test strategy recommendation with strong hand
    equity_data = {
        'equity': 75,
        'win_pct': 75,
        'tie_pct': 0,
        'lose_pct': 25,
        'current_hand': 'Two Pair',
        'hand_strength': 'STRONG'
    }

    rec = strategy.get_recommendation(
        equity_data,
        position='BTN',
        num_opponents=2,
        street='flop',
        facing_bet=False
    )

    print(f"\n✓ Strong hand recommendation:")
    print(f"  Action: {rec['action']}")
    print(f"  Equity: {rec['equity']}%")
    print(f"  Adjusted equity: {rec['adjusted_equity']}%")

    assert 'RAISE' in rec['action'], "Should recommend RAISE with strong hand"

    # Test opponent tendency adjustment
    strategy.update_opponent_tendencies(tightness=0.8, aggression=0.7)
    rec2 = strategy.get_recommendation(
        equity_data,
        position='BTN',
        num_opponents=2,
        street='flop',
        facing_bet=False
    )

    print(f"\n✓ Recommendation vs tight-aggressive opponents:")
    print(f"  Action: {rec2['action']}")
    print(f"  Adjusted equity: {rec2['adjusted_equity']}%")

    print("\n✅ All strategy engine tests passed!\n")


def test_full_hand_scenario():
    """Test a complete hand from pre-flop to river"""
    print("=" * 50)
    print("TESTING FULL HAND SCENARIO")
    print("=" * 50)
    print("Scenario: You have A♥K♠ on the Button\n")

    calc = EquityCalculator(simulations=500)
    strategy = StrategyEngine()

    # Your hole cards
    hole = [Card('A', 'h'), Card('K', 's')]

    # Pre-flop
    print("PRE-FLOP:")
    preflop_strength = strategy.get_preflop_hand_strength(hole)
    print(f"  Hand strength: {preflop_strength}%")

    # Flop: J♥ 9♠ 2♦
    print("\nFLOP: J♥ 9♠ 2♦")
    board_flop = [Card('J', 'h'), Card('9', 's'), Card('2', 'd')]
    result_flop = calc.quick_equity(hole, board_flop, num_opponents=2, simulations=300)
    print(f"  Win%: {result_flop['win_pct']}%")
    print(f"  Current hand: {result_flop['current_hand']}")

    rec_flop = strategy.get_recommendation(
        result_flop,
        position='BTN',
        num_opponents=2,
        street='flop',
        facing_bet=False
    )
    print(f"  Recommendation: {rec_flop['action']}")

    # Turn: K♦
    print("\nTURN: K♦ (board: J♥ 9♠ 2♦ K♦)")
    board_turn = board_flop + [Card('K', 'd')]
    result_turn = calc.quick_equity(hole, board_turn, num_opponents=2, simulations=300)
    print(f"  Win%: {result_turn['win_pct']}%")
    print(f"  Current hand: {result_turn['current_hand']}")

    rec_turn = strategy.get_recommendation(
        result_turn,
        position='BTN',
        num_opponents=2,
        street='turn',
        facing_bet=False
    )
    print(f"  Recommendation: {rec_turn['action']}")

    # River: 3♣
    print("\nRIVER: 3♣ (board: J♥ 9♠ 2♦ K♦ 3♣)")
    board_river = board_turn + [Card('3', 'c')]
    result_river = calc.quick_equity(hole, board_river, num_opponents=2, simulations=300)
    print(f"  Win%: {result_river['win_pct']}%")
    print(f"  Current hand: {result_river['current_hand']}")

    rec_river = strategy.get_recommendation(
        result_river,
        position='BTN',
        num_opponents=2,
        street='river',
        facing_bet=False
    )
    print(f"  Recommendation: {rec_river['action']}")

    print("\n✅ Full hand scenario test completed!\n")


if __name__ == '__main__':
    print("\n🃏 POKER STRATEGY ADVISOR - LOGIC TESTS 🃏\n")

    try:
        test_hand_evaluator()
        test_equity_calculator()
        test_strategy_engine()
        test_full_hand_scenario()

        print("=" * 50)
        print("✅ ALL TESTS PASSED SUCCESSFULLY! ✅")
        print("=" * 50)
        print("\nThe poker logic is working correctly.")
        print("Ready to run on Pythonista 3!\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
