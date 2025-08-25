import unittest
from board import Board
from game import Game
from player import Player, HumanPlayer, AIPlayer
from piece import Piece

class BoardTests(unittest.TestCase):
    def setUp(self):
        """Připraví desku pro testy"""
        self.board = Board()
        
    def test_initialization(self):
        # Testuje, že deska je inicializována se správnými figurkami
        self.assertEqual(self.board.pole[0][1].color, "white")
        self.assertEqual(self.board.pole[6][1].color, "black")
        
    def test_je_v_poli(self):
        # Testuje kontrolu hranic desky
        self.assertTrue(self.board.je_v_poli(0, 0))
        self.assertTrue(self.board.je_v_poli(7, 7))
        self.assertFalse(self.board.je_v_poli(8, 0))
        self.assertTrue(self.board.je_v_poli(0, 8))  # Should wrap around
        
    def test_perform_jump(self):
        # Nastaví situaci, kdy je možné provést skok
        self.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        self.board.pole[2][2] = Piece("white", "pawn")
        self.board.pole[3][3] = Piece("black", "pawn")
        self.board.pole[4][4] = 0  # Destination is empty
        
        # Provede skok
        self.board.perform_jump(2, 2, 4, 4)
        
        # Kontroluje, že figurky se přesunuly správně
        self.assertEqual(self.board.pole[2][2], 0)  # Original position empty
        self.assertEqual(self.board.pole[3][3], 0)  # Jumped piece removed
        self.assertNotEqual(self.board.pole[4][4], 0)  # Destination has piece
        self.assertEqual(self.board.pole[4][4].color, "white")
    
    def test_no_moves_condition(self):
        # Testuje, že funkce no_moves_available funguje správně
        self.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        
        # Nastaví situaci, kdy bílý nemá žádné tahy
        self.board.pole[1][1] = Piece("white", "pawn")
        self.board.pole[2][0] = Piece("black", "pawn")
        self.board.pole[2][2] = Piece("black", "pawn")
        self.board.pole[3][3] = Piece("black", "pawn")
        self.board.pole[3][7] = Piece("black", "pawn")
        
        # Mělo by vrátit True (bílý nemá žádné tahy)
        self.assertTrue(self.board.no_moves_available("white"))
        self.assertFalse(self.board.no_moves_available("black"))
        
    def test_kruhova_deska(self):
        """Test pohybů na kruhové desce"""
        self.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        
        # Umístíme bílého pěšce na pozici [2,0]
        self.board.pole[2][0] = Piece("white", "pawn")
        
        # Zkontrolujeme možnost pohybu "za roh" desky z [2,0] na [3,7]
        self.assertTrue(self.board.je_v_poli(3, 7))
        self.assertTrue(self.board.je_volne(3, 7))
        
        # Zkusíme skok přes okraj desky
        self.board.pole[3][7] = Piece("black", "pawn")
        self.board.pole[4][6] = 0  # Cíl je prázdný
        
        # Provést skok z [2,0] přes [3,7] na [4,6]
        result = self.board.perform_jump(2, 0, 4, 6)
        
        # Kontrola správnosti skoku
        self.assertEqual(self.board.pole[2][0], 0)  # Původní pozice prázdná
        self.assertEqual(self.board.pole[3][7], 0)  # Přeskočená figurka odstraněna
        self.assertNotEqual(self.board.pole[4][6], 0)  # Cílová pozice má figurku
        self.assertEqual(self.board.pole[4][6].color, "white")
    
    def test_povyseni_na_damu(self):
        """Test povýšení pěšce na dámu"""
        self.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        
        # Umístíme bílého pěšce těsně před poslední řadu
        self.board.pole[6][2] = Piece("white", "pawn")
        
        # Provedeme tah do poslední řady
        self.board.pole[7][3] = 0  # Ujistíme se, že cíl je prázdný
        
        # Vytvoříme instanci hry pro použití funkce play_turn
        game = Game(HumanPlayer("white"), HumanPlayer("black"))
        game.board = self.board  # Použijeme náš připravený board
        
        # Použijeme play_turn pro provedení tahu (správná metoda pro pohyb figurek)
        game.play_turn(6, 2, 7, 3)
        
        # Kontrola, že pěšec byl povýšen na dámu
        self.assertNotEqual(self.board.pole[7][3], 0)  # Cílová pozice má figurku
        self.assertEqual(self.board.pole[7][3].color, "white")  # Figurka je bílá
        self.assertEqual(self.board.pole[7][3].type, "queen")  # Figurka je dáma (oprava atributu z 'typ' na 'type')
        
    def test_nelze_tahnout_zpet(self):
        # Pokus o tah zpět by měl vyvolat výjimku
        game = Game(HumanPlayer("white"), HumanPlayer("black"))
        game.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        game.board.pole[3][3] = Piece("white", "pawn")

        with self.assertRaises(ValueError):
            # Bílý pěšec se pokouší táhnout zpět (dolů)
            game.play_turn(3, 3, 2, 2)  # Tah diagonálně dolů vpravo

        with self.assertRaises(ValueError):
            # Bílý pěšec se pokouší táhnout zpět (dolů)
            game.play_turn(3, 3, 2, 4)  # Tah diagonálně dolů vlevo
    
    def test_vicenasobny_skok(self):
        """Test vícenásobného skoku"""
        self.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        
        # Nastavíme situaci pro vícenásobný skok
        self.board.pole[2][2] = Piece("white", "pawn")
        self.board.pole[3][3] = Piece("black", "pawn")
        self.board.pole[5][5] = Piece("black", "pawn")
        
        # Kontrola detekce možnosti skoku
        self.assertTrue(self.board.moznostSkoku("white"))
        
        # První skok
        self.board.perform_jump(2, 2, 4, 4)
        
        # Kontrola prvního skoku
        self.assertEqual(self.board.pole[3][3], 0)  # První přeskočená figurka
        self.assertEqual(self.board.pole[4][4].color, "white")  # Figurka na mezipozici
        
        # Druhý skok
        self.board.perform_jump(4, 4, 6, 6)
        
        # Kontrola druhého skoku
        self.assertEqual(self.board.pole[5][5], 0)  # Druhá přeskočená figurka
        self.assertEqual(self.board.pole[4][4], 0)  # Startovní pozice je prázdná
        self.assertEqual(self.board.pole[6][6].color, "white")  # Figurka na konečné pozici
        
