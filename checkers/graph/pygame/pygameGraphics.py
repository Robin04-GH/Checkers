import pygame
from checkers.graph.graphicsInterface import GraphicsInterface

class PygameGraphics(GraphicsInterface):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Checkers")

    def draw_board(self, board_state):
        # Disegna la scacchiera in base a board_state
        self.screen.fill((255, 255, 255))  # Sfondo bianco
        # Logica per disegnare caselle e pezzi
        pass