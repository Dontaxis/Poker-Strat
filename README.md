# 🃏 Poker Strategy Advisor

A real-time poker strategy advisor designed for 4-handed Texas Hold'em games. Built specifically for **Pythonista 3 on iPad**, this app helps you make optimal decisions during fast-paced poker games with your friends.

## ✨ Features

### Core Functionality
- **Real-time Hand Analysis** - Calculate win probability using Monte Carlo simulation
- **Strategic Recommendations** - Get actionable advice (Fold/Call/Raise/Check) based on:
  - Hand strength and equity
  - Position at the table
  - Number of active opponents
  - Current betting round (pre-flop, flop, turn, river)
  - Opponent playing tendencies

### 4-Handed Optimization
- Aggressive ranges optimized for short-handed play
- Position-aware strategy (Button, Cutoff, Small Blind, Big Blind)
- Automatic position rotation between hands
- Multi-way vs heads-up adjustments

### Opponent Tracking
- **Tightness Slider** - Adjust for loose (plays many hands) vs tight (plays few hands) opponents
- **Aggression Slider** - Adjust for passive (calls often) vs aggressive (raises often) opponents
- **Live Updates** - Strategy adapts in real-time as you adjust opponent tendencies

### Fast, Touch-Optimized UI
- Large button grid for quick card selection
- Single-tap card input for hole cards and community cards
- Clear visual display of:
  - Your hole cards
  - Community cards (flop, turn, river)
  - Current position and street
  - Win probability percentage
  - Hand strength evaluation
  - Strategic recommendation

## 📱 Installation

### For Pythonista 3 (iPad)

1. **Download Files** - Transfer all Python files to Pythonista:
   - `poker_advisor.py` (main app)
   - `poker_evaluator.py` (hand evaluation)
   - `equity_calculator.py` (Monte Carlo simulation)
   - `strategy_engine.py` (strategy logic)

2. **Run the App**:
   - Open Pythonista 3
   - Navigate to `poker_advisor.py`
   - Tap the ▶️ Run button
   - The app will launch in fullscreen mode

## 🎮 How to Use

### Starting a New Hand

1. **Set Your Position** - Tap the position button (BTN/SB/BB/CO) to set your initial position
   - The position will auto-rotate after each new hand

2. **Input Hole Cards**:
   - Tap the first hole card slot
   - Select your card from the grid (organized by suit)
   - Tap the second hole card slot
   - Select your second card
   - **Win probability displays immediately** for pre-flop

3. **Set Number of Opponents** - Use the +/- buttons to adjust how many opponents are still in the hand

4. **Facing a Bet?** - Toggle the "Facing Bet" switch if someone has bet or raised

### During the Hand

#### The Flop (3 Community Cards)
1. Tap each of the first three community card slots
2. Select the flop cards from the grid
3. **Win probability updates automatically** with Monte Carlo simulation
4. Review the new recommendation

#### The Turn (4th Community Card)
1. Tap the fourth community card slot
2. Select the turn card
3. Win probability recalculates
4. Check updated strategy

#### The River (5th Community Card)
1. Tap the fifth community card slot
2. Select the river card
3. Get final win probability and recommendation

### Adjusting Opponent Tendencies

1. Tap **⚙️ Opponent Settings**
2. Adjust sliders:
   - **LOOSE ← → TIGHT**: How wide is their hand range?
   - **PASSIVE ← → AGGRESSIVE**: How often do they bet/raise vs call?
3. Tap **✓ Save & Apply**
4. Strategy recalculates immediately with new adjustments

### Starting a New Hand

1. Tap **🔄 New Hand**
2. Position automatically rotates (dealer button moves)
3. All cards clear
4. Ready for next hand!

## 🎯 Understanding Recommendations

### Action Types

- **RAISE** - You should bet or raise (strong hand or good bluffing spot)
- **CALL** - Match the current bet (good odds to continue)
- **CHECK** - Don't bet if possible (marginal hand, see free card)
- **FOLD** - Give up the hand (insufficient equity to continue)
- **FOLD/CHECK** - Fold if facing a bet, check if no bet
- **CALL/CHECK** - Call a small bet or check if free

