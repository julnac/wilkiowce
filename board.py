import random

class Board:
    def __init__(self):
        # 0: puste, 1: owca, 2: wilk
        self.grid = [[0 for _ in range(8)] for _ in range(8)]
        self.setup_game()

    def setup_game(self):
        for c in range(1, 8, 2):
            self.grid[0][c] = 1
        
        wilk_cols = [0, 2, 4, 6]
        self.grid[7][random.choice(wilk_cols)] = 2

    def get_piece(self, r, c):
        return self.grid[r][c]

    def is_on_board(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def validate_move(self, fr, fc, tr, tc, player_type):

        if not self.is_on_board(tr, tc):
            return False, "Poza planszą"

        if self.grid[tr][tc] != 0:
            return False, "Pole zajęte"

        row_diff = tr - fr
        col_diff = abs(tc - fc)
        
        if col_diff != 1:
            return False, "Ruch musi być po skosie o 1 pole"

        piece = self.grid[fr][fc]
        if player_type == "OWCE":
            if piece != 1: return False, "To nie jest owca"
            if row_diff != 1:
                return False, "Owce nie mogą się cofać"
        
        elif player_type == "WILK":
            if piece != 2: return False, "To nie jest wilk"
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

        if wilk_pos[0] == 0:
            return "WILK"

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