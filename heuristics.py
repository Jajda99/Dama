# heuristics.py
# Hodnoticí funkce pro AI hráče
# 1) Materiál, 2) Mobilita, 3) Povinné braní & hrozby, 4) Tlak na proměnu, 5) Centrum & formace

from typing import List, Tuple

# Nastavení vah
W_KING      = 2.8     # 1) dáma zhruba ~2.5–3× silnější než pěšec
W_MOB       = 0.08    # 2) mobilita (počet legálních tahů)
W_CAPTURE   = 1.0     # 3) mám-li capture a soupeř ne (a naopak)
W_THREAT    = 1.0     # 3) penalizace za můj kámen, který soupeř může hned sebrat (za kus)
W_PROMO     = 0.15    # 4) bonus za blízkost proměny (pěšci)
W_CENTER    = 0.05    # 5) bonus za kámen v centru- strategie v damách
W_FORMATION = 0.05    # 5) bonus za diagonální "sousednost" (základní souhra)

# Centrum (volba jednoduchá a praktická: vnitřní 4×4 tmavá pole)
CENTER_ROWS = range(2, 6) 
CENTER_COLS = range(2, 6)  


def evaluate_position(game, me_color: str):
    """
    Vrátí reálné skóre pozice z pohledu 'me_color'.
    Kladné = lepší pro mě, záporné = horší.
    Zohledňuje body 1-5 (viz výše).
    """

    #  MATERIÁL
    my_pawns, my_kings, op_pawns, op_kings = count_material(game, me_color)
    material = (my_pawns + W_KING * my_kings) - (op_pawns + W_KING * op_kings)

    #  MOBILITA
    my_moves = count_legal_moves(game, me_color)
    op_moves = count_legal_moves(game, opp(me_color))
    mobility = W_MOB * (my_moves - op_moves)

    # POVINNÉ BRANÍ & HROZBY
    # Povinné braní – mít capture je „dobře“ (tempo i změna materiálu)
    my_can_capture = 1 if game.moznostSkoku(me_color) else 0
    op_can_capture = 1 if game.moznostSkoku(opp(me_color)) else 0
    capture_pressure = W_CAPTURE * (my_can_capture - op_can_capture)

    # Kolik mých kamenů je přímo k sebrání jedním skokem soupeře?
    my_threatened = count_threatened_pieces(game, me_color)
    threats_penalty = - W_THREAT * my_threatened

    # TLAK NA PROMĚNU
    # Jednoduché: čím blíž poslední řadě, tím větší bonus (jen pěšci)
    promo = W_PROMO * (promotion_progress(game, me_color) -
                       promotion_progress(game, opp(me_color)))

    # CENTRUM & FORMAce
    center_score = W_CENTER * (count_in_center(game, me_color) -
                               count_in_center(game, opp(me_color)))
    formation_score = W_FORMATION * (formation_pairs(game, me_color) -
                                     formation_pairs(game, opp(me_color)))

    # Penalizace za opakování pozice (cyklení)
    repetition_penalty = 0
    if hasattr(game, 'state_history'):
        # Pokud se aktuální pozice vyskytla už 2x nebo víc, penalizuj
        current_hash = game._board_state_hash()
        repeats = game.state_history.count(current_hash)
        if repeats >= 2:
            repetition_penalty = -2.0 * repeats  # váhu můžeš upravit
    return material + mobility + capture_pressure + threats_penalty + promo + center_score + formation_score + repetition_penalty


#  Pomocné funkce

def opp(color: str) -> str:
    return "white" if color == "black" else "black"


def iterate_pieces(game, color: str) -> List[Tuple[int, int]]:
    whites, blacks = game.vsechny_figurky()
    return whites if color == "white" else blacks


def count_material(game, me_color: str):
    """Spočítá (my_pawns, my_kings, op_pawns, op_kings)."""
    def split(color: str):
        pawns = kings = 0
        for x, y in iterate_pieces(game, color):
            p = game.board.pole[x][y]
            if p.type == "queen":
                kings += 1
            else:
                pawns += 1
        return pawns, kings

    my_pawns, my_kings = split(me_color)
    op_pawns, op_kings = split(opp(me_color))
    return my_pawns, my_kings, op_pawns, op_kings


