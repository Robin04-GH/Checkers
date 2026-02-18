import pygame

pygame.init()

CELL = 80
BOARD_SIZE = 8
WIDTH = HEIGHT = CELL * BOARD_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- LAYER ---
board_layer = pygame.Surface((WIDTH, HEIGHT))
pieces_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
highlight_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
drag_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# --- DISEGNO SCACCHIERA (STATICO) ---
def draw_board():
    colors = [(240, 217, 181), (181, 136, 99)]
    for y in range(BOARD_SIZE):
        for x in range (BOARD_SIZE):
            rect = (x*CELL, y*CELL, CELL, CELL)
            pygame.draw.rect(board_layer, colors[(x+y)%2], rect)

draw_board()

# --- PEDINE DI ESEMPIO ---
pieces = {(2,5): "red", (5,2): "white"}

def draw_pieces():
    pieces_layer.fill((0, 0, 0, 0))
    for (x, y), color in pieces.items():
        cx = x*CELL + CELL//2
        cy = y*CELL + CELL//2
        pygame.draw.circle(pieces_layer,
                           (200, 0, 0) if color == "red" else (230, 230, 230),
                           (cx, cy), CELL//2 - 10)

draw_pieces()

# ---HIGHLIGHT CELLE ---
def highlight_moves(moves):
    highlight_layer.fill((0, 0, 0, 0))
    for (x, y) in moves:
        rect = (x*CELL, y*CELL, CELL, CELL)
        pygame.draw.rect(highlight_layer, (0, 255, 0, 120), rect)

# --- DRAG & DROP ---
dragging = False
drag_piece = None
drag_pos = (0,0)

def draw_drag_piece():
    drag_layer.fill((0, 0, 0, 0))
    if dragging and drag_piece:
        pygame.draw.circle(drag_layer,
                           (200, 0, 0) if drag_piece == "red" else (230, 230, 230),
                           drag_pos, CELL//2 - 10)
        
# --- LOOP ---
running = True
dirty_rects = []

while running:
    dirty_rects.clear()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- CLICK SU PEDINA ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            gx, gy = mx // CELL, my // CELL
            if (gx, gy) in pieces:
                dragging = True
                drag_piece = pieces[(gx, gy)]
                del pieces[(gx, gy)]
                draw_pieces()
                drag_pos = event.pos #((gx*CELL) + CELL//2, (gy*CELL) + CELL//2)
                draw_drag_piece()
                dirty_rects.append(pygame.Rect(gx*CELL, gy*CELL, CELL, CELL))

                # highlight mosse possibili (esempio finto)
                highlight_moves([(gx+1, gy-1), (gx-1, gy-1)])
                dirty_rects.append(highlight_layer.get_rect())
        
        # --- MOUSE MOVE DURANTE DRAG ---
        if event.type == pygame.MOUSEMOTION and dragging:
            drag_pos = event.pos
            draw_drag_piece()
            dirty_rects.append(drag_layer.get_rect())

        # --- RILASCIO PEDINA ---
        if event.type == pygame.MOUSEBUTTONUP and dragging:
            mx, my = event.pos
            gx, gy = mx // CELL, my // CELL
            pieces[(gx, gy)] = drag_piece            
            dragging = False
            drag_piece = None
            draw_pieces()
            draw_drag_piece()
            highlight_layer.fill((0, 0, 0, 0))

            # N.B.: non ottimizzati i rettangoli highlight_layer e drag_layer
            # difatto equivale ad un pygame.display.flip() !
            dirty_rects.append(pygame.Rect(gx*CELL, gy*CELL, CELL, CELL))
            dirty_rects.append(highlight_layer.get_rect())
            dirty_rects.append(drag_layer.get_rect())
    
    # --- COMPOSIZIONE LAYER ---
    screen.blit(board_layer, (0, 0))
    screen.blit(pieces_layer, (0, 0))
    screen.blit(highlight_layer, (0, 0))
    screen.blit(drag_layer, (0, 0))

    # --- AGGIORNAMENTO PARZIALE ---
    if dirty_rects:
        pygame.display.update(dirty_rects)
    else:
        pygame.display.flip()

    clock.tick(60)

pygame.quit()