class GameTests(unittest.TestCase):
    def setUp(self):
        self.player1 = HumanPlayer("white")
        self.player2 = HumanPlayer("black")
        self.game = Game(self.player1, self.player2)
        
    def test_game_initialization(self):
        # Testuje, že hra se správně inicializuje
        self.assertEqual(self.game.current_player, "white")
        
    def test_play_turn(self):
        # Testuje jednoduchý tah
        self.game.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        self.game.board.pole[2][2] = Piece("white", "pawn")
        
        # Posune bílého pěšce
        self.game.play_turn(2, 2, 3, 3)
        
        # Kontroluje, že figurka se přesunula
        self.assertEqual(self.game.board.pole[2][2], 0)
        self.assertNotEqual(self.game.board.pole[3][3], 0)
        
        # Kontroluje, že se změnil hráč na tahu
        self.assertEqual(self.game.current_player, "black")
    
    def test_povinny_skok(self):
        """Test pravidla povinného skoku"""
        self.game.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        
        # Nastavíme situaci, kde je možný skok
        self.game.board.pole[2][2] = Piece("white", "pawn")
        self.game.board.pole[3][3] = Piece("black", "pawn")
        self.game.board.pole[1][1] = Piece("white", "pawn")  # Jiná bílá figurka
        
        # Pokus o běžný tah by měl selhat, protože je k dispozici skok
        with self.assertRaises(ValueError):
            self.game.play_turn(1, 1, 2, 2)  # Běžný tah
        
        # Kontrola, že figurky zůstaly na svých místech
        self.assertEqual(self.game.board.pole[1][1].color, "white")
        self.assertEqual(self.game.board.pole[3][3].color, "black")
    
    def test_konec_hry_blokovane_figurky(self):
        """Test konce hry, když jsou všechny figurky zablokovány"""
        self.game.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        
        # Nastavíme situaci, kde černý nemá možnost tahu
        self.game.board.pole[5][6] = Piece("black", "pawn")
        self.game.board.pole[4][5] = Piece("white", "pawn")
        self.game.board.pole[4][7] = Piece("white", "pawn")
        self.game.board.pole[3][4] = Piece("white", "pawn")
        self.game.board.pole[3][0] = Piece("white", "pawn")
        
        # Nastavíme, že je na tahu černý
        self.game.current = 1
        self.game.current_player = "black"
        
        # Test detekce zablokovaných figurek
        self.assertTrue(self.game.board.no_moves_available("black"))

        self.test_game_ends_when_no_moves()

    def test_game_ends_when_no_moves(self):
        """Test že hra správně končí, když hráč nemá možné tahy"""
        # Nastavení scénáře, kde černý nemá možné tahy
        self.game.board.pole = [[0 for _ in range(8)] for _ in range(8)]
        
        # Umístíme černé figurky na pozice bez možnosti tahu
        self.game.board.pole[7][1] = Piece("black", "pawn")
        self.game.board.pole[6][0] = Piece("white", "pawn")
        self.game.board.pole[6][2] = Piece("white", "pawn")
        self.game.board.pole[5][7] = Piece("white", "pawn")
        self.game.board.pole[5][3] = Piece("white", "pawn")
        
        # Nastavíme, že je na tahu černý
        self.game.current = 1
        self.game.current_player = "black"
        
        # Kontrola, zda hra správně identifikuje, že nejsou dostupné žádné tahy
        self.assertTrue(self.game.board.no_moves_available("black"))
        
        # Kontrola, že hra správně identifikuje vítěze
        game_status = self.game.board.check_game_status()
        self.assertEqual(game_status["status"], "game_over")
        self.assertEqual(game_status["winner"], "white")
        self.assertEqual(game_status["reason"], "blocked")

