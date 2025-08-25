from piece import Piece

class Board:
    def __init__(self): # matice s bud 0 nebo figurkou, říká kde jsou jaké figurky
        self.pole = [[0 for _ in range(8)] for _ in range(8)]
        self.setup_pieces()
        
    def setup_pieces(self):
        """Rozmístí počáteční figurky na desku"""
        for j in range(1):
            #self.pole[0][j * 2 + 1] = Piece("white", "pawn")
            self.pole[1][j * 2] = Piece("white", "pawn")
            self.pole[6][j * 2 + 1] = Piece("black", "pawn")
            self.pole[7][j * 2] = Piece("black", "pawn")

    def je_v_poli(self, x, y):
        """Kontroluje, zda jsou souřadnice v rámci desky"""
        return 0 <= x < 8  # na y je modulo 8

    def je_volne(self, x, y):
        """Kontroluje, zda je pole prázdné"""
        return self.pole[x][y % 8] == 0

    def wrap_col(self, y):
        """Aplikuje modulo na sloupec pro kruhovou desku"""
        return y % 8

    def middle_col(self, y1, y2):
        """Najde sloupec mezi dvěma sloupci (pro skoky)"""
        d = (y2 - y1) % 8
        if d == 2:   # +2 vpravo (po směru hodin)
            return (y1 + 1) % 8
        if d == 6:   # -2 vlevo (proti směru)
            return (y1 - 1) % 8
        raise ValueError("Neplatný posun sloupce: musí být +2 nebo -2.")
    
    def perform_jump(self, x1, y1, x2, y2):
        """Provede skok a vrátí stav hry"""
        y1, y2 = y1 % 8, y2 % 8

        if abs(x2 - x1) != 2 or ((y2 - y1) % 8 not in [2, 6]):
            raise ValueError("Neplatný skok: rozdíl souřadnic musí být přesně 2.")

        jumped_x = (x1 + x2) // 2
        jumped_y = self.middle_col(y1, y2)

        figurka = self.pole[x1][y1]
        preskocena = self.pole[jumped_x][jumped_y]
        
        if figurka.type == "pawn":
            if figurka.color == "black" and (x1-x2) < 0:
                raise ValueError("Černá figurka nemůže skákat zpět.")
            if figurka.color == "white" and (x1-x2) > 0:
                raise ValueError("Bílá figurka nemůže skákat zpět.")

        if figurka == 0:
            raise ValueError("Na výchozím poli není figurka.")
        if preskocena == 0:
            raise ValueError("Není koho přeskočit.")
        if figurka.color == preskocena.color:
            raise ValueError("Nelze přeskočit vlastní figurku.")
        if not self.je_volne(x2, y2):
            raise ValueError("Cílové pole není volné.")

        # Provede skok
        self.pole[x2][y2] = figurka
        self.pole[x1][y1] = 0
        self.pole[jumped_x][jumped_y] = 0  # maže přeskočenou figurku
        
        # Kontroluje stav hry
        game_status = self.check_game_status()
        return game_status
    
    def check_game_status(self):
        """Kontroluje stav hry a vrací výsledek"""
        bili, cerni = self.pocetfigurek()
        
        # Kontrola počtu figurek
        if cerni == 0:
            return {"status": "game_over", "winner": "white", "reason": "no_pieces"}
        elif bili == 0:
            return {"status": "game_over", "winner": "black", "reason": "no_pieces"}
        
        # Kontrola, zda bílý není zablokován
        if self.no_moves_available("white"):
            return {"status": "game_over", "winner": "black", "reason": "blocked"}
            
        # Kontrola, zda černý není zablokován
        if self.no_moves_available("black"):
            return {"status": "game_over", "winner": "white", "reason": "blocked"}
            
        # Hra pokračuje
        return {"status": "continue"}
        
    def pocetfigurek(self):
        """Spočítá počet figurek každé barvy na desce"""
        bili, cerni = 0, 0
        for i in range(8):
            for j in range(8):
                figurka = self.pole[i][j]
                if figurka != 0:
                    if figurka.color == "white":
                        bili += 1
                    elif figurka.color == "black":
                        cerni += 1
        return bili, cerni

    def no_moves_available(self, color):
        """Kontroluje, zda hráč s danou barvou má k dispozici platné tahy"""
        for i in range(8):
            for j in range(8):
                piece = self.pole[i][j]
                if piece != 0 and piece.color == color:
                    # Kontrola možných skoků
                    for dx, dy in piece.skok():
                        x2, y2 = i + dx, (j + dy) % 8
                        if self.je_v_poli(x2, y2) and self.je_volne(x2, y2):
                            mx = (i + x2) // 2
                            my = self.middle_col(j, y2)
                            victim = self.pole[mx][my]
                            if victim != 0 and victim.color != color:
                                # Nalezen platný skok
                                return False
                    
                    # Kontrola možných tahů (pokud nejsou skoky)
                    for dx, dy in piece.krok():
                        x2, y2 = i + dx, (j + dy) % 8
                        if self.je_v_poli(x2, y2) and self.je_volne(x2, y2):
                            if piece.type == "queen" or (
                                (color == "white" and dx > 0) or 
                                (color == "black" and dx < 0)
                            ):
                                # Nalezen platný tah
                                return False
        
        # Nenalezeny žádné platné tahy
        return True

    def moznostSkoku(self, color):
        """Kontroluje, zda má hráč k dispozici nějaké možné skoky"""
        for i in range(8):
            for j in range(8):
                piece = self.pole[i][j]
                if piece != 0 and piece.color == color:
                    for dx, dy in piece.skok():
                        x2, y2 = i + dx, (j + dy) % 8
                        if self.je_v_poli(x2, y2) and self.je_volne(x2, y2):
                            mx = (i + x2) // 2
                            my = self.middle_col(j, y2)
                            victim = self.pole[mx][my]
                            if victim != 0 and victim.color != color:
                                return True
        return False

