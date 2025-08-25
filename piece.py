class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.type = piece_type

    def __repr__(self):
        return f"{self.color} {self.type}"

    def krok(self):
        if self.type == "pawn":
            if self.color == "white":
                return [(1, 1), (1, -1)]
            else:
                return [(-1, 1), (-1, -1)]
        elif self.type == "queen":
            return [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def skok(self):
        if self.type == "pawn":
            if self.color == "white":
                return [(2, 2), (2, -2)]
            else:
                return [(-2, 2), (-2, -2)]
        elif self.type == "queen":
            return [(2, 2), (2, -2), (-2, 2), (-2, -2)]


from sys import exit

 