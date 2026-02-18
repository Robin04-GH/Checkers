import pygame

class Colors:
    # Pygame colors
    CELL_LIGHT = pygame.Color(255, 239, 166)          # + giallo ambrato o caramello
    CELL_DARK = pygame.Color(64, 60, 46)              # + marrone scuro (tonalità verde-oliva)
#   CELL_SELECTION = pygame.Color(229, 215, 166)      # + verde veronese
    CELL_SELECTION = pygame.Color(125, 255, 125)      # + verde chiaro
    CELL_SELECTED = pygame.Color(191, 179, 139)       # + sabbia
    CELL_MOVEMENT_FW = pygame.Color(229, 215, 166)    # + verde veronese
#   CELL_MOVEMENT_RV = pygame.Color(229, 215, 166)    # + verde veronese
    CELL_MOVEMENT_RV = pygame.Color(205, 133,  63)    # + perù
    PIECE_LIGHT = pygame.Color(255, 239, 166)         # + giallo ambrato o caramello
    PIECE_DARK = pygame.Color(127, 119, 92)           # + grigio ostrica (sfumature verdognole)       
    PIECE_BORDER_SELECTED = pygame.Color(255, 0 ,0 )  #   red border
    PIECE_BORDER_LIGHT = pygame.Color(0, 0, 0)        #   black
    PIECE_BORDER_DARK = pygame.Color(255, 255, 255)   #   white
    FILL_TRANSPARENT = pygame.Color(0, 0, 0, 0)       #   clear (transparent)

# 245, 245, 220     Beige
#  71,  10,   0     Marrone scuro
# 139,  69,  19     Marrone medio
# 205, 133,  63     Perù 
# 150,  75,   0     Marrone chiaro
# 152, 118,  84     Marrone pastello

# Abbinamenti 5 colori 
#  85,  60,  78
# 165, 189, 156
# 236, 189, 117
# 138, 84,   79
# 177, 155,  83

# 130, 109,  79
# 181, 186,  99
# 252, 249, 209
# 148, 150, 121
# 234, 174,  71

# 127, 119,  92     pedina scura
# 191, 179, 139     select scura
# 255, 239, 185     cella chiara, pedina chiara
# 229, 215, 166     select chiara
#  64,  60,  46     cella  scura