def count_legal_moves(game, color: str) -> int:
    """
    Vrátí počet legálních tahů pro danou barvu. Respektuje povinné braní:
    pokud existuje skok, vrátí jen počet skoků.
    (Bez simulace - jen lokální kontrola podle desky.)
    """
    board = game.board
    my_figs = iterate_pieces(game, color)

    jumps = 0
    steps = 0

    for x, y in my_figs:
        piece = board.pole[x][y]
        # Skoky
        for dx, dy in piece.skok():
            x2, y2 = x + dx, (y + dy) % 8
            if not board.je_v_poli(x2, y2) or not board.je_volne(x2, y2):
                continue
            mx, my = (x + x2) // 2, board.middle_col(y, y2)
            victim = board.pole[mx][my]
            if victim != 0 and victim.color != color:
                # pěšec skáče správným směrem (dáma oběma)
                if piece.type == "queen" or \
                   (color == "white" and dx > 0) or (color == "black" and dx < 0):
                    jumps += 1
        # Kroky
        for dx, dy in piece.krok():
            x2, y2 = x + dx, (y + dy) % 8
            if not board.je_v_poli(x2, y2) or not board.je_volne(x2, y2):
                continue
            # pěšec jen dopředu, dáma i zpět
            if piece.type == "queen" or \
               (color == "white" and dx == 1) or (color == "black" and dx == -1):
                steps += 1

    return jumps if jumps > 0 else steps


def count_threatened_pieces(game, my_color: str) -> int:
    """
    Spočítá, kolik mých kamenů může soupeř sebrat JEDNÍM skokem z aktuální pozice.
    (Hrubý, ale rychlý odhad taktického rizika.)
    """
    board = game.board
    opp_color = opp(my_color)
    opp_figs = iterate_pieces(game, opp_color)

    threatened_positions = set()

    for ox, oy in opp_figs:
        op = board.pole[ox][oy]
        for dx, dy in op.skok():
            tx, ty = ox + dx, (oy + dy) % 8
            if not board.je_v_poli(tx, ty) or not board.je_volne(tx, ty):
                continue
            mx, my = (ox + tx) // 2, board.middle_col(oy, ty)
            mid = board.pole[mx][my]
            if mid != 0 and mid.color == my_color:
                # pěšec soupeře musí skákat správným směrem
                if op.type == "queen" or \
                   (opp_color == "white" and dx > 0) or (opp_color == "black" and dx < 0):
                    threatened_positions.add((mx, my))

    return len(threatened_positions)


def promotion_progress(game, color: str) -> float:
    """
    Jednoduchý součet „pokroku“ pěšců k proměně (normalizovaný).
    Bílý: vyšší x = blíž k proměně; Černý: nižší x = blíž.
    (Bez úplné kontroly volné cesty – je to rychlá a stabilní aproximace.)
    """
    total = 0.0
    count = 0
    for x, y in iterate_pieces(game, color):
        p = game.board.pole[x][y]
        if p.type == "pawn":
            if color == "white":
                # 0..7 -> 0..1
                total += x / 7.0
            else:
                total += (7 - x) / 7.0
            count += 1
    return total if count == 0 else total  # suma (ne průměr), ať víc pěšců => víc tlaku


def count_in_center(game, color: str) -> int:
    """Počet kamenů v jednoduchém 'centru' (řádky/ sloupce 2..5)."""
    cnt = 0
    for x, y in iterate_pieces(game, color):
        if x in CENTER_ROWS and y in CENTER_COLS:
            cnt += 1
    return cnt


def formation_pairs(game, color: str) -> int:
    """
    Hrubé měřítko souhry: kolik mám diagonálně sousedících dvojic (±1,±1).
    (Válcový sloupec řešíme mod 8.)
    """
    board = game.board
    my_set = set(iterate_pieces(game, color))
    pairs = 0
    for x, y in my_set:
        for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, (y + dy) % 8
            if board.je_v_poli(nx, ny) and (nx, ny) in my_set:
                pairs += 1
    # Každý pár se započítá 2× (z obou konců)
    return pairs // 2
