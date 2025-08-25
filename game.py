from piece import Piece
from board import Board
import pygame

class Game:
    def __init__(self, player1, player2):
        self.board = Board()
        self.board.setup_pieces()  # Ujistěte se, že figurky jsou nastaveny
        self.players = [player1, player2]
        self.current = 0  
        self.current_player = self.players[self.current].color
        self.messages = []  # Uchovává zprávy pro zobrazení
        self.running = True
        
    def run_game(self, visual_renderer):
        pygame.init()
        
        clock = pygame.time.Clock()
        
        while self.running:
            # Zobrazí aktuální stav hry
            visual_renderer.draw_game_state(self)

            # Zpracuje události a vstupy
            self._process_events(visual_renderer)

            # Zpracuje tahy AI, pokud je aktuální hráč AI
            self._process_ai_turn(visual_renderer)

            self._check_game_end(visual_renderer)

            # Udržuje frekvenci snímků
            clock.tick(60)
        pygame.quit()
        return
    
    def _check_game_end(self, visual_renderer):
        game_status = self.board.check_game_status()
        if game_status["status"] == "game_over":
            visual_renderer.draw_game_state(self)
            pygame.time.wait(1000)
            visual_renderer.display_end(game_status["winner"])
            self.running = False
        return

    def _process_events(self, visual_renderer):
        """Zpracuje události pygame a uživatelské vstupy"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Zpracuje kliknutí pouze pro lidské hráče
                if not self.current_player_obj().is_ai_player():
                    self._handle_player_click(event.pos, visual_renderer)
    
    def _handle_player_click(self, pos, visual_renderer):
        """Zpracuje kliknutí myší pro lidského hráče"""
        tile = visual_renderer.get_tile_from_click(pos)
        player = self.current_player_obj()
        
        if tile:
            if player._selected is None:
                player._selected = tile
            else:
                x1, y1 = player._selected
                x2, y2 = tile
                player.dalsi_tah = (x1, y1, x2, y2)
                player._selected = None
        else:
            player._selected = None
    
    def _process_ai_turn(self, visual_renderer):
        """Zpracuje tah AI hráče"""
        player = self.current_player_obj()
        
    # Přeskočí, pokud není AI nebo pokud lidský hráč má čekající tah
        if not player.is_ai_player():
            move = player.get_move(self)
            if move:
                try:
                    self.play_turn(*move)
                except ValueError as e:
                    self.add_message(f"Chyba: {str(e)}")
            return
        
    # Zpracuje tah AI
        move = player.get_move(self)
        if move:
            x1, y1, x2, y2 = move
            
            # Ukáže zprávu o přemýšlení
            self.add_message(f"AI zvažuje tah {x1},{y1} -> {x2},{y2}")
            visual_renderer.draw_game_state(self)
            
            # Přidá zpoždění pro zobrazení AI "přemýšlení"
            pygame.time.wait(1500)
            
            try:
                self.play_turn(x1, y1, x2, y2)
                self.add_message(f"AI táhl {x1},{y1} -> {x2},{y2}")
            except ValueError as e:
                self.add_message(f"Chyba: {e}")
            
            # Aktualizuje zobrazení po tahu
            visual_renderer.draw_game_state(self)

    def add_message(self, msg):
        """Přidá zprávu do fronty pro zobrazení"""
        self.messages.append(msg)
        if len(self.messages) > 3:
            self.messages[:] = self.messages[-3:]

    def current_player_obj(self):
        return self.players[self.current]

    def current_color(self):
        return self.current_player
            
    def play_turn(self, x1, y1, x2, y2): 
            y1, y2 = y1 % 8, y2 % 8       
            figurka = self.board.pole[x1][y1]
            if figurka == 0:
                raise ValueError("Na výchozím poli není žádná figurka.")
            if figurka.color != self.current_player:
                raise ValueError("Nelze hrát s figurkou soupeře.")
                        
            dx = x2 - x1
            dy = (y2 - y1)% 8
            
            if abs(dx) == 2 and dy in [2, 6]:
                self.board.perform_jump(x1, y1, x2, y2)
            
            elif abs(dx) == 1 and dy in [1, 7]:
            # Zkontroluje, jestli nejsou možné jiné skoky
                if self.moznostSkoku(self.current_player):
                    raise ValueError("Musíte provést skok, pokud je možný.")
                if not self.board.je_volne(x2, y2):
                    raise ValueError("Cílové pole není volné.")
                if figurka.type == "pawn":
                    if (figurka.color == "white" and dx != 1) or (figurka.color == "black" and dx != -1):
                        raise ValueError("Pěšec nemůže jít zpět.")
                # Provedení tahu
                self.board.pole[x2][y2] = figurka
                self.board.pole[x1][y1] = 0

            else:
                raise ValueError("Neplatný tah.")

            # Proměna v dámu
            if figurka.type == "pawn":
                if (figurka.color == "white" and x2 == 7) or (figurka.color == "black" and x2 == 0):
                    self.board.pole[x2][y2] = Piece(figurka.color, "queen")

            # Změna hráče
            self.current = 1 - self.current
            self.current_player = self.players[self.current].color
            
    def moznostSkoku(self, color):
        figurky_bile, figurky_cerne = self.vsechny_figurky()
        figurky = figurky_bile if color == "white" else figurky_cerne

        for x, y in figurky:
            piece = self.board.pole[x][y]
            for dx, dy in piece.skok(): #pro každý skok
                x2, y2 = x + dx, (y + dy) % 8
                if not self.board.je_v_poli(x2, y2):
                    continue
                try:
                    # zkusí jestli by slo skakat
                    jumped_x = (x + x2) // 2
                    jumped_y = self.board.middle_col(y, y2)
                    preskocena = self.board.pole[jumped_x][jumped_y]
                    if self.board.je_volne(x2, y2) and preskocena != 0 and preskocena.color != color:
                        if piece.type == "pawn":
                            if (piece.color == "white" and dx < 0) or (piece.color == "black" and dx > 0):
                                continue
                        return True
                except IndexError:
                    continue
        return False        
            
    def vsechny_figurky(self):
        figurkyBile = []
        figurkyCerne = []
        for i in range(8):
            for j in range(8):
                piece = self.board.pole[i][j]
                if piece != 0:
                    if piece.color == "white":
                        figurkyBile.append((i, j))
                    elif piece.color == "black":
                        figurkyCerne.append((i, j))
        return figurkyBile, figurkyCerne         
        
        
    def display_board(self):
        for row in self.board.pole:
            print(" ".join(str(piece) if piece else "." for piece in row))
        print()        

    def switch_player(self):
        self.current = 1 - self.current
        self.current_player = self.players[self.current].color
    
    def play(self):
            while True:
                self.display_board()
                player = self.players[self.current]
                try:
                    move = player.get_move(self)
                    if move:
                        x1, y1, x2, y2 = move
                        self.play_turn(x1, y1, x2, y2)
                except Exception as e:
                    print("Chyba:", e)
                    continue