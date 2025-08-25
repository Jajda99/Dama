import pygame
import math
from player import AIPlayer, HumanPlayer, Player
from game import Game

class VisualRenderer:
    def __init__(self):
        """Inicializace vizuálního rendereru"""
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Dáma")
        self.FONT = pygame.font.SysFont("consolas", 18)
        self.CENTER = (self.WIDTH // 2, self.HEIGHT // 2-45)
        
        # Parametry pro vykreslování desky
        self.tile_count = 8
        self.min_radius = 60
        self.max_radius = 340
        self.radius_step = (self.max_radius - self.min_radius) // self.tile_count
        self.angle_step = 360 // self.tile_count
        
    def draw_game_state(self, game):
        """Vykreslí kompletní stav hry (desku, zprávy)"""
        self.screen.fill(pygame.Color("black"))
        self.draw_circular_board(game)
        self.draw_messages(game)
        pygame.display.flip()
    
    def draw_messages(self, game):
        """Vykreslí oblast zpráv a informace o aktuálním hráči"""
        pygame.draw.rect(self.screen, pygame.Color("lightgrey"), 
                        (0, self.HEIGHT-80, self.WIDTH, 80))
        
        for i, msg in enumerate(game.messages):
            text = self.FONT.render(msg, True, pygame.Color("black"))
            self.screen.blit(text, (10, self.HEIGHT-80 + i * 20))
        
        turn_info = self.FONT.render(f"Na tahu: {game.current_player_obj().color}", 
                                    True, pygame.Color("blue"))
        self.screen.blit(turn_info, (self.WIDTH - 220, self.HEIGHT - 75))
    
    def draw_circular_board(self, game):
        """Vykreslí kruhovou desku se všemi figurkami"""
        colors = [pygame.Color("burlywood"), pygame.Color("saddlebrown")]
      
        for r in range(self.tile_count):
            inner = self.min_radius + r * self.radius_step
            outer = inner + self.radius_step
            
            for c in range(self.tile_count):
                start_angle = c * self.angle_step
                points = []
                
                # Vykreslí body vnějšího okraje
                for i in range(6):
                    angle = math.radians(start_angle + i * (self.angle_step / 5))
                    x = self.CENTER[0] + outer * math.cos(angle)
                    y = self.CENTER[1] + outer * math.sin(angle)
                    points.append((x, y))
                
                # Vykreslí body vnitřního okraje (v opačném pořadí)
                for i in range(5, -1, -1):
                    angle = math.radians(start_angle + i * (self.angle_step / 5))
                    x = self.CENTER[0] + inner * math.cos(angle)
                    y = self.CENTER[1] + inner * math.sin(angle)
                    points.append((x, y))

                # Vykreslí dlaždici
                pygame.draw.polygon(self.screen, colors[(r + c) % 2], points)
                
                # Vykreslí figurku, pokud je přítomna
                piece = game.board.pole[r][c]
                if piece != 0:
                    angle_mid = math.radians(start_angle + self.angle_step / 2)
                    radius_mid = (inner + outer) // 2
                    fx = self.CENTER[0] + radius_mid * math.cos(angle_mid)
                    fy = self.CENTER[1] + radius_mid * math.sin(angle_mid)
                    
                    # Vykreslí figurku
                    piece_color = pygame.Color("white") if piece.color == "white" else pygame.Color("black")
                    pygame.draw.circle(self.screen, piece_color, (int(fx), int(fy)), self.radius_step // 2 - 4)
                    
                    # Označí dámy
                    if piece.type == "queen":
                        pygame.draw.circle(self.screen, pygame.Color("gold"), (int(fx), int(fy)), 8)
                    
                    # Zvýrazní vybranou figurku
                    player = game.current_player_obj()
                    if not Player.is_ai_player(player) and hasattr(player, "_selected") and player._selected == (r, c):
                        pygame.draw.circle(self.screen, pygame.Color("red"), 
                                         (int(fx), int(fy)), self.radius_step // 2, 3)
    
    def get_tile_from_click(self, pos):
        """Převede souřadnice obrazovky na souřadnice desky"""
        dx = pos[0] - self.CENTER[0]
        dy = pos[1] - self.CENTER[1]
        distance = math.hypot(dx, dy)
        angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360
        
        r = int((distance - self.min_radius) // self.radius_step)
        c = int(angle // self.angle_step)
        
        if 0 <= r < self.tile_count and 0 <= c < self.tile_count:
            return r, c
        return None
    
    def display_end(self, winner):
        """Zobrazí obrazovku konce hry"""
        # Vytvoří poloprůhledný překryv
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Poloprůhledná černá
        
        # Připraví text
        font_large = pygame.font.SysFont("Arial", 72, bold=True)
        font_small = pygame.font.SysFont("Arial", 24)
        
        if winner == "white":
            message = "BÍLÝ HRÁČ VYHRÁL!"
        else:
            message = "ČERNÝ HRÁČ VYHRÁL!"
        
        color = (255, 255, 255)  # Bílá
        
        # Vykreslí text
        text_win = font_large.render(message, True, color)
        text_exit = font_small.render("Stiskněte libovolnou klávesu pro ukončení", True, (200, 200, 200))
        
        # Umístí text
        text_win_rect = text_win.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 50))
        text_exit_rect = text_exit.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
        
        # Vykreslí všechno
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text_win, text_win_rect)
        self.screen.blit(text_exit, text_exit_rect)
        
        # Aktualizuje obrazovku
        pygame.display.flip()
        
        # Čeká na uživatele pro ukončení
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

# Zachování funkce menu
def start_menu():
    """Zobrazí úvodní menu pro výběr herního režimu"""
    pygame.init()
    WIDTH, HEIGHT = 500, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Výběr herního režimu")
    font = pygame.font.SysFont("consolas", 32)
    small_font = pygame.font.SysFont("consolas", 20)

    buttons = [
        {"rect": pygame.Rect(100, 80, 300, 60), "text": "1 - Hráč vs Hráč", "mode": 1},
        {"rect": pygame.Rect(100, 160, 300, 60), "text": "2 - Hráč vs Počítač", "mode": 2},
        {"rect": pygame.Rect(100, 240, 300, 60), "text": "3 - Počítač vs Počítač", "mode": 3},
    ]

    running = True
    selected_mode = None

    while running:
        screen.fill((220, 210, 180))
        title = font.render("Zvol herní režim:", True, (60, 30, 10))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

        for btn in buttons:
            pygame.draw.rect(screen, (180, 140, 90), btn["rect"], border_radius=12)
            text = small_font.render(btn["text"], True, (0, 0, 0))
            screen.blit(text, (btn["rect"].x + 20, btn["rect"].y + 15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                selected_mode = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn["rect"].collidepoint(event.pos):
                        selected_mode = btn["mode"]
                        running = False

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()
    return selected_mode

