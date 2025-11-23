"""
Poker Strategy Advisor - Mobile Optimized
Auto-adapts for iPhone 15 and iPad screens
Pythonista 3 optimized UI
"""

import ui
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
        self.preflop_raise = False
        self.used_cards = set()

        # Detect device type
        screen = ui.get_screen_size()
        self.is_iphone = screen[0] < 500  # iPhone if width < 500 points

        self.main_view = None
        self.build_ui()

    def build_ui(self):
        """Build the main interface - auto-adapts to iPhone/iPad"""
        self.main_view = ui.View()
        self.main_view.name = 'Poker Advisor'
        self.main_view.background_color = '#1a472a'

        # Get screen dimensions
        screen = ui.get_screen_size()
        w = screen[0]
        h = screen[1]

        # Scale factors for iPhone vs iPad
        if self.is_iphone:
            # iPhone 15: 393 x 852 points
            scale = 0.52  # Scale everything down by ~48%
            font_scale = 0.65
        else:
            # iPad
            scale = 1.0
            font_scale = 1.0

        # Scrollview for everything
        scroll = ui.ScrollView(frame=(0, 0, w, h))
        scroll.background_color = '#1a472a'
        self.main_view.add_subview(scroll)

        y = 10 if self.is_iphone else 20

        # TITLE
        title = ui.Label(frame=(0, y, w, int(50 * font_scale)))
        title.text = '♠️ POKER ADVISOR ♥️'
        title.font = ('<system-bold>', int(32 * font_scale))
        title.text_color = 'white'
        title.alignment = ui.ALIGN_CENTER
        scroll.add_subview(title)
        y += int(50 * font_scale) + 10

        # POSITION & OPPONENTS & SETTINGS
        controls_height = int(340 * scale) if not self.is_iphone else 280
        controls = ui.View(frame=(10, y, w-20, controls_height))
        controls.background_color = '#0d2818'
        controls.corner_radius = 10
        scroll.add_subview(controls)

        # Position and opponents - side by side on iPhone
        if self.is_iphone:
            # ROW 1: Position and Opponents
            pos_label = ui.Label(frame=(10, 10, 60, 20))
            pos_label.text = 'Position:'
            pos_label.text_color = 'white'
            pos_label.font = ('<system-bold>', 13)
            controls.add_subview(pos_label)

            self.pos_btn = ui.Button(frame=(10, 32, 70, 35))
            self.pos_btn.title = self.position
            self.pos_btn.background_color = '#d4af37'
            self.pos_btn.tint_color = 'black'
            self.pos_btn.font = ('<system-bold>', 18)
            self.pos_btn.corner_radius = 8
            self.pos_btn.action = self.cycle_position
            controls.add_subview(self.pos_btn)

            # Opponents controls
            opp_label = ui.Label(frame=(95, 10, 80, 20))
            opp_label.text = 'Opponents:'
            opp_label.text_color = 'white'
            opp_label.font = ('<system-bold>', 13)
            controls.add_subview(opp_label)

            self.opp_lbl = ui.Label(frame=(95, 32, 50, 35))
            self.opp_lbl.text = str(self.num_opponents)
            self.opp_lbl.text_color = '#d4af37'
            self.opp_lbl.font = ('<system-bold>', 28)
            self.opp_lbl.alignment = ui.ALIGN_CENTER
            controls.add_subview(self.opp_lbl)

            btn_minus = ui.Button(frame=(150, 32, 50, 35))
            btn_minus.title = '-'
            btn_minus.background_color = '#8b0000'
            btn_minus.tint_color = 'white'
            btn_minus.font = ('<system-bold>', 20)
            btn_minus.corner_radius = 8
            btn_minus.action = lambda s: self.adjust_opponents(-1)
            controls.add_subview(btn_minus)

            btn_plus = ui.Button(frame=(205, 32, 50, 35))
            btn_plus.title = '+'
            btn_plus.background_color = '#006400'
            btn_plus.tint_color = 'white'
            btn_plus.font = ('<system-bold>', 20)
            btn_plus.corner_radius = 8
            btn_plus.action = lambda s: self.adjust_opponents(1)
            controls.add_subview(btn_plus)

            # Street label - compact
            self.street_lbl = ui.Label(frame=(10, 75, w-40, 20))
            self.street_lbl.text = '🎴 PRE-FLOP'
            self.street_lbl.text_color = '#d4af37'
            self.street_lbl.font = ('<system-bold>', 16)
            self.street_lbl.alignment = ui.ALIGN_CENTER
            controls.add_subview(self.street_lbl)

            # Toggles - compact
            bet_label = ui.Label(frame=(10, 100, 100, 15))
            bet_label.text = 'Facing Bet?'
            bet_label.text_color = 'white'
            bet_label.font = ('<system>', 12)
            controls.add_subview(bet_label)

            self.bet_switch = ui.Switch(frame=(10, 118, 51, 31))
            self.bet_switch.value = False
            self.bet_switch.action = self.toggle_facing_bet
            controls.add_subview(self.bet_switch)

            preflop_raise_label = ui.Label(frame=(75, 100, 130, 15))
            preflop_raise_label.text = 'Opp Raised Pre-flop?'
            preflop_raise_label.text_color = 'white'
            preflop_raise_label.font = ('<system>', 12)
            controls.add_subview(preflop_raise_label)

            self.preflop_raise_switch = ui.Switch(frame=(75, 118, 51, 31))
            self.preflop_raise_switch.value = False
            self.preflop_raise_switch.action = self.toggle_preflop_raise
            controls.add_subview(self.preflop_raise_switch)

            # Sliders - compact
            slider_y = 160

            tight_lbl = ui.Label(frame=(10, slider_y, w-40, 18))
            tight_lbl.text = 'Style: LOOSE ← → TIGHT'
            tight_lbl.text_color = 'white'
            tight_lbl.font = ('<system-bold>', 12)
            tight_lbl.alignment = ui.ALIGN_CENTER
            controls.add_subview(tight_lbl)

            self.tight_slider = ui.Slider(frame=(20, slider_y+20, w-60, 30))
            self.tight_slider.value = self.strategy.opponent_tightness
            self.tight_slider.action = self.update_opponent_sliders
            controls.add_subview(self.tight_slider)

            slider_y += 60

            agg_lbl = ui.Label(frame=(10, slider_y, w-40, 18))
            agg_lbl.text = 'Betting: PASSIVE ← → AGGRESSIVE'
            agg_lbl.text_color = 'white'
            agg_lbl.font = ('<system-bold>', 12)
            agg_lbl.alignment = ui.ALIGN_CENTER
            controls.add_subview(agg_lbl)

            self.agg_slider = ui.Slider(frame=(20, slider_y+20, w-60, 30))
            self.agg_slider.value = self.strategy.opponent_aggression
            self.agg_slider.action = self.update_opponent_sliders
            controls.add_subview(self.agg_slider)

        else:
            # iPad layout (original)
            pos_label = ui.Label(frame=(20, 15, 120, 30))
            pos_label.text = 'Position:'
            pos_label.text_color = 'white'
            pos_label.font = ('<system-bold>', 18)
            controls.add_subview(pos_label)

            self.pos_btn = ui.Button(frame=(150, 10, 120, 50))
            self.pos_btn.title = self.position
            self.pos_btn.background_color = '#d4af37'
            self.pos_btn.tint_color = 'black'
            self.pos_btn.font = ('<system-bold>', 24)
            self.pos_btn.corner_radius = 10
            self.pos_btn.action = self.cycle_position
            controls.add_subview(self.pos_btn)

            opp_label = ui.Label(frame=(300, 15, 150, 30))
            opp_label.text = 'Opponents:'
            opp_label.text_color = 'white'
            opp_label.font = ('<system-bold>', 18)
            controls.add_subview(opp_label)

            self.opp_lbl = ui.Label(frame=(460, 10, 80, 50))
            self.opp_lbl.text = str(self.num_opponents)
            self.opp_lbl.text_color = '#d4af37'
            self.opp_lbl.font = ('<system-bold>', 36)
            self.opp_lbl.alignment = ui.ALIGN_CENTER
            controls.add_subview(self.opp_lbl)

            btn_minus = ui.Button(frame=(550, 10, 70, 50))
            btn_minus.title = '-'
            btn_minus.background_color = '#8b0000'
            btn_minus.tint_color = 'white'
            btn_minus.font = ('<system-bold>', 28)
            btn_minus.corner_radius = 10
            btn_minus.action = lambda s: self.adjust_opponents(-1)
            controls.add_subview(btn_minus)

            btn_plus = ui.Button(frame=(630, 10, 70, 50))
            btn_plus.title = '+'
            btn_plus.background_color = '#006400'
            btn_plus.tint_color = 'white'
            btn_plus.font = ('<system-bold>', 28)
            btn_plus.corner_radius = 10
            btn_plus.action = lambda s: self.adjust_opponents(1)
            controls.add_subview(btn_plus)

            self.street_lbl = ui.Label(frame=(20, 75, w-80, 30))
            self.street_lbl.text = '🎴 PRE-FLOP'
            self.street_lbl.text_color = '#d4af37'
            self.street_lbl.font = ('<system-bold>', 22)
            self.street_lbl.alignment = ui.ALIGN_CENTER
            controls.add_subview(self.street_lbl)

            bet_label = ui.Label(frame=(20, 115, 140, 20))
            bet_label.text = 'Facing Bet?'
            bet_label.text_color = 'white'
            bet_label.font = ('<system>', 15)
            controls.add_subview(bet_label)

            self.bet_switch = ui.Switch(frame=(20, 138, 60, 30))
            self.bet_switch.value = False
            self.bet_switch.action = self.toggle_facing_bet
            controls.add_subview(self.bet_switch)

            preflop_raise_label = ui.Label(frame=(110, 115, 180, 20))
            preflop_raise_label.text = 'Opp Raised Pre-flop?'
            preflop_raise_label.text_color = 'white'
            preflop_raise_label.font = ('<system>', 15)
            controls.add_subview(preflop_raise_label)

            self.preflop_raise_switch = ui.Switch(frame=(110, 138, 60, 30))
            self.preflop_raise_switch.value = False
            self.preflop_raise_switch.action = self.toggle_preflop_raise
            controls.add_subview(self.preflop_raise_switch)

            slider_y = 185

            tight_lbl = ui.Label(frame=(20, slider_y, w-80, 25))
            tight_lbl.text = 'Opponent Style:  LOOSE ← → TIGHT'
            tight_lbl.text_color = 'white'
            tight_lbl.font = ('<system-bold>', 16)
            tight_lbl.alignment = ui.ALIGN_CENTER
            controls.add_subview(tight_lbl)

            self.tight_slider = ui.Slider(frame=(40, slider_y+30, w-120, 40))
            self.tight_slider.value = self.strategy.opponent_tightness
            self.tight_slider.action = self.update_opponent_sliders
            controls.add_subview(self.tight_slider)

            slider_y += 85

            agg_lbl = ui.Label(frame=(20, slider_y, w-80, 25))
            agg_lbl.text = 'Opponent Betting:  PASSIVE ← → AGGRESSIVE'
            agg_lbl.text_color = 'white'
            agg_lbl.font = ('<system-bold>', 16)
            agg_lbl.alignment = ui.ALIGN_CENTER
            controls.add_subview(agg_lbl)

            self.agg_slider = ui.Slider(frame=(40, slider_y+30, w-120, 40))
            self.agg_slider.value = self.strategy.opponent_aggression
            self.agg_slider.action = self.update_opponent_sliders
            controls.add_subview(self.agg_slider)

        y += controls_height + 15

        # HOLE CARDS SECTION
        hole_title = ui.Label(frame=(0, y, w, int(30 * font_scale)))
        hole_title.text = 'YOUR HOLE CARDS'
        hole_title.text_color = '#d4af37'
        hole_title.font = ('<system-bold>', int(20 * font_scale))
        hole_title.alignment = ui.ALIGN_CENTER
        scroll.add_subview(hole_title)
        y += int(35 * font_scale)

        # Hole card buttons
        self.hole_btns = []
        if self.is_iphone:
            card_w = 100
            card_h = 130
            gap = 20
            card_font = 48
        else:
            card_w = 150
            card_h = 200
            gap = 30
            card_font = 72

        start_x = (w - (2*card_w + gap)) / 2

        for i in range(2):
            btn = ui.Button(frame=(start_x + i*(card_w+gap), y, card_w, card_h))
            btn.title = '?'
            btn.background_color = 'white'
            btn.tint_color = 'black'
            btn.font = ('<system-bold>', card_font)
            btn.corner_radius = 10
            btn.border_width = 3
            btn.border_color = '#d4af37'
            btn.action = lambda s, idx=i: self.select_hole_card(idx)
            scroll.add_subview(btn)
            self.hole_btns.append(btn)

        y += card_h + 20

        # COMMUNITY CARDS SECTION
        comm_title = ui.Label(frame=(0, y, w, int(30 * font_scale)))
        comm_title.text = 'COMMUNITY CARDS'
        comm_title.text_color = '#d4af37'
        comm_title.font = ('<system-bold>', int(18 * font_scale))
        comm_title.alignment = ui.ALIGN_CENTER
        scroll.add_subview(comm_title)
        y += int(35 * font_scale)

        # Community cards
        self.comm_btns = []
        if self.is_iphone:
            comm_w = 60
            comm_h = 80
            comm_gap = 8
            comm_font = 32
        else:
            comm_w = 120
            comm_h = 160
            comm_gap = 15
            comm_font = 54

        comm_start = (w - (5*comm_w + 4*comm_gap)) / 2

        for i in range(5):
            btn = ui.Button(frame=(comm_start + i*(comm_w+comm_gap), y, comm_w, comm_h))
            btn.title = '?'
            btn.background_color = 'white'
            btn.tint_color = 'gray'
            btn.font = ('<system-bold>', comm_font)
            btn.corner_radius = 8
            btn.border_width = 2
            btn.border_color = 'gray'
            btn.action = lambda s, idx=i: self.select_comm_card(idx)
            scroll.add_subview(btn)
            self.comm_btns.append(btn)

        y += comm_h + 20

        # ANALYSIS SECTION
        analysis_height = int(250 * scale) if self.is_iphone else 320
        analysis = ui.View(frame=(10, y, w-20, analysis_height))
        analysis.background_color = '#0d2818'
        analysis.corner_radius = 10
        scroll.add_subview(analysis)

        # Win probability
        win_prob_title = ui.Label(frame=(0, 10, w-20, int(25 * font_scale)))
        win_prob_title.text = 'WIN PROBABILITY'
        win_prob_title.text_color = 'white'
        win_prob_title.font = ('<system-bold>', int(18 * font_scale))
        win_prob_title.alignment = ui.ALIGN_CENTER
        analysis.add_subview(win_prob_title)

        self.equity_lbl = ui.Label(frame=(0, int(35 * font_scale), w-20, int(60 * font_scale)))
        self.equity_lbl.text = '--%'
        self.equity_lbl.text_color = '#00ff00'
        self.equity_lbl.font = ('<system-bold>', int(52 * font_scale))
        self.equity_lbl.alignment = ui.ALIGN_CENTER
        analysis.add_subview(self.equity_lbl)

        self.hand_lbl = ui.Label(frame=(0, int(100 * font_scale), w-20, int(30 * font_scale)))
        self.hand_lbl.text = 'Select your cards'
        self.hand_lbl.text_color = 'white'
        self.hand_lbl.font = ('<system-bold>', int(16 * font_scale))
        self.hand_lbl.alignment = ui.ALIGN_CENTER
        analysis.add_subview(self.hand_lbl)

        # Recommendation
        rec_title = ui.Label(frame=(0, int(135 * font_scale), w-20, int(25 * font_scale)))
        rec_title.text = 'RECOMMENDATION'
        rec_title.text_color = '#d4af37'
        rec_title.font = ('<system-bold>', int(16 * font_scale))
        rec_title.alignment = ui.ALIGN_CENTER
        analysis.add_subview(rec_title)

        self.rec_lbl = ui.Label(frame=(10, int(165 * font_scale), w-40, int(80 * font_scale)))
        self.rec_lbl.text = 'Tap the ? buttons\nto select your cards'
        self.rec_lbl.text_color = '#ff6600'
        self.rec_lbl.font = ('<system-bold>', int(22 * font_scale))
        self.rec_lbl.alignment = ui.ALIGN_CENTER
        self.rec_lbl.number_of_lines = 0
        analysis.add_subview(self.rec_lbl)

        y += analysis_height + 15

        # NEW HAND BUTTON
        new_btn_height = int(55 * scale) if self.is_iphone else 70
        new_btn = ui.Button(frame=(10, y, w-20, new_btn_height))
        new_btn.title = '🔄 New Hand'
        new_btn.background_color = '#006400'
        new_btn.tint_color = 'white'
        new_btn.font = ('<system-bold>', int(20 * font_scale))
        new_btn.corner_radius = 10
        new_btn.action = self.new_hand
        scroll.add_subview(new_btn)

        y += new_btn_height + 20

        scroll.content_size = (w, y)

    def build_card_selector(self, callback):
        """Build FULL SCREEN card selector - adapts to device"""
        v = ui.View()
        v.name = 'Select Card'
        v.background_color = '#1a472a'

        screen = ui.get_screen_size()
        w = screen[0]
        h = screen[1]

        scroll = ui.ScrollView(frame=(0, 0, w, h))
        scroll.background_color = '#1a472a'
        v.add_subview(scroll)

        y = 20

        # Title
        font_scale = 0.7 if self.is_iphone else 1.0
        selector_title = ui.Label(frame=(0, y, w, int(50 * font_scale)))
        selector_title.text = '♠️ SELECT CARD ♥️'
        selector_title.text_color = 'white'
        selector_title.font = ('<system-bold>', int(28 * font_scale))
        selector_title.alignment = ui.ALIGN_CENTER
        scroll.add_subview(selector_title)
        y += int(60 * font_scale)

        # Card grid
        ranks = list(Card.RANKS)
        suits = ['♥️', '♦️', '♣️', '♠️']
        suit_chars = ['h', 'd', 'c', 's']
        suit_colors = ['red', 'red', 'black', 'black']

        if self.is_iphone:
            card_w = 55
            card_h = 75
            card_gap = 3
            card_font = 20
            suit_font = 42
            suit_width = 50
        else:
            card_w = 90
            card_h = 120
            card_gap = 5
            card_font = 28
            suit_font = 72
            suit_width = 80

        for suit_idx, (symbol, char, color) in enumerate(zip(suits, suit_chars, suit_colors)):
            # Suit label
            suit_lbl = ui.Label(frame=(10, y + 20, suit_width, suit_width))
            suit_lbl.text = symbol
            suit_lbl.text_color = color
            suit_lbl.font = ('<system>', suit_font)
            suit_lbl.alignment = ui.ALIGN_CENTER
            scroll.add_subview(suit_lbl)

            # Cards in suit
            x_start = suit_width + 15
            for rank_idx, rank in enumerate(ranks):
                card = Card(rank, char)
                if card in self.used_cards:
                    continue

                col = rank_idx % 6 if self.is_iphone else rank_idx % 7
                row = rank_idx // 6 if self.is_iphone else rank_idx // 7

                x_pos = x_start + col * (card_w + card_gap)
                y_pos = y + row * (card_h + card_gap)

                btn = ui.Button(frame=(x_pos, y_pos, card_w, card_h))
                btn.title = f"{rank}\n{symbol}"
                btn.background_color = 'white'
                btn.tint_color = color
                btn.font = ('<system-bold>', card_font)
                btn.corner_radius = 8
                btn.border_width = 2
                btn.border_color = '#d4af37'

                def make_action(c):
                    return lambda s: callback(c)

                btn.action = make_action(card)
                scroll.add_subview(btn)

            rows_needed = 3 if self.is_iphone else 2
            y += rows_needed * (card_h + card_gap) + 20

        # Cancel button
        cancel_w = int(250 * font_scale)
        cancel_h = int(60 * font_scale)
        cancel_btn = ui.Button(frame=(w/2 - cancel_w/2, y, cancel_w, cancel_h))
        cancel_btn.title = '✖ Cancel'
        cancel_btn.background_color = '#8b0000'
        cancel_btn.tint_color = 'white'
        cancel_btn.font = ('<system-bold>', int(24 * font_scale))
        cancel_btn.corner_radius = 12
        cancel_btn.action = lambda s: v.close()
        scroll.add_subview(cancel_btn)

        y += cancel_h + 30

        scroll.content_size = (w, y)

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
        self.card_selector_view.present('fullscreen')

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
        self.card_selector_view.present('fullscreen')

    def update_hole_display(self):
        """Update hole card buttons"""
        suit_symbols = {'h': '♥️', 'd': '♦️', 'c': '♣️', 's': '♠️'}

        for i, btn in enumerate(self.hole_btns):
            if i < len(self.hole_cards):
                card = self.hole_cards[i]
                btn.title = f"{card.rank}{suit_symbols[card.suit]}"
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
                btn.title = f"{card.rank}{suit_symbols[card.suit]}"
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
            self.street_lbl.text = '🎴 PRE-FLOP'
        elif n == 3:
            self.street = 'flop'
            self.street_lbl.text = '🎴 FLOP'
        elif n == 4:
            self.street = 'turn'
            self.street_lbl.text = '🎴 TURN'
        elif n == 5:
            self.street = 'river'
            self.street_lbl.text = '🎴 RIVER'

    def analyze(self):
        """Analyze hand and show recommendation"""
        if len(self.hole_cards) != 2:
            self.rec_lbl.text = 'Select 2 hole cards first'
            return

        try:
            if len(self.community_cards) == 0:
                # Pre-flop
                strength = self.strategy.get_preflop_hand_strength(self.hole_cards)
                self.equity_lbl.text = f"{strength}%"

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
                self.equity_lbl.text = f"{equity_data['win_pct']}%"

            # Color code equity
            if equity_data['win_pct'] >= 60:
                self.equity_lbl.text_color = '#00ff00'
            elif equity_data['win_pct'] >= 40:
                self.equity_lbl.text_color = '#ffff00'
            else:
                self.equity_lbl.text_color = '#ff6600'

            # Update hand
            self.hand_lbl.text = equity_data['current_hand']

            # Get recommendation
            rec = self.strategy.get_recommendation(
                equity_data,
                self.position,
                self.num_opponents,
                self.street,
                self.facing_bet
            )

            self.rec_lbl.text = f"⚡ {rec['action']} ⚡"

        except Exception as e:
            self.rec_lbl.text = f"Error: {str(e)}"

    def cycle_position(self, sender):
        """Cycle position"""
        positions = ['BTN', 'SB', 'BB', 'CO']
        idx = positions.index(self.position)
        self.position = positions[(idx + 1) % 4]
        self.pos_btn.title = self.position
        self.analyze()

    def adjust_opponents(self, delta):
        """Adjust opponents"""
        self.num_opponents = max(1, min(3, self.num_opponents + delta))
        self.opp_lbl.text = str(self.num_opponents)
        self.analyze()

    def toggle_facing_bet(self, sender):
        """Toggle facing bet"""
        self.facing_bet = sender.value
        self.analyze()

    def toggle_preflop_raise(self, sender):
        """Toggle pre-flop raise"""
        self.preflop_raise = sender.value
        self.analyze()

    def update_opponent_sliders(self, sender):
        """Update opponent tendencies from sliders"""
        self.strategy.update_opponent_tendencies(
            self.tight_slider.value,
            self.agg_slider.value
        )
        self.analyze()

    def new_hand(self, sender):
        """New hand"""
        # Rotate position
        positions = ['BTN', 'SB', 'BB', 'CO']
        idx = positions.index(self.position)
        self.position = positions[(idx + 1) % 4]
        self.pos_btn.title = self.position

        # Clear
        self.hole_cards = []
        self.community_cards = []
        self.used_cards = set()
        self.street = 'preflop'
        self.facing_bet = False
        self.bet_switch.value = False
        self.preflop_raise = False
        self.preflop_raise_switch.value = False

        # Reset display
        self.update_hole_display()
        self.update_comm_display()
        self.update_street()
        self.equity_lbl.text = '--%'
        self.equity_lbl.text_color = '#00ff00'
        self.hand_lbl.text = 'Select your cards'
        self.rec_lbl.text = 'Tap the ? buttons\nto select your cards'

    def run(self):
        """Run the app"""
        self.main_view.present('fullscreen', hide_title_bar=False)


if __name__ == '__main__':
    app = PokerAdvisorApp()
    app.run()
