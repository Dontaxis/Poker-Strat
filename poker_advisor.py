"""
Poker Strategy Advisor - Main Application
Pythonista 3 optimized UI for iPad - ULTRA SIMPLIFIED VERSION
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
        """Build the main interface - SIMPLIFIED"""
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

        # Position
        ui.Label(frame=(20, 15, 120, 30), text='Position:', text_color='white',
                 font=('<system-bold>', 18)).add_to(controls)

        self.pos_btn = ui.Button(frame=(150, 10, 120, 50))
        self.pos_btn.title = self.position
        self.pos_btn.background_color = '#d4af37'
        self.pos_btn.tint_color = 'black'
        self.pos_btn.font = ('<system-bold>', 24)
        self.pos_btn.corner_radius = 10
        self.pos_btn.action = self.cycle_position
        controls.add_subview(self.pos_btn)

        # Opponents
        ui.Label(frame=(300, 15, 150, 30), text='Opponents:', text_color='white',
                 font=('<system-bold>', 18)).add_to(controls)

        self.opp_lbl = ui.Label(frame=(460, 10, 80, 50))
        self.opp_lbl.text = str(self.num_opponents)
        self.opp_lbl.text_color = '#d4af37'
        self.opp_lbl.font = ('<system-bold>', 36)
        self.opp_lbl.alignment = ui.ALIGN_CENTER
        controls.add_subview(self.opp_lbl)

        ui.Button(frame=(550, 10, 70, 50), title='-', background_color='#8b0000',
                 tint_color='white', font=('<system-bold>', 28), corner_radius=10,
                 action=lambda s: self.adjust_opponents(-1)).add_to(controls)

        ui.Button(frame=(630, 10, 70, 50), title='+', background_color='#006400',
                 tint_color='white', font=('<system-bold>', 28), corner_radius=10,
                 action=lambda s: self.adjust_opponents(1)).add_to(controls)

        # Street & Facing Bet
        self.street_lbl = ui.Label(frame=(20, 75, w-80, 30))
        self.street_lbl.text = '🎴 PRE-FLOP'
        self.street_lbl.text_color = '#d4af37'
        self.street_lbl.font = ('<system-bold>', 22)
        self.street_lbl.alignment = ui.ALIGN_CENTER
        controls.add_subview(self.street_lbl)

        ui.Label(frame=(20, 110, 140, 25), text='Facing Bet?', text_color='white',
                 font=('<system>', 16)).add_to(controls)

        self.bet_switch = ui.Switch(frame=(170, 108, 60, 30))
        self.bet_switch.value = False
        self.bet_switch.action = self.toggle_facing_bet
        controls.add_subview(self.bet_switch)

        y += 155

        # HOLE CARDS SECTION
        ui.Label(frame=(0, y, w, 35), text='YOUR HOLE CARDS', text_color='#d4af37',
                 font=('<system-bold>', 24), alignment=ui.ALIGN_CENTER).add_to(scroll)
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
        ui.Label(frame=(0, y, w, 35), text='COMMUNITY CARDS (FLOP/TURN/RIVER)',
                 text_color='#d4af37', font=('<system-bold>', 24),
                 alignment=ui.ALIGN_CENTER).add_to(scroll)
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

        ui.Label(frame=(0, 15, w-40, 30), text='WIN PROBABILITY', text_color='white',
                 font=('<system-bold>', 22), alignment=ui.ALIGN_CENTER).add_to(analysis)

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

        ui.Label(frame=(0, 180, w-40, 30), text='RECOMMENDATION', text_color='#d4af37',
                 font=('<system-bold>', 20), alignment=ui.ALIGN_CENTER).add_to(analysis)

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

        ui.Button(frame=(20, y, btn_w, 70), title='⚙️ Opponent Settings',
                 background_color='#4a4a4a', tint_color='white',
                 font=('<system-bold>', 22), corner_radius=12,
                 action=self.show_settings).add_to(scroll)

        ui.Button(frame=(40 + btn_w, y, btn_w, 70), title='🔄 New Hand',
                 background_color='#006400', tint_color='white',
                 font=('<system-bold>', 22), corner_radius=12,
                 action=self.new_hand).add_to(scroll)

        y += 85

        scroll.content_size = (w, y + 20)

    def build_card_selector(self, callback):
        """Build BIGGER card selection popup"""
        v = ui.View()
        v.name = 'Select Card'
        v.background_color = '#1a472a'

        # Make it bigger and scrollable
        w = 750
        h = 500

        # Title
        ui.Label(frame=(0, 20, w, 50), text='TAP TO SELECT CARD', text_color='white',
                 font=('<system-bold>', 28), alignment=ui.ALIGN_CENTER).add_to(v)

        # Card grid with bigger buttons
        ranks = list(Card.RANKS)
        suits = ['♥️', '♦️', '♣️', '♠️']
        suit_chars = ['h', 'd', 'c', 's']
        suit_colors = ['red', 'red', 'black', 'black']

        card_size = 52
        y_start = 85

        for suit_idx, (symbol, char, color) in enumerate(zip(suits, suit_chars, suit_colors)):
            # Suit label - BIGGER
            ui.Label(frame=(15, y_start + suit_idx*80, 50, 60), text=symbol,
                    text_color=color, font=('<system>', 42),
                    alignment=ui.ALIGN_CENTER).add_to(v)

            # Cards - BIGGER with suit symbols
            for rank_idx, rank in enumerate(ranks):
                card = Card(rank, char)
                if card in self.used_cards:
                    continue

                btn = ui.Button(frame=(75 + rank_idx*52, y_start + suit_idx*80, card_size, card_size))
                btn.title = f"{rank}\n{symbol}"
                btn.background_color = 'white'
                btn.tint_color = color
                btn.font = ('<system-bold>', 16)
                btn.corner_radius = 6

                def make_action(c):
                    return lambda s: callback(c)

                btn.action = make_action(card)
                v.add_subview(btn)

        # Cancel button - BIGGER
        ui.Button(frame=(w/2-120, h-70, 240, 60), title='Cancel',
                 background_color='#8b0000', tint_color='white',
                 font=('<system-bold>', 24), corner_radius=12,
                 action=lambda s: v.close()).add_to(v)

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
        self.card_selector_view.present('sheet')

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
        self.card_selector_view.present('sheet')

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
        """Show settings"""
        v = ui.View()
        v.name = 'Opponent Settings'
        v.background_color = '#1a472a'

        w = 650
        h = 400

        # Title
        ui.Label(frame=(0, 30, w, 50), text='OPPONENT TENDENCIES', text_color='white',
                 font=('<system-bold>', 28), alignment=ui.ALIGN_CENTER).add_to(v)

        y = 100

        # Tightness
        ui.Label(frame=(30, y, w-60, 35), text='Playing Style: LOOSE ← → TIGHT',
                 text_color='white', font=('<system-bold>', 20),
                 alignment=ui.ALIGN_CENTER).add_to(v)

        tight_slider = ui.Slider(frame=(60, y+45, w-120, 40))
        tight_slider.value = self.strategy.opponent_tightness
        v.add_subview(tight_slider)

        y += 110

        # Aggression
        ui.Label(frame=(30, y, w-60, 35), text='Betting Style: PASSIVE ← → AGGRESSIVE',
                 text_color='white', font=('<system-bold>', 20),
                 alignment=ui.ALIGN_CENTER).add_to(v)

        agg_slider = ui.Slider(frame=(60, y+45, w-120, 40))
        agg_slider.value = self.strategy.opponent_aggression
        v.add_subview(agg_slider)

        # Save button
        def save(s):
            self.strategy.update_opponent_tendencies(
                tight_slider.value,
                agg_slider.value
            )
            self.analyze()
            v.close()

        ui.Button(frame=(w/2-140, h-80, 280, 60), title='✓ Save & Update',
                 background_color='#006400', tint_color='white',
                 font=('<system-bold>', 24), corner_radius=12,
                 action=save).add_to(v)

        v.present('sheet')

    def run(self):
        """Run the app"""
        self.main_view.present('fullscreen', hide_title_bar=False)


if __name__ == '__main__':
    app = PokerAdvisorApp()
    app.run()