class PieceTests(unittest.TestCase):
    """Testy pro třídu Piece"""
    
    def test_pawn_movement(self):
        """Test pohybu pěšce"""
        # Bílý pěšec
        white_pawn = Piece("white", "pawn")
        
        # Pohyby bílého pěšce (měl by se pohybovat dopředu a do stran)
        expected_moves = [(1, 1), (1, -1)]  # Dopředu vlevo, dopředu vpravo
        self.assertEqual(white_pawn.krok(), expected_moves)
        
        # Černý pěšec
        black_pawn = Piece("black", "pawn")
        
        # Pohyby černého pěšce (měl by se pohybovat dozadu a do stran)
        expected_moves = [(-1, 1), (-1, -1)]  # Dozadu vlevo, dozadu vpravo
        self.assertEqual(black_pawn.krok(), expected_moves)
    
    def test_queen_movement(self):
        """Test pohybu dámy"""
        # Bílá dáma
        white_queen = Piece("white", "queen")
        
        # Dáma by se měla pohybovat všemi diagonálními směry
        expected_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        self.assertEqual(white_queen.krok(), expected_moves)
        
        # Černá dáma (stejné pohyby jako bílá)
        black_queen = Piece("black", "queen")
        self.assertEqual(black_queen.krok(), expected_moves)
    
    def test_skok_directions(self):
        """Test směrů skoku"""
        # Bílý pěšec
        white_pawn = Piece("white", "pawn")
        
        # Skoky bílého pěšce
        expected_jumps = [(2, 2), (2, -2)]  # Dopředu vlevo, dopředu vpravo
        self.assertEqual(white_pawn.skok(), expected_jumps)
        
        # Dáma
        queen = Piece("white", "queen")
        
        # Skoky dámy ve všech směrech
        expected_jumps = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        self.assertEqual(queen.skok(), expected_jumps)
        
if __name__ == "__main__":
    unittest.main()