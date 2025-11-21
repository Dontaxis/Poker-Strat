"""
Poker Strategy Advisor - Main Application
Pythonista 3 optimized UI for iPad
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
        self.used_cards = set()

        self.main_view = None
        self.build_ui()

    def build_ui(self):
        """Build the main interface"""
        self.main_view = ui.View()
        self.main_view.name = 'Poker Advisor'
        self.main_view.background_color = '#1a472a'

        # Use full screen
        screen = ui.get_screen_size()
        w = screen[0]
        h = screen[1]

        # Scrollview for everything
        scroll = ui.ScrollView(frame=(0, 0, w, h))
        scroll.background_color = '#1a472a'
        self.main_view.add_subview(scroll)

        y = 20

        # TITLE
        title = ui.Label(frame=(0, y, w, 50))
        title.text = '♠️ POKER ADVISOR ♥️'
        title.font = ('<system-bold>', 32)
        title.text_color = 'white'
        title.alignment = ui.ALIGN_CENTER
        scroll.add_subview(title)
        y += 60

        # POSITION & OPPONENTS
        controls = ui.View(frame=(20, y, w-40, 140))
        controls.background_color = '#0d2818'
        controls.corner_radius = 10
        scroll.add_subview(controls)

        # Position label
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

        # Opponents label
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

        # Minus button
        btn_minus = ui.Button(frame=(550, 10, 70, 50))
        btn_minus.title = '-'
        btn_minus.background_color = '#8b0000'
        btn_minus.tint_color = 'white'
        btn_minus.font = ('<system-bold>', 28)
        btn_minus.corner_radius = 10
        btn_minus.action = lambda s: self.adjust_opponents(-1)
        controls.add_subview(btn_minus)

        # Plus button
        btn_plus = ui.Button(frame=(630, 10, 70, 50))
        btn_plus.title = '+'
        btn_plus.background_color = '#006400'
        btn_plus.tint_color = 'white'
        btn_plus.font = ('<system-bold>', 28)
        btn_plus.corner_radius = 10
        btn_plus.action = lambda s: self.adjust_opponents(1)
        controls.add_subview(btn_plus)

        # Street label
        self.street_lbl = ui.Label(frame=(20, 75, w-80, 30))
        self.street_lbl.text = '🎴 PRE-FLOP'
        self.street_lbl.text_color = '#d4af37'
        self.street_lbl.font = ('<system-bold>', 22)
        self.street_lbl.alignment = ui.ALIGN_CENTER
        controls.add_subview(self.street_lbl)

        # Facing bet label
        bet_label = ui.Label(frame=(20, 110, 140, 25))
        bet_label.text = 'Facing Bet?'
        bet_label.text_color = 'white'
        bet_label.font = ('<system>', 16)
        controls.add_subview(bet_label)

        self.bet_switch = ui.Switch(frame=(170, 108, 60, 30))
        self.bet_switch.value = False
        self.bet_switch.action = self.toggle_facing_bet
        controls.add_subview(self.bet_switch)

        y += 155

        # HOLE CARDS SECTION
        hole_title = ui.Label(frame=(0, y, w, 35))
        hole_title.text = 'YOUR HOLE CARDS'
        hole_title.text_color = '#d4af37'
        hole_title.font = ('<system-bold>', 24)
        hole_title.alignment = ui.ALIGN_CENTER
        scroll.add_subview(hole_title)
        y += 40

        # Hole card buttons - BIGGER
        self.hole_btns = []
        card_w = 150
        card_h = 200
        gap = 30
        start_x = (w - (2*card_w + gap)) / 2

        for i in range(2):
            btn = ui.Button(frame=(start_x + i*(card_w+gap), y, card_w, card_h))
            btn.title = '?'
            btn.background_color = 'white'
            btn.tint_color = 'black'
            btn.font = ('<system-bold>', 72)
            btn.corner_radius = 12
            btn.border_width = 4
            btn.border_color = '#d4af37'
            btn.action = lambda s, idx=i: self.select_hole_card(idx)
            scroll.add_subview(btn)
            self.hole_btns.append(btn)

        y += card_h + 30

        # COMMUNITY CARDS SECTION
        comm_title = ui.Label(frame=(0, y, w, 35))
        comm_title.text = 'COMMUNITY CARDS (FLOP/TURN/RIVER)'
        comm_title.text_color = '#d4af37'
        comm_title.font = ('<system-bold>', 24)
        comm_title.alignment = ui.ALIGN_CENTER
        scroll.add_subview(comm_title)
        y += 40

        # Community cards - BIGGER
        self.comm_btns = []
        comm_w = 120
        comm_h = 160
        comm_gap = 15
        comm_start = (w - (5*comm_w + 4*comm_gap)) / 2

        for i in range(5):
            btn = ui.Button(frame=(comm_start + i*(comm_w+comm_gap), y, comm_w, comm_h))
            btn.title = '?'
            btn.background_color = 'white'
            btn.tint_color = 'gray'
            btn.font = ('<system-bold>', 54)
            btn.corner_radius = 10
            btn.border_width = 3
            btn.border_color = 'gray'
            btn.action = lambda s, idx=i: self.select_comm_card(idx)
            scroll.add_subview(btn)
            self.comm_btns.append(btn)

        y += comm_h + 30

        # ANALYSIS SECTION - BIGGER
        analysis = ui.View(frame=(20, y, w-40, 320))
        analysis.background_color = '#0d2818'
        analysis.corner_radius = 10
        scroll.add_subview(analysis)

        # Win probability label
        win_prob_title = ui.Label(frame=(0, 15, w-40, 30))
        win_prob_title.text = 'WIN PROBABILITY'
        win_prob_title.text_color = 'white'
        win_prob_title.font = ('<system-bold>', 22)
        win_prob_title.alignment = ui.ALIGN_CENTER
        analysis.add_subview(win_prob_title)

        self.equity_lbl = ui.Label(frame=(0, 50, w-40, 80))
        self.equity_lbl.text = '--%'
        self.equity_lbl.text_color = '#00ff00'
        self.equity_lbl.font = ('<system-bold>', 72)
        self.equity_lbl.alignment = ui.ALIGN_CENTER
        analysis.add_subview(self.equity_lbl)

        self.hand_lbl = ui.Label(frame=(0, 135, w-40, 35))
        self.hand_lbl.text = 'Select your cards'
        self.hand_lbl.text_color = 'white'
        self.hand_lbl.font = ('<system-bold>', 20)
        self.hand_lbl.alignment = ui.ALIGN_CENTER
        analysis.add_subview(self.hand_lbl)

        # Recommendation title
        rec_title = ui.Label(frame=(0, 180, w-40, 30))
        rec_title.text = 'RECOMMENDATION'
        rec_title.text_color = '#d4af37'
        rec_title.font = ('<system-bold>', 20)
        rec_title.alignment = ui.ALIGN_CENTER
        analysis.add_subview(rec_title)

        self.rec_lbl = ui.Label(frame=(20, 215, w-80, 100))
        self.rec_lbl.text = 'Tap the ? buttons above\nto select your cards'
        self.rec_lbl.text_color = '#ff6600'
        self.rec_lbl.font = ('<system-bold>', 28)
        self.rec_lbl.alignment = ui.ALIGN_CENTER
        self.rec_lbl.number_of_lines = 0
        analysis.add_subview(self.rec_lbl)

        y += 335

        # ACTION BUTTONS - BIGGER
        btn_w = (w - 60) / 2

        settings_btn = ui.Button(frame=(20, y, btn_w, 70))
        settings_btn.title = '⚙️ Opponent Settings'
        settings_btn.background_color = '#4a4a4a'
        settings_btn.tint_color = 'white'
        settings_btn.font = ('<system-bold>', 22)
        settings_btn.corner_radius = 12
        settings_btn.action = self.show_settings
        scroll.add_subview(settings_btn)

        new_btn = ui.Button(frame=(40 + btn_w, y, btn_w, 70))
        new_btn.title = '🔄 New Hand'
        new_btn.background_color = '#006400'
        new_btn.tint_color = 'white'
        new_btn.font = ('<system-bold>', 22)
        new_btn.corner_radius = 12
        new_btn.action = self.new_hand
        scroll.add_subview(new_btn)

        y += 85

        scroll.content_size = (w, y + 20)

    def build_card_selector(self, callback):
        """Build FULL SCREEN card selector with scrolling"""
        v = ui.View()
        v.name = 'Select Card'
        v.background_color = '#1a472a'

        # FULL SCREEN
        screen = ui.get_screen_size()
        w = screen[0]
        h = screen[1]

        # Add ScrollView so everything is visible
        scroll = ui.ScrollView(frame=(0, 0, w, h))
        scroll.background_color = '#1a472a'
        v.add_subview(scroll)

        y = 20

        # Title - HUGE
        selector_title = ui.Label(frame=(0, y, w, 60))
        selector_title.text = '♠️ TAP TO SELECT CARD ♥️'
        selector_title.text_color = 'white'
        selector_title.font = ('<system-bold>', 36)
        selector_title.alignment = ui.ALIGN_CENTER
        scroll.add_subview(selector_title)
        y += 80

        # Card grid with HUGE buttons
        ranks = list(Card.RANKS)
        suits = ['♥️', '♦️', '♣️', '♠️']
        suit_chars = ['h', 'd', 'c', 's']
        suit_colors = ['red', 'red', 'black', 'black']

        # MASSIVE cards - easy to see and tap
        card_w = 90
        card_h = 120
        card_gap = 5

        for suit_idx, (symbol, char, color) in enumerate(zip(suits, suit_chars, suit_colors)):
            # Suit label - HUGE
            suit_lbl = ui.Label(frame=(20, y + 40, 80, 80))
            suit_lbl.text = symbol
            suit_lbl.text_color = color
            suit_lbl.font = ('<system>', 72)
            suit_lbl.alignment = ui.ALIGN_CENTER
            scroll.add_subview(suit_lbl)

            # Cards in this suit - HUGE buttons
            x_start = 110
            for rank_idx, rank in enumerate(ranks):
                card = Card(rank, char)
                if card in self.used_cards:
                    continue

                # Calculate position (wrap to multiple rows if needed)
                col = rank_idx % 7  # 7 cards per row
                row = rank_idx // 7

                x_pos = x_start + col * (card_w + card_gap)
                y_pos = y + row * (card_h + card_gap)

                btn = ui.Button(frame=(x_pos, y_pos, card_w, card_h))
                btn.title = f"{rank}\n{symbol}"
                btn.background_color = 'white'
                btn.tint_color = color
                btn.font = ('<system-bold>', 28)
                btn.corner_radius = 10
                btn.border_width = 2
                btn.border_color = '#d4af37'

                def make_action(c):
                    return lambda s: callback(c)

                btn.action = make_action(card)
                scroll.add_subview(btn)

            # Space between suits (13 cards = 2 rows)
            y += 2 * (card_h + card_gap) + 30

        # Cancel button - HUGE at bottom
        cancel_btn = ui.Button(frame=(w/2-200, y, 400, 80))
        cancel_btn.title = '✖ Cancel'
        cancel_btn.background_color = '#8b0000'
        cancel_btn.tint_color = 'white'
        cancel_btn.font = ('<system-bold>', 32)
        cancel_btn.corner_radius = 15
        cancel_btn.action = lambda s: v.close()
        scroll.add_subview(cancel_btn)

        y += 100

        # Set scroll content size
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

        # Reset display
        self.update_hole_display()
        self.update_comm_display()
        self.update_street()
        self.equity_lbl.text = '--%'
        self.equity_lbl.text_color = '#00ff00'
        self.hand_lbl.text = 'Select your cards'
        self.rec_lbl.text = 'Tap the ? buttons above\nto select your cards'

    def show_settings(self, sender):
        """Show settings - FULLSCREEN"""
        v = ui.View()
        v.name = 'Opponent Settings'
        v.background_color = '#1a472a'

        # FULL SCREEN
        screen = ui.get_screen_size()
        w = screen[0]
        h = screen[1]

        # Title
        settings_title = ui.Label(frame=(0, 80, w, 60))
        settings_title.text = '⚙️ OPPONENT TENDENCIES ⚙️'
        settings_title.text_color = 'white'
        settings_title.font = ('<system-bold>', 36)
        settings_title.alignment = ui.ALIGN_CENTER
        v.add_subview(settings_title)

        y = 200

        # Tightness label
        tight_label = ui.Label(frame=(40, y, w-80, 50))
        tight_label.text = 'Playing Style: LOOSE ← → TIGHT'
        tight_label.text_color = 'white'
        tight_label.font = ('<system-bold>', 26)
        tight_label.alignment = ui.ALIGN_CENTER
        v.add_subview(tight_label)

        tight_slider = ui.Slider(frame=(80, y+70, w-160, 50))
        tight_slider.value = self.strategy.opponent_tightness
        v.add_subview(tight_slider)

        y += 180

        # Aggression label
        agg_label = ui.Label(frame=(40, y, w-80, 50))
        agg_label.text = 'Betting Style: PASSIVE ← → AGGRESSIVE'
        agg_label.text_color = 'white'
        agg_label.font = ('<system-bold>', 26)
        agg_label.alignment = ui.ALIGN_CENTER
        v.add_subview(agg_label)

        agg_slider = ui.Slider(frame=(80, y+70, w-160, 50))
        agg_slider.value = self.strategy.opponent_aggression
        v.add_subview(agg_slider)

        y += 200

        # Save button - HUGE
        def save(s):
            self.strategy.update_opponent_tendencies(
                tight_slider.value,
                agg_slider.value
            )
            self.analyze()
            v.close()

        save_btn = ui.Button(frame=(w/2-200, y, 400, 80))
        save_btn.title = '✓ Save & Update'
        save_btn.background_color = '#006400'
        save_btn.tint_color = 'white'
        save_btn.font = ('<system-bold>', 32)
        save_btn.corner_radius = 15
        save_btn.action = save
        v.add_subview(save_btn)

        y += 100

        # Cancel button - HUGE
        cancel_btn = ui.Button(frame=(w/2-200, y, 400, 80))
        cancel_btn.title = '✖ Cancel'
        cancel_btn.background_color = '#8b0000'
        cancel_btn.tint_color = 'white'
        cancel_btn.font = ('<system-bold>', 32)
        cancel_btn.corner_radius = 15
        cancel_btn.action = lambda s: v.close()
        v.add_subview(cancel_btn)

        v.present('fullscreen')

    def run(self):
        """Run the app"""
        self.main_view.present('fullscreen', hide_title_bar=False)


if __name__ == '__main__':
    app = PokerAdvisorApp()
    app.run()
