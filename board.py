import random

class Board:
    def __init__(self):
        # 0: puste, 1: owca, 2: wilk
        self.grid = [[0 for _ in range(8)] for _ in range(8)]
        self.setup_game()

    def setup_game(self):
        # Owce: rząd 0, kolumny 1, 3, 5, 7
        for c in range(1, 8, 2):
            self.grid[0][c] = 1
        
        # Wilk: rząd 7, losowe czarne pole (0, 2, 4, 6)
        wilk_cols = [0, 2, 4, 6]
        self.grid[7][random.choice(wilk_cols)] = 2

    def get_piece(self, r, c):
        return self.grid[r][c]

    def is_on_board(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def validate_move(self, fr, fc, tr, tc, player_type):
        # 1. Czy docelowe pole jest na planszy?
        if not self.is_on_board(tr, tc):
            return False, "Poza planszą"

        # 2. Czy docelowe pole jest puste?
        if self.grid[tr][tc] != 0:
            return False, "Pole zajęte"

        # 3. Czy ruch jest po skosie o 1 pole?
        row_diff = tr - fr
        col_diff = abs(tc - fc)
        
        if col_diff != 1:
            return False, "Ruch musi być po skosie o 1 pole"

        # 4. Specyficzne zasady dla typów pionków
        piece = self.grid[fr][fc]
        if player_type == "OWCE":
            if piece != 1: return False, "To nie jest owca"
            # Owce poruszają się tylko "w dół" (zwiększanie indeksu rzędu)
            if row_diff != 1:
                return False, "Owce nie mogą się cofać"
        
        elif player_type == "WILK":
            if piece != 2: return False, "To nie jest wilk"
            # Wilk porusza się o 1 w dowolną stronę po skosie
            if abs(row_diff) != 1:
                return False, "Nieprawidłowy zasięg wilka"

        return True, "OK"

    def move_piece(self, fr, fc, tr, tc):
        piece = self.grid[fr][fc]
        self.grid[fr][fc] = 0
        self.grid[tr][tc] = piece

    def check_winner(self):

        wilk_pos = None
        for r in range(8):
            for c in range(8):
                if self.grid[r][c] == 2:
                    wilk_pos = (r, c)
                    break
        
        if not wilk_pos:
            return "OWCE"

        # Wilk wygrywa, gdy dotrze do rzędu 0
        if wilk_pos[0] == 0:
            return "WILK"

        # Owce wygrywają, gdy wilk nie ma ruchu
        r, c = wilk_pos
        possible_moves = [(r-1, c-1), (r-1, c+1), (r+1, c-1), (r+1, c+1)]
        can_move = False
        for tr, tc in possible_moves:
            if self.is_on_board(tr, tc) and self.grid[tr][tc] == 0:
                can_move = True
                break
        
        if not can_move:
            return "OWCE"

        return None