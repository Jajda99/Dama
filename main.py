from player import HumanPlayer, AIPlayer
from visual import start_menu, VisualRenderer
from game import Game


def main():
    mode = start_menu()
    if mode == 1:
        p1 = HumanPlayer("white")
        p2 = HumanPlayer("black")
    elif mode == 2:
        p1 = HumanPlayer("white")
        p2 = AIPlayer("black")
    elif mode == 3:
        p1 = AIPlayer("white")
        p2 = AIPlayer("black")
    else:
        print("Neplatná volba nebo ukončeno.")
        return
    
    game = Game(p1, p2)
    renderer = VisualRenderer()
    game.run_game(renderer)


if __name__ == "__main__":
    main()

