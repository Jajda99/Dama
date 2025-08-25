import random
from heuristics import evaluate_position
import time

class Player:
    def __init__(self, color):
        self.color = color

    def get_move(self, game):
        raise NotImplementedError()
    
    def is_ai_player(self):
        return False

class HumanPlayer(Player):
    def __init__(self, color):
        super().__init__(color)
        self._selected = None        # (x, y) počátek tahu
        self.dalsi_tah = None 
        
    def get_move(self, game):
        """Vrátí tah, jakmile je připraven (jinak None)."""
        if self.dalsi_tah is not None:
            move = self.dalsi_tah
            self.dalsi_tah = None
            return move
        return None
    
    def is_ai_player(self):
        return False

class AIPlayer(Player):
    def __init__(self, color):
        super().__init__(color)

    def is_ai_player(self):
        return True

    def get_move(self, game):
        """Vrátí nejlepší tah podle heuristické funkce."""
        color = self.color
        board = game.board
        
        # Generování možných tahů
        def gen_moves(skok):
            """Generuje všechny možné tahy (skoky nebo kroky)."""
            moves = []
            my_figs_w, my_figs_b = game.vsechny_figurky()
            my_figs = my_figs_w if color == "white" else my_figs_b
            
            for x, y in my_figs:
                p = board.pole[x][y]
                for dx, dy in (p.skok() if skok else p.krok()):
                    x2, y2 = x + dx, (y + dy) % 8
                    if not board.je_v_poli(x2, y2) or not board.je_volne(x2, y2):
                        continue
                    if p.type == "pawn" and ((color == "white" and dx < 0) or (color == "black" and dx > 0)):
                        continue
                    if skok:
                        mx, my = (x + x2) // 2, board.middle_col(y, y2)
                        victim = board.pole[mx][my]
                        if victim == 0 or victim.color == color:
                            continue
                    moves.append((x, y, x2, y2))
            return moves

        # Simulace tahu a vyhodnocení pozice
        def evaluate_move(move):
            """Simuluje tah a vrací ohodnocení výsledné pozice."""
            x1, y1, x2, y2 = move
            
            # Uložení původního stavu
            original_piece = board.pole[x1][y1]
            target = board.pole[x2][y2]
            
            # Simulace tahu
            board.pole[x2][y2] = original_piece
            board.pole[x1][y1] = 0
            
            # U skoku odstraníme přeskočenou figurku
            is_jump = abs(x2 - x1) == 2
            if is_jump:
                mx = (x1 + x2) // 2
                my = board.middle_col(y1, y2)
                captured = board.pole[mx][my]
                board.pole[mx][my] = 0
            
            # Vyhodnocení pozice
            score = evaluate_position(game, color)
            
            # Obnova původního stavu
            board.pole[x1][y1] = original_piece
            board.pole[x2][y2] = target
            if is_jump:
                board.pole[mx][my] = captured
                
            return score
        
        # Vybereme typ tahů podle pravidel
        if game.moznostSkoku(color):
            # Pokud existuje povinný skok, musíme ho provést
            possible_moves = gen_moves(True)
        else:
            # Jinak můžeme provést normální tah
            possible_moves = gen_moves(False)
            
        if not possible_moves:
            return None
        
        # Ohodnocení všech možných tahů
        moves_with_scores = [(move, evaluate_move(move)) for move in possible_moves]
        
        # Seřazení tahů podle skóre (od nejlepšího)
        moves_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Vybereme nejlepší tah (případně náhodně z několika nejlepších)
        best_score = moves_with_scores[0][1]
        best_moves = [move for move, score in moves_with_scores if score == best_score]
        time.sleep(1.5)
        return random.choice(best_moves)


