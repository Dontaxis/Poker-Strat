"""
Poker Strategy Advisor - Main Application
Pythonista 3 optimized UI for iPad - SIMPLIFIED VERSION
"""

import ui
import random
from poker_evaluator import Card, HandEvaluator
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
        self.position = 'BTN'
        self.num_opponents = 3
        self.street = 'preflop'
        self.facing_bet = False
        self.used_cards = set()

        # UI components
        self.main_view = None
        self.build_ui()

    def build_ui(self):
        """Build the main interface"""
        # Create main view with adaptive sizing
        self.main_view = ui.View()
        self.main_view.name = 'Poker Advisor'
        self.main_view.background_color = '#1a472a'

        # Use device width/height
        w = min(ui.get_screen_size()[0], 800)
        h = ui.get_screen_size()[1]
        self.main_view.frame = (0, 0, w, h)

        # Create scrollview for content
        scroll = ui.ScrollView()
        scroll.frame = (0, 0, w, h)
        scroll.background_color = '#1a472a'
        self.main_view.add_subview(scroll)

        y = 10

        # Title
        title = ui.Label()
        title.text = '♠️ POKER ADVISOR ♥️'
        title.font = ('<system-bold>', 28)
        title.text_color = 'white'
        title.alignment = ui.ALIGN_CENTER
        title.frame = (0, y, w, 50)
        scroll.add_subview(title)
        y += 60

        # === GAME INFO SECTION ===
        info_bg = ui.View()
        info_bg.background_color = '#0d2818'
        info_bg.corner_radius = 10
        info_bg.frame = (10, y, w-20, 120)
        scroll.add_subview(info_bg)

        # Position
        pos_lbl = ui.Label(frame=(10, 10, 100, 30))
        pos_lbl.text = 'Position:'
        pos_lbl.text_color = 'white'
        pos_lbl.font = ('<system>', 16)
        info_bg.add_subview(pos_lbl)

        self.position_btn = ui.Button(frame=(120, 10, 100, 40))
        self.position_btn.title = self.position
        self.position_btn.background_color = '#d4af37'
        self.position_btn.tint_color = 'black'
        self.position_btn.font = ('<system-bold>', 20)
        self.position_btn.corner_radius = 8
        self.position_btn.action = self.cycle_position
        info_bg.add_subview(self.position_btn)

        # Opponents
        opp_lbl = ui.Label(frame=(240, 10, 120, 30))
        opp_lbl.text = 'Opponents:'
        opp_lbl.text_color = 'white'
        opp_lbl.font = ('<system>', 16)
        info_bg.add_subview(opp_lbl)

        self.opp_label = ui.Label(frame=(370, 10, 60, 40))
        self.opp_label.text = str(self.num_opponents)
        self.opp_label.text_color = '#d4af37'
        self.opp_label.font = ('<system-bold>', 28)
        self.opp_label.alignment = ui.ALIGN_CENTER
        info_bg.add_subview(self.opp_label)

        btn_minus = ui.Button(frame=(440, 10, 50, 40))
        btn_minus.title = '-'
        btn_minus.background_color = '#8b0000'
        btn_minus.tint_color = 'white'
        btn_minus.font = ('<system-bold>', 24)
        btn_minus.corner_radius = 8
        btn_minus.action = lambda s: self.adjust_opponents(-1)
        info_bg.add_subview(btn_minus)

        btn_plus = ui.Button(frame=(500, 10, 50, 40))
        btn_plus.title = '+'
        btn_plus.background_color = '#006400'
        btn_plus.tint_color = 'white'
        btn_plus.font = ('<system-bold>', 24)
        btn_plus.corner_radius = 8
        btn_plus.action = lambda s: self.adjust_opponents(1)
        info_bg.add_subview(btn_plus)

        # Street
        self.street_label = ui.Label(frame=(10, 60, w-40, 30))
        self.street_label.text = '🎴 PRE-FLOP'
        self.street_label.text_color = '#d4af37'
        self.street_label.font = ('<system-bold>', 20)
        self.street_label.alignment = ui.ALIGN_CENTER
        info_bg.add_subview(self.street_label)

        # Facing bet
        bet_lbl = ui.Label(frame=(10, 95, 120, 20))
        bet_lbl.text = 'Facing Bet?'
        bet_lbl.text_color = 'white'
        bet_lbl.font = ('<system>', 14)
        info_bg.add_subview(bet_lbl)

        self.bet_switch = ui.Switch(frame=(140, 90, 60, 30))
        self.bet_switch.value = False
        self.bet_switch.action = self.toggle_facing_bet
        info_bg.add_subview(self.bet_switch)

        y += 130

        # === HOLE CARDS ===
        hole_lbl = ui.Label(frame=(0, y, w, 30))
        hole_lbl.text = 'YOUR HOLE CARDS'
        hole_lbl.text_color = '#d4af37'
        hole_lbl.font = ('<system-bold>', 20)
        hole_lbl.alignment = ui.ALIGN_CENTER
        scroll.add_subview(hole_lbl)
        y += 35

        # Hole card buttons
        self.hole_btns = []
        card_w = 120
        card_h = 160
        spacing = 20
        start_x = (w - (2*card_w + spacing)) / 2

        for i in range(2):
            btn = ui.Button()
            btn.title = '?'
            btn.background_color = 'white'
            btn.tint_color = 'black'
            btn.font = ('<system-bold>', 56)
            btn.corner_radius = 10
            btn.border_width = 3
            btn.border_color = '#d4af37'
            btn.frame = (start_x + i*(card_w+spacing), y, card_w, card_h)
            btn.action = lambda s, idx=i: self.select_hole_card(idx)
            scroll.add_subview(btn)
            self.hole_btns.append(btn)

        y += card_h + 20

        # === COMMUNITY CARDS ===
        comm_lbl = ui.Label(frame=(0, y, w, 30))
        comm_lbl.text = 'COMMUNITY CARDS'
        comm_lbl.text_color = '#d4af37'
        comm_lbl.font = ('<system-bold>', 20)
        comm_lbl.alignment = ui.ALIGN_CENTER
        scroll.add_subview(comm_lbl)
        y += 35

        # Community card buttons
        self.comm_btns = []
        comm_w = 90
        comm_h = 120
        comm_spacing = 10
        comm_start = (w - (5*comm_w + 4*comm_spacing)) / 2

        for i in range(5):
            btn = ui.Button()
            btn.title = '?'
            btn.background_color = 'white'
            btn.tint_color = 'gray'
            btn.font = ('<system-bold>', 42)
            btn.corner_radius = 8
            btn.border_width = 2
            btn.border_color = 'gray'
            btn.frame = (comm_start + i*(comm_w+comm_spacing), y, comm_w, comm_h)
            btn.action = lambda s, idx=i: self.select_comm_card(idx)
            scroll.add_subview(btn)
            self.comm_btns.append(btn)

        y += comm_h + 20

        # === ANALYSIS SECTION ===
        analysis_bg = ui.View()
        analysis_bg.background_color = '#0d2818'
        analysis_bg.corner_radius = 10
        analysis_bg.frame = (10, y, w-20, 280)
        scroll.add_subview(analysis_bg)

        # Equity
        eq_lbl = ui.Label(frame=(0, 10, w-20, 25))
        eq_lbl.text = 'WIN PROBABILITY'
        eq_lbl.text_color = 'white'
        eq_lbl.font = ('<system-bold>', 18)
        eq_lbl.alignment = ui.ALIGN_CENTER
        analysis_bg.add_subview(eq_lbl)

        self.equity_label = ui.Label(frame=(0, 40, w-20, 70))
        self.equity_label.text = '--%'
        self.equity_label.text_color = '#00ff00'
        self.equity_label.font = ('<system-bold>', 60)
        self.equity_label.alignment = ui.ALIGN_CENTER
        analysis_bg.add_subview(self.equity_label)

        # Hand strength
        self.hand_label = ui.Label(frame=(0, 115, w-20, 30))
        self.hand_label.text = 'Select your cards'
        self.hand_label.text_color = 'white'
        self.hand_label.font = ('<system-bold>', 18)
        self.hand_label.alignment = ui.ALIGN_CENTER
        analysis_bg.add_subview(self.hand_label)

        # Recommendation
        rec_title = ui.Label(frame=(0, 155, w-20, 25))
        rec_title.text = 'RECOMMENDATION'
        rec_title.text_color = '#d4af37'
        rec_title.font = ('<system-bold>', 16)
        rec_title.alignment = ui.ALIGN_CENTER
        analysis_bg.add_subview(rec_title)

        self.rec_label = ui.Label(frame=(10, 185, w-40, 90))
        self.rec_label.text = 'Input your hole cards'
        self.rec_label.text_color = '#ff6600'
        self.rec_label.font = ('<system-bold>', 26)
        self.rec_label.alignment = ui.ALIGN_CENTER
        self.rec_label.number_of_lines = 0
        analysis_bg.add_subview(self.rec_label)

        y += 290

        # === BUTTONS ===
        btn_w = (w - 30) / 2

        settings_btn = ui.Button(frame=(10, y, btn_w, 60))
        settings_btn.title = '⚙️ Settings'
        settings_btn.background_color = '#4a4a4a'
        settings_btn.tint_color = 'white'
        settings_btn.font = ('<system-bold>', 20)
        settings_btn.corner_radius = 10
        settings_btn.action = self.show_settings
        scroll.add_subview(settings_btn)

        new_btn = ui.Button(frame=(20 + btn_w, y, btn_w, 60))
        new_btn.title = '🔄 New Hand'
        new_btn.background_color = '#006400'
        new_btn.tint_color = 'white'
        new_btn.font = ('<system-bold>', 20)
        new_btn.corner_radius = 10
        new_btn.action = self.new_hand
        scroll.add_subview(new_btn)

        y += 70

        # Set scroll content size
        scroll.content_size = (w, y + 20)

    def build_card_selector(self, callback):
        """Build card selection popup"""
        v = ui.View()
        v.name = 'Select Card'
        v.background_color = '#1a472a'

        w = 700
        h = 400
        v.frame = (0, 0, w, h)

        # Title
        title = ui.Label(frame=(0, 10, w, 40))
        title.text = 'TAP A CARD'
        title.text_color = 'white'
        title.font = ('<system-bold>', 24)
        title.alignment = ui.ALIGN_CENTER
        v.add_subview(title)

        # Card grid
        ranks = list(Card.RANKS)
        suits = ['♥️', '♦️', '♣️', '♠️']
        suit_chars = ['h', 'd', 'c', 's']
        suit_colors = ['red', 'red', 'black', 'black']

        card_size = 50
        y_start = 60

        for suit_idx, (symbol, char, color) in enumerate(zip(suits, suit_chars, suit_colors)):
            # Suit label
            lbl = ui.Label(frame=(10, y_start + suit_idx*70, 40, 50))
            lbl.text = symbol
            lbl.text_color = color
            lbl.font = ('<system>', 36)
            lbl.alignment = ui.ALIGN_CENTER
            v.add_subview(lbl)

            # Cards
            for rank_idx, rank in enumerate(ranks):
                card = Card(rank, char)
                if card in self.used_cards:
                    continue

                btn = ui.Button()
                btn.title = rank
                btn.background_color = 'white'
                btn.tint_color = color
                btn.font = ('<system-bold>', 22)
                btn.corner_radius = 5
                btn.frame = (60 + rank_idx*50, y_start + suit_idx*70, card_size, card_size)

                def make_action(c):
                    return lambda s: callback(c)

                btn.action = make_action(card)
                v.add_subview(btn)

        # Cancel
        cancel = ui.Button(frame=(w/2-100, h-60, 200, 50))
        cancel.title = 'Cancel'
        cancel.background_color = '#8b0000'
        cancel.tint_color = 'white'
        cancel.font = ('<system-bold>', 20)
        cancel.corner_radius = 10
        cancel.action = lambda s: v.close()
        v.add_subview(cancel)

        return v

    def select_hole_card(self, idx):
        """Select hole card"""
        def on_select(card):
            if idx < len(self.hole_cards):
                self.used_cards.discard(self.hole_cards[idx])
                self.hole_cards[idx] = card
            else:
                self.hole_cards.append(card)

            self.used_cards.add(card)
            self.update_hole_display()
            self.card_selector_view.close()
            self.analyze()

        self.card_selector_view = self.build_card_selector(on_select)
        self.card_selector_view.present('popover')

    def select_comm_card(self, idx):
        """Select community card"""
        def on_select(card):
            if idx < len(self.community_cards):
                self.used_cards.discard(self.community_cards[idx])
                self.community_cards[idx] = card
            else:
                self.community_cards.append(card)

            self.used_cards.add(card)
            self.update_comm_display()
            self.update_street()
            self.card_selector_view.close()
            self.analyze()

        self.card_selector_view = self.build_card_selector(on_select)
        self.card_selector_view.present('popover')

    def update_hole_display(self):
        """Update hole card buttons"""
        suit_symbols = {'h': '♥️', 'd': '♦️', 'c': '♣️', 's': '♠️'}

        for i, btn in enumerate(self.hole_btns):
            if i < len(self.hole_cards):
                card = self.hole_cards[i]
                btn.title = f"{card.rank}\n{suit_symbols[card.suit]}"
                color = 'red' if card.suit in ['h', 'd'] else 'black'
                btn.tint_color = color
            else:
                btn.title = '?'
                btn.tint_color = 'black'

    def update_comm_display(self):
        """Update community card buttons"""
        suit_symbols = {'h': '♥️', 'd': '♦️', 'c': '♣️', 's': '♠️'}

        for i, btn in enumerate(self.comm_btns):
            if i < len(self.community_cards):
                card = self.community_cards[i]
                btn.title = f"{card.rank}\n{suit_symbols[card.suit]}"
                color = 'red' if card.suit in ['h', 'd'] else 'black'
                btn.tint_color = color
                btn.border_color = '#d4af37'
            else:
                btn.title = '?'
                btn.tint_color = 'gray'
                btn.border_color = 'gray'

    def update_street(self):
        """Update street label"""
        n = len(self.community_cards)
        if n == 0:
            self.street = 'preflop'
            self.street_label.text = '🎴 PRE-FLOP'
        elif n == 3:
            self.street = 'flop'
            self.street_label.text = '🎴 FLOP'
        elif n == 4:
            self.street = 'turn'
            self.street_label.text = '🎴 TURN'
        elif n == 5:
            self.street = 'river'
            self.street_label.text = '🎴 RIVER'

    def analyze(self):
        """Analyze hand and show recommendation"""
        if len(self.hole_cards) != 2:
            self.rec_label.text = 'Select 2 hole cards'
            return

        try:
            if len(self.community_cards) == 0:
                # Pre-flop
                strength = self.strategy.get_preflop_hand_strength(self.hole_cards)
                self.equity_label.text = f"{strength}%"

                equity_data = {
                    'equity': strength,
                    'win_pct': strength,
                    'tie_pct': 0,
                    'lose_pct': 100 - strength,
                    'current_hand': 'Hole Cards',
                    'hand_strength': 'Pre-flop'
                }
            else:
                # Post-flop
                equity_data = self.equity_calc.quick_equity(
                    self.hole_cards,
                    self.community_cards,
                    self.num_opponents,
                    simulations=500
                )
                self.equity_label.text = f"{equity_data['win_pct']}%"

            # Color code equity
            if equity_data['win_pct'] >= 60:
                self.equity_label.text_color = '#00ff00'
            elif equity_data['win_pct'] >= 40:
                self.equity_label.text_color = '#ffff00'
            else:
                self.equity_label.text_color = '#ff6600'

            # Update hand
            self.hand_label.text = equity_data['current_hand']

            # Get recommendation
            rec = self.strategy.get_recommendation(
                equity_data,
                self.position,
                self.num_opponents,
                self.street,
                self.facing_bet
            )

            self.rec_label.text = f"⚡ {rec['action']}"

        except Exception as e:
            self.rec_label.text = f"Error: {str(e)}"

    def cycle_position(self, sender):
        """Cycle position"""
        positions = ['BTN', 'SB', 'BB', 'CO']
        idx = positions.index(self.position)
        self.position = positions[(idx + 1) % 4]
        self.position_btn.title = self.position
        self.analyze()

    def adjust_opponents(self, delta):
        """Adjust opponents"""
        self.num_opponents = max(1, min(3, self.num_opponents + delta))
        self.opp_label.text = str(self.num_opponents)
        self.analyze()

    def toggle_facing_bet(self, sender):
        """Toggle facing bet"""
        self.facing_bet = sender.value
        self.analyze()

    def new_hand(self, sender):
        """New hand"""
        # Rotate position
        positions = ['BTN', 'SB', 'BB', 'CO']
        idx = positions.index(self.position)
        self.position = positions[(idx + 1) % 4]
        self.position_btn.title = self.position

        # Clear
        self.hole_cards = []
        self.community_cards = []
        self.used_cards = set()
        self.street = 'preflop'
        self.facing_bet = False
        self.bet_switch.value = False

        # Reset display
        self.update_hole_display()
        self.update_comm_display()
        self.update_street()
        self.equity_label.text = '--%'
        self.equity_label.text_color = '#00ff00'
        self.hand_label.text = 'Select your cards'
        self.rec_label.text = 'Input your hole cards'

    def show_settings(self, sender):
        """Show settings"""
        v = ui.View()
        v.name = 'Settings'
        v.background_color = '#1a472a'
        v.frame = (0, 0, 600, 350)

        # Title
        title = ui.Label(frame=(0, 20, 600, 40))
        title.text = 'OPPONENT TENDENCIES'
        title.text_color = 'white'
        title.font = ('<system-bold>', 24)
        title.alignment = ui.ALIGN_CENTER
        v.add_subview(title)

        y = 80

        # Tightness
        lbl1 = ui.Label(frame=(20, y, 560, 30))
        lbl1.text = 'LOOSE ← → TIGHT'
        lbl1.text_color = 'white'
        lbl1.font = ('<system-bold>', 18)
        lbl1.alignment = ui.ALIGN_CENTER
        v.add_subview(lbl1)

        tight_slider = ui.Slider(frame=(50, y+40, 500, 40))
        tight_slider.value = self.strategy.opponent_tightness
        v.add_subview(tight_slider)

        y += 100

        # Aggression
        lbl2 = ui.Label(frame=(20, y, 560, 30))
        lbl2.text = 'PASSIVE ← → AGGRESSIVE'
        lbl2.text_color = 'white'
        lbl2.font = ('<system-bold>', 18)
        lbl2.alignment = ui.ALIGN_CENTER
        v.add_subview(lbl2)

        agg_slider = ui.Slider(frame=(50, y+40, 500, 40))
        agg_slider.value = self.strategy.opponent_aggression
        v.add_subview(agg_slider)

        # Save
        def save(s):
            self.strategy.update_opponent_tendencies(
                tight_slider.value,
                agg_slider.value
            )
            self.analyze()
            v.close()

        save_btn = ui.Button(frame=(200, 280, 200, 50))
        save_btn.title = '✓ Save'
        save_btn.background_color = '#006400'
        save_btn.tint_color = 'white'
        save_btn.font = ('<system-bold>', 20)
        save_btn.corner_radius = 10
        save_btn.action = save
        v.add_subview(save_btn)

        v.present('popover')

    def run(self):
        """Run the app"""
        self.main_view.present('fullscreen', hide_title_bar=False)


if __name__ == '__main__':
    app = PokerAdvisorApp()
    app.run()
