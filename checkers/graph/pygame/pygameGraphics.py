import pygame
from checkers.graph.graphics_interface import GraphicsInterface

class PygameGraphics(GraphicsInterface):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Checkers")

        self.clock = pygame.time.Clock()
        self.running = True

    def process_events(self):
        """
        Handles input events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Mouse and Keyboard Management
            # ...

    def refresh_screen(self):
        """
        Renders frames
        """
        pygame.display.flip()
        # Limit frame rate to 60 FPS
        self.clock.tick(60)

    def main_loop(self, update_logic):
        """
        Main graphic loop.
        Calls a logical update function provided by the derived class.
        """
        while self.running:
            self.process_events()
            update_logic()
            self.refresh_screen()   

    def message_new_game(self) -> bool:
        """
        Modal message new game.
        """
        pass