### Win Probability Colors

- 🟢 **Green (60%+)** - Strong hand, usually raise for value
- 🟡 **Yellow (40-60%)** - Marginal hand, position matters
- 🟠 **Orange (<40%)** - Weak hand, usually fold unless bluffing

### Position Indicators

- **BTN (Button)** ⚡ - Best position, play aggressively
- **CO (Cutoff)** - Second-best position, still strong
- **BB (Big Blind)** - Neutral position, already invested
- **SB (Small Blind)** ⚠️ - Worst position, play cautiously

## 🧮 Strategy Philosophy

This advisor uses **game theory optimal (GTO) concepts** adapted for 4-handed play:

### Pre-flop
- Much wider opening ranges than full-ring games
- Position is critical - play ~60% of hands on the button
- Aggressive 3-betting strategy
- Consider opponent tendencies for adjustments

### Post-flop
- **Equity calculation** via Monte Carlo simulation (500-1000 trials)
- Pot odds and implied odds considerations
- Multi-way pots require stronger hands
- Aggression increases in position

### Opponent Adjustments
- **vs Tight Players**: Bluff more, steal more pots
- **vs Loose Players**: Value bet more, bluff less
- **vs Aggressive Players**: Call down lighter, trap more
- **vs Passive Players**: Bet more often, build bigger pots

## 🔧 Technical Details

### Poker Hand Evaluation
- Evaluates all 5-card combinations from 7 cards
- Standard hand rankings (Royal Flush → High Card)
- Tie-breaker logic for identical hand types

### Monte Carlo Simulation
- Simulates 500-1000 random outcomes
- Accounts for:
  - Unknown opponent hole cards
  - Remaining community cards
  - Multiple opponent scenarios
- Provides win%, tie%, and lose% probabilities

### Strategy Engine
- Position-based multipliers
- Opponent tendency adjustments
- Street-specific recommendations
- 4-handed range optimization

## 💡 Pro Tips

1. **Speed is Key** - The card grid is optimized for quick taps during live play
2. **Update Opponents** - Adjust tendencies mid-session as you learn how friends play
3. **Trust Position** - The button is gold in 4-handed; play aggressively
4. **Watch Opponent Count** - Strategy changes dramatically between heads-up and 3-way
5. **Use "Facing Bet"** - Don't forget to toggle this for accurate recommendations
6. **Multi-way Pots** - Tighten up when multiple opponents are in the hand

## 🎓 Learning Mode

This tool is also great for **learning poker strategy**:
- See how equity changes from flop → turn → river
- Understand how position affects playable hands
- Learn which hands are strong pre-flop
- Develop intuition for pot odds and equity

## 📊 Example Walkthrough

**Scenario**: You're on the Button with A♥K♠

1. Select position: BTN ⚡
2. Input cards: A♥, K♠
3. Pre-flop strength: ~72% (STRONG)
4. Recommendation: **RAISE** - "Strong hand with position, be aggressive"

**Flop**: J♥ 9♠ 2♦

5. Input flop cards
6. Win probability vs 2 opponents: 58%
7. Current hand: High Card
8. Recommendation: **RAISE** - "Good equity, bet for value and protection"

**Turn**: K♦

9. Input turn card
10. Win probability: 78%
11. Current hand: One Pair (Kings)
12. Recommendation: **RAISE** - "Strong hand, bet for value"

**River**: 3♣

13. Input river card
14. Win probability: 82%
15. Recommendation: **RAISE** - "Strong hand, extract value"

## 🤝 Responsible Gaming

This tool is designed to help you:
- ✅ Learn poker strategy
- ✅ Make better decisions with friends
- ✅ Understand hand equity and odds

**Remember**: Poker should be fun! Use this tool to improve your game, not to take advantage of casual players.

## 📝 Credits

Built with:
- Python 3
- Pythonista 3 UI framework
- Monte Carlo simulation algorithms
- Game theory optimal poker concepts

---

**Good luck at the tables! 🃏♠️♥️♦️♣️**
