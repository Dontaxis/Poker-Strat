"""
Poker Strategy Advisor - Main Application
Pythonista 3 optimized UI for iPad
"""

import ui
import random
from poker_evaluator import Card, HandEvaluator, parse_card
from equity_calculator import EquityCalculator
from strategy_engine import StrategyEngine

class PokerAdvisorApp:
    """Main application class for Poker Strategy Advisor"""

    def __init__(self):
        self.equity_calc = EquityCalculator(simulations=1000)
        self.strategy = StrategyEngine()

        # Game state
        self.hole_cards = []
        self.community_cards = []
        self.position = 'BTN'  # Default position
        self.num_opponents = 3
        self.street = 'preflop'
        self.facing_bet = False

        # Card selection state
        self.selecting_for = None  # 'hole1', 'hole2', 'flop1', 'flop2', 'flop3', 'turn', 'river'
        self.used_cards = set()

        # UI components
        self.main_view = None
        self.card_selector_view = None

        # Build UI
        self.build_main_ui()

    def build_main_ui(self):
        """Build the main game interface"""
        self.main_view = ui.View()
        self.main_view.name = 'Poker Strategy Advisor'
        self.main_view.background_color = '#1a472a'  # Poker table green

        # Screen dimensions
        width = 768
        height = 1024

        y_offset = 20

        # Title
        title = ui.Label()
        title.text = '♠️ POKER STRATEGY ADVISOR ♥️'
        title.font = ('<system-bold>', 24)
        title.text_color = 'white'
        title.alignment = ui.ALIGN_CENTER
        title.frame = (0, y_offset, width, 40)
        self.main_view.add_subview(title)
        y_offset += 50

        # Position and opponents section
        info_frame = ui.View()
        info_frame.background_color = '#0d2818'
        info_frame.frame = (10, y_offset, width-20, 80)
        info_frame.corner_radius = 10
        self.main_view.add_subview(info_frame)

        # Position selector
        pos_label = ui.Label()
        pos_label.text = 'Position:'
        pos_label.font = ('<system>', 16)
        pos_label.text_color = 'white'
        pos_label.frame = (10, 10, 100, 30)
        info_frame.add_subview(pos_label)

        self.position_btn = ui.Button()
        self.position_btn.title = self.position
        self.position_btn.font = ('<system-bold>', 18)
        self.position_btn.background_color = '#d4af37'
        self.position_btn.tint_color = 'black'
        self.position_btn.corner_radius = 8
        self.position_btn.frame = (110, 10, 100, 30)
        self.position_btn.action = self.cycle_position
        info_frame.add_subview(self.position_btn)

        # Opponents counter
        opp_label = ui.Label()
        opp_label.text = 'Opponents:'
        opp_label.font = ('<system>', 16)
        opp_label.text_color = 'white'
        opp_label.frame = (220, 10, 120, 30)
        info_frame.add_subview(opp_label)

        self.opp_count_label = ui.Label()
        self.opp_count_label.text = str(self.num_opponents)
        self.opp_count_label.font = ('<system-bold>', 24)
        self.opp_count_label.text_color = '#d4af37'
        self.opp_count_label.alignment = ui.ALIGN_CENTER
        self.opp_count_label.frame = (340, 5, 50, 40)
        info_frame.add_subview(self.opp_count_label)

        # Opponent +/- buttons
        opp_minus = ui.Button()
        opp_minus.title = '-'
        opp_minus.font = ('<system-bold>', 24)
        opp_minus.background_color = '#8b0000'
        opp_minus.tint_color = 'white'
        opp_minus.corner_radius = 8
        opp_minus.frame = (400, 10, 40, 30)
        opp_minus.action = lambda sender: self.adjust_opponents(-1)
        info_frame.add_subview(opp_minus)

        opp_plus = ui.Button()
        opp_plus.title = '+'
        opp_plus.font = ('<system-bold>', 24)
        opp_plus.background_color = '#006400'
        opp_plus.tint_color = 'white'
        opp_plus.corner_radius = 8
        opp_plus.frame = (450, 10, 40, 30)
        opp_plus.action = lambda sender: self.adjust_opponents(1)
        info_frame.add_subview(opp_plus)

        # Street indicator
        self.street_label = ui.Label()
        self.street_label.text = '🎴 PRE-FLOP'
        self.street_label.font = ('<system-bold>', 18)
        self.street_label.text_color = '#d4af37'
        self.street_label.alignment = ui.ALIGN_CENTER
        self.street_label.frame = (500, 10, 250, 30)
        info_frame.add_subview(self.street_label)

        # Facing bet toggle
        bet_label = ui.Label()
        bet_label.text = 'Facing Bet:'
        bet_label.font = ('<system>', 14)
        bet_label.text_color = 'white'
        bet_label.frame = (10, 50, 100, 20)
        info_frame.add_subview(bet_label)

        self.bet_switch = ui.Switch()
        self.bet_switch.value = False
        self.bet_switch.frame = (110, 45, 60, 30)
        self.bet_switch.action = self.toggle_facing_bet
        info_frame.add_subview(self.bet_switch)

        y_offset += 90

        # Hole cards section
        hole_section = ui.Label()
        hole_section.text = 'YOUR HOLE CARDS'
        hole_section.font = ('<system-bold>', 18)
        hole_section.text_color = '#d4af37'
        hole_section.alignment = ui.ALIGN_CENTER
        hole_section.frame = (0, y_offset, width, 30)
        self.main_view.add_subview(hole_section)
        y_offset += 35

        # Hole card buttons
        card_width = 100
        card_height = 140
        spacing = 20
        start_x = (width - (2 * card_width + spacing)) / 2

        self.hole_card_btns = []
        for i in range(2):
            btn = ui.Button()
            btn.title = '?'
            btn.font = ('<system-bold>', 48)
            btn.background_color = 'white'
            btn.tint_color = 'black'
            btn.corner_radius = 10
            btn.border_width = 2
            btn.border_color = '#d4af37'
            btn.frame = (start_x + i * (card_width + spacing), y_offset, card_width, card_height)
            btn.action = lambda sender, idx=i: self.select_hole_card(idx)
            self.main_view.add_subview(btn)
            self.hole_card_btns.append(btn)

        y_offset += card_height + 20

        # Community cards section
        comm_label = ui.Label()
        comm_label.text = 'COMMUNITY CARDS'
        comm_label.font = ('<system-bold>', 18)
        comm_label.text_color = '#d4af37'
        comm_label.alignment = ui.ALIGN_CENTER
        comm_label.frame = (0, y_offset, width, 30)
        self.main_view.add_subview(comm_label)
        y_offset += 35

        # Community card buttons (flop, turn, river)
        comm_card_width = 80
        comm_card_height = 110
        comm_spacing = 15
        comm_start_x = (width - (5 * comm_card_width + 4 * comm_spacing)) / 2

        self.comm_card_btns = []
        for i in range(5):
            btn = ui.Button()
            btn.title = '?'
            btn.font = ('<system-bold>', 36)
            btn.background_color = 'white'
            btn.tint_color = 'gray'
            btn.corner_radius = 8
            btn.border_width = 2
            btn.border_color = 'gray'
            btn.frame = (comm_start_x + i * (comm_card_width + comm_spacing), y_offset, comm_card_width, comm_card_height)
            btn.action = lambda sender, idx=i: self.select_community_card(idx)
            self.main_view.add_subview(btn)
            self.comm_card_btns.append(btn)

        y_offset += comm_card_height + 20

        # Analysis section
        analysis_frame = ui.View()
        analysis_frame.background_color = '#0d2818'
        analysis_frame.frame = (10, y_offset, width-20, 250)
        analysis_frame.corner_radius = 10
        self.main_view.add_subview(analysis_frame)

        # Equity display
        equity_label = ui.Label()
        equity_label.text = 'WIN PROBABILITY'
        equity_label.font = ('<system-bold>', 16)
        equity_label.text_color = 'white'
        equity_label.alignment = ui.ALIGN_CENTER
        equity_label.frame = (0, 10, width-20, 25)
        analysis_frame.add_subview(equity_label)

        self.equity_display = ui.Label()
        self.equity_display.text = '--%'
        self.equity_display.font = ('<system-bold>', 48)
        self.equity_display.text_color = '#00ff00'
        self.equity_display.alignment = ui.ALIGN_CENTER
        self.equity_display.frame = (0, 35, width-20, 60)
        analysis_frame.add_subview(self.equity_display)

        # Hand strength
        self.hand_strength_label = ui.Label()
        self.hand_strength_label.text = 'No hand yet'
        self.hand_strength_label.font = ('<system-bold>', 20)
        self.hand_strength_label.text_color = 'white'
        self.hand_strength_label.alignment = ui.ALIGN_CENTER
        self.hand_strength_label.frame = (0, 100, width-20, 30)
        analysis_frame.add_subview(self.hand_strength_label)

        # Recommendation
        rec_label = ui.Label()
        rec_label.text = 'RECOMMENDATION'
        rec_label.font = ('<system-bold>', 16)
        rec_label.text_color = '#d4af37'
        rec_label.alignment = ui.ALIGN_CENTER
        rec_label.frame = (0, 140, width-20, 25)
        analysis_frame.add_subview(rec_label)

        self.recommendation_label = ui.Label()
        self.recommendation_label.text = 'Select your hole cards to begin'
        self.recommendation_label.font = ('<system-bold>', 24)
        self.recommendation_label.text_color = '#ff6600'
        self.recommendation_label.alignment = ui.ALIGN_CENTER
        self.recommendation_label.number_of_lines = 0
        self.recommendation_label.frame = (10, 165, width-40, 80)
        analysis_frame.add_subview(self.recommendation_label)

        y_offset += 260

        # Action buttons
        btn_width = (width - 40) / 2
        btn_height = 50

        # Settings button
        settings_btn = ui.Button()
        settings_btn.title = '⚙️ Opponent Settings'
        settings_btn.font = ('<system-bold>', 18)
        settings_btn.background_color = '#4a4a4a'
        settings_btn.tint_color = 'white'
        settings_btn.corner_radius = 10
        settings_btn.frame = (10, y_offset, btn_width - 5, btn_height)
        settings_btn.action = self.show_settings
        self.main_view.add_subview(settings_btn)

        # New hand button
        new_hand_btn = ui.Button()
        new_hand_btn.title = '🔄 New Hand'
        new_hand_btn.font = ('<system-bold>', 18)
        new_hand_btn.background_color = '#006400'
        new_hand_btn.tint_color = 'white'
        new_hand_btn.corner_radius = 10
        new_hand_btn.frame = (btn_width + 15, y_offset, btn_width - 5, btn_height)
        new_hand_btn.action = self.new_hand
        self.main_view.add_subview(new_hand_btn)

    def build_card_selector(self, callback):
        """Build card selection grid"""
        self.card_selector_view = ui.View()
        self.card_selector_view.name = 'Select Card'
        self.card_selector_view.background_color = '#1a472a'

        width = 768
        height = 1024

        # Title
        title = ui.Label()
        title.text = 'SELECT CARD'
        title.font = ('<system-bold>', 24)
        title.text_color = 'white'
        title.alignment = ui.ALIGN_CENTER
        title.frame = (0, 20, width, 40)
        self.card_selector_view.add_subview(title)

        # Card grid
        ranks = list(Card.RANKS)
        suits = ['♥️', '♦️', '♣️', '♠️']
        suit_colors = ['red', 'red', 'black', 'black']
        suit_chars = ['h', 'd', 'c', 's']

        card_size = 55
        spacing = 3
        start_y = 80

        for suit_idx, (suit_symbol, suit_char, color) in enumerate(zip(suits, suit_chars, suit_colors)):
            # Suit label
            suit_label = ui.Label()
            suit_label.text = suit_symbol
            suit_label.font = ('<system>', 32)
            suit_label.text_color = color
            suit_label.alignment = ui.ALIGN_CENTER
            suit_label.frame = (10, start_y + suit_idx * (card_size + 50), 50, 40)
            self.card_selector_view.add_subview(suit_label)

            for rank_idx, rank in enumerate(ranks):
                card = Card(rank, suit_char)

                # Skip if card already used
                if card in self.used_cards:
                    continue

                btn = ui.Button()
                btn.title = rank
                btn.font = ('<system-bold>', 24)
                btn.background_color = 'white'
                btn.tint_color = color
                btn.corner_radius = 5
                btn.frame = (
                    70 + rank_idx * (card_size + spacing),
                    start_y + suit_idx * (card_size + 50),
                    card_size,
                    card_size
                )

                # Create closure to capture card
                def make_action(c):
                    return lambda sender: callback(c)

                btn.action = make_action(card)
                self.card_selector_view.add_subview(btn)

        # Cancel button
        cancel_btn = ui.Button()
        cancel_btn.title = 'Cancel'
        cancel_btn.font = ('<system-bold>', 20)
        cancel_btn.background_color = '#8b0000'
        cancel_btn.tint_color = 'white'
        cancel_btn.corner_radius = 10
        cancel_btn.frame = (width/2 - 100, height - 100, 200, 50)
        cancel_btn.action = lambda sender: self.card_selector_view.close()
        self.card_selector_view.add_subview(cancel_btn)

        return self.card_selector_view

    def select_hole_card(self, index):
        """Select a hole card"""
        def card_selected(card):
            if index < len(self.hole_cards):
                # Remove old card from used set
                self.used_cards.discard(self.hole_cards[index])
                self.hole_cards[index] = card
            else:
                self.hole_cards.append(card)

            self.used_cards.add(card)
            self.update_hole_card_display()
            self.card_selector_view.close()
            self.analyze_hand()

        selector = self.build_card_selector(card_selected)
        selector.present('sheet')

    def select_community_card(self, index):
        """Select a community card"""
        def card_selected(card):
            if index < len(self.community_cards):
                # Remove old card from used set
                self.used_cards.discard(self.community_cards[index])
                self.community_cards[index] = card
            else:
                self.community_cards.append(card)

            self.used_cards.add(card)
            self.update_community_card_display()
            self.update_street()
            self.card_selector_view.close()
            self.analyze_hand()

        selector = self.build_card_selector(card_selected)
        selector.present('sheet')

    def update_hole_card_display(self):
        """Update hole card button displays"""
        for i, btn in enumerate(self.hole_card_btns):
            if i < len(self.hole_cards):
                card = self.hole_cards[i]
                btn.title = self.format_card_display(card)
                color = 'red' if card.suit in ['h', 'd'] else 'black'
                btn.tint_color = color
                btn.border_color = '#d4af37'
            else:
                btn.title = '?'
                btn.tint_color = 'black'
                btn.border_color = '#d4af37'

    def update_community_card_display(self):
        """Update community card button displays"""
        for i, btn in enumerate(self.comm_card_btns):
            if i < len(self.community_cards):
                card = self.community_cards[i]
                btn.title = self.format_card_display(card)
                color = 'red' if card.suit in ['h', 'd'] else 'black'
                btn.tint_color = color
                btn.border_color = '#d4af37'
            else:
                btn.title = '?'
                btn.tint_color = 'gray'
                btn.border_color = 'gray'

    def format_card_display(self, card):
        """Format card for display with suit symbol"""
        suit_symbols = {'h': '♥️', 'd': '♦️', 'c': '♣️', 's': '♠️'}
        return f"{card.rank}\n{suit_symbols[card.suit]}"

    def update_street(self):
        """Update the current street based on community cards"""
        num_comm = len(self.community_cards)
        if num_comm == 0:
            self.street = 'preflop'
            self.street_label.text = '🎴 PRE-FLOP'
        elif num_comm == 3:
            self.street = 'flop'
            self.street_label.text = '🎴 FLOP'
        elif num_comm == 4:
            self.street = 'turn'
            self.street_label.text = '🎴 TURN'
        elif num_comm == 5:
            self.street = 'river'
            self.street_label.text = '🎴 RIVER'

    def analyze_hand(self):
        """Analyze current hand and update recommendations"""
        if len(self.hole_cards) != 2:
            self.recommendation_label.text = 'Select your hole cards'
            return

        # Calculate equity
        try:
            if len(self.community_cards) == 0:
                # Pre-flop: use quick estimate
                preflop_strength = self.strategy.get_preflop_hand_strength(self.hole_cards)
                self.equity_display.text = f"{preflop_strength}%"

                # Mock equity data for strategy
                equity_data = {
                    'equity': preflop_strength,
                    'win_pct': preflop_strength,
                    'tie_pct': 0,
                    'lose_pct': 100 - preflop_strength,
                    'current_hand': 'Hole Cards',
                    'hand_strength': 'Pre-flop'
                }
            else:
                # Post-flop: run simulation
                equity_data = self.equity_calc.quick_equity(
                    self.hole_cards,
                    self.community_cards,
                    self.num_opponents,
                    simulations=500
                )
                self.equity_display.text = f"{equity_data['win_pct']}%"

            # Update equity color
            if equity_data['win_pct'] >= 60:
                self.equity_display.text_color = '#00ff00'  # Green
            elif equity_data['win_pct'] >= 40:
                self.equity_display.text_color = '#ffff00'  # Yellow
            else:
                self.equity_display.text_color = '#ff6600'  # Orange

            # Update hand strength
            self.hand_strength_label.text = equity_data['current_hand']

            # Get recommendation
            recommendation = self.strategy.get_recommendation(
                equity_data,
                self.position,
                self.num_opponents,
                self.street,
                self.facing_bet
            )

            # Display recommendation
            self.recommendation_label.text = f"⚡ {recommendation['action']}"

        except Exception as e:
            self.recommendation_label.text = f"Error: {str(e)}"

    def cycle_position(self, sender):
        """Cycle through positions"""
        positions = ['BTN', 'SB', 'BB', 'CO']
        current_idx = positions.index(self.position)
        self.position = positions[(current_idx + 1) % len(positions)]
        self.position_btn.title = self.position
        self.analyze_hand()

    def adjust_opponents(self, delta):
        """Adjust number of opponents"""
        self.num_opponents = max(1, min(3, self.num_opponents + delta))
        self.opp_count_label.text = str(self.num_opponents)
        self.analyze_hand()

    def toggle_facing_bet(self, sender):
        """Toggle facing bet status"""
        self.facing_bet = sender.value
        self.analyze_hand()

    def new_hand(self, sender):
        """Reset for new hand"""
        # Rotate position (dealer button moves)
        positions = ['BTN', 'SB', 'BB', 'CO']
        current_idx = positions.index(self.position)
        self.position = positions[(current_idx + 1) % len(positions)]
        self.position_btn.title = self.position

        # Clear cards
        self.hole_cards = []
        self.community_cards = []
        self.used_cards = set()
        self.street = 'preflop'
        self.facing_bet = False
        self.bet_switch.value = False

        # Reset displays
        self.update_hole_card_display()
        self.update_community_card_display()
        self.update_street()
        self.equity_display.text = '--%'
        self.equity_display.text_color = '#00ff00'
        self.hand_strength_label.text = 'No hand yet'
        self.recommendation_label.text = 'Select your hole cards to begin'

    def show_settings(self, sender):
        """Show opponent tendency settings"""
        settings_view = ui.View()
        settings_view.name = 'Opponent Settings'
        settings_view.background_color = '#1a472a'

        width = 600
        height = 400

        y_offset = 30

        # Title
        title = ui.Label()
        title.text = 'OPPONENT TENDENCIES'
        title.font = ('<system-bold>', 24)
        title.text_color = 'white'
        title.alignment = ui.ALIGN_CENTER
        title.frame = (0, y_offset, width, 40)
        settings_view.add_subview(title)
        y_offset += 60

        # Tightness slider
        tight_label = ui.Label()
        tight_label.text = 'Playing Style: LOOSE ← → TIGHT'
        tight_label.font = ('<system-bold>', 18)
        tight_label.text_color = 'white'
        tight_label.alignment = ui.ALIGN_CENTER
        tight_label.frame = (20, y_offset, width-40, 30)
        settings_view.add_subview(tight_label)
        y_offset += 40

        tight_slider = ui.Slider()
        tight_slider.value = self.strategy.opponent_tightness
        tight_slider.frame = (50, y_offset, width-100, 40)
        settings_view.add_subview(tight_slider)
        y_offset += 60

        # Aggression slider
        agg_label = ui.Label()
        agg_label.text = 'Betting Style: PASSIVE ← → AGGRESSIVE'
        agg_label.font = ('<system-bold>', 18)
        agg_label.text_color = 'white'
        agg_label.alignment = ui.ALIGN_CENTER
        agg_label.frame = (20, y_offset, width-40, 30)
        settings_view.add_subview(agg_label)
        y_offset += 40

        agg_slider = ui.Slider()
        agg_slider.value = self.strategy.opponent_aggression
        agg_slider.frame = (50, y_offset, width-100, 40)
        settings_view.add_subview(agg_slider)
        y_offset += 80

        # Save button
        def save_settings(sender):
            self.strategy.update_opponent_tendencies(
                tight_slider.value,
                agg_slider.value
            )
            self.analyze_hand()  # Re-analyze with new settings
            settings_view.close()

        save_btn = ui.Button()
        save_btn.title = '✓ Save & Apply'
        save_btn.font = ('<system-bold>', 20)
        save_btn.background_color = '#006400'
        save_btn.tint_color = 'white'
        save_btn.corner_radius = 10
        save_btn.frame = (width/2 - 100, y_offset, 200, 50)
        save_btn.action = save_settings
        settings_view.add_subview(save_btn)

        settings_view.present('popover')

    def run(self):
        """Run the application"""
        self.main_view.present('fullscreen')


# Run the app
if __name__ == '__main__':
    app = PokerAdvisorApp()
    app.run()
