#import sys
#import os
# Aggiungi la directory principale del progetto al PYTHONPATH
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
import threading
import time
import queue  # Per la comunicazione tra thread

# Impostazioni
LARGHEZZA, ALTEZZA = 400, 400
N_COLONNE, N_RIGHE = 8, 8
DIM_CASELLA = LARGHEZZA // N_COLONNE

# Colori
NERO = (0, 0, 0)
BIANCO = (255, 255, 255)
ROSSO = (255, 0, 0)
BLU = (0, 0, 255)

# Inizializza Pygame
pygame.init()
schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Dama con IA")

# Creiamo la scacchiera solo una volta
scacchiera_surface = pygame.Surface((LARGHEZZA, ALTEZZA))
for r in range(N_RIGHE):
    for c in range(N_COLONNE):
        colore = NERO if (r + c) % 2 else BIANCO
        pygame.draw.rect(scacchiera_surface, colore, (c * DIM_CASELLA, r * DIM_CASELLA, DIM_CASELLA, DIM_CASELLA))

# Buffer per le pedine
pedine_surface = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
pedine = []

# Posizioniamo le pedine iniziali (rosse = giocatore, blu = IA)
for r in range(3):
    for c in range(N_COLONNE):
        if (r + c) % 2 == 1:
            centro = (c * DIM_CASELLA + DIM_CASELLA // 2, r * DIM_CASELLA + DIM_CASELLA // 2)
            pedine.append({"r": r, "c": c, "x": centro[0], "y": centro[1], "colore": ROSSO, "selected": False})
for r in range(5, 8):
    for c in range(N_COLONNE):
        if (r + c) % 2 == 1:
            centro = (c * DIM_CASELLA + DIM_CASELLA // 2, r * DIM_CASELLA + DIM_CASELLA // 2)
            pedine.append({"r": r, "c": c, "x": centro[0], "y": centro[1], "colore": BLU, "selected": False})

# Variabili per la selezione della pedina
pedina_selezionata = None
mossa_IA_completata = False  # Controlla se l'IA ha finito la mossa

# Coda per comunicare con il thread IA
queue_ia = queue.Queue()

def motore_IA():
    """Thread IA: attende richieste e calcola le mosse"""
    global mossa_IA_completata
    while True:
        mossa_richiesta = queue_ia.get()  # Aspetta una mossa
        if mossa_richiesta == "EXIT":
            break  # Permette di chiudere il thread in modo pulito

        print("L'IA sta calcolando la mossa...")
        time.sleep(2)  # Simula il tempo di calcolo
        for pedina in pedine:
            if pedina["colore"] == BLU:
                pedina["x"] += DIM_CASELLA  # Muove una casella a destra
                pedina["y"] -= DIM_CASELLA  # Muove in avanti
                break
        mossa_IA_completata = True

# Avvia il thread IA una sola volta
thread_ia = threading.Thread(target=motore_IA, daemon=True)
thread_ia.start()

# Loop principale
running = True
aggiorna_schermo = True  # Usato per primo disegno scacchiera
counter = 0

while running:
#    aggiorna_schermo = False  # Evita ridisegni inutili

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            queue_ia.put("EXIT")  # Chiude il thread IA in modo pulito
            running = False

        # Rileva il click del mouse
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            for pedina in pedine:
                if pedina["colore"] == ROSSO:  # Solo le pedine del giocatore sono selezionabili
                    dx = x - pedina["x"]
                    dy = y - pedina["y"]
                    if dx**2 + dy**2 <= (DIM_CASELLA // 2 - 5) ** 2:
                        pedina_selezionata = pedina
                        pedina["selected"] = True
                        aggiorna_schermo = True
                        break

        # Muove la pedina selezionata
        elif event.type == pygame.MOUSEMOTION and pedina_selezionata:
            pedina_selezionata["x"], pedina_selezionata["y"] = event.pos
            aggiorna_schermo = True

        # Rilascia la pedina
        elif event.type == pygame.MOUSEBUTTONUP and pedina_selezionata:
            pedina_selezionata["selected"] = False
            pedina_selezionata = None
            aggiorna_schermo = True

            # Dopo la mossa del giocatore, segnala l'IA di calcolare la contromossa
            queue_ia.put("MOVE")

    # Disegna solo se necessario
    if aggiorna_schermo or mossa_IA_completata:
        aggiorna_schermo = False
        schermo.blit(scacchiera_surface, (0, 0))  # Sfondo fisso
        pedine_surface.fill((0, 0, 0, 0))  # Pulisce la surface delle pedine

        counter += 1
        print(f'Refresh {counter}')

        for pedina in pedine:
            colore = (0, 255, 0) if pedina["selected"] else pedina["colore"]
            pygame.draw.circle(pedine_surface, colore, (pedina["x"], pedina["y"]), DIM_CASELLA // 2 - 5)

        schermo.blit(pedine_surface, (0, 0))
        pygame.display.flip()
        mossa_IA_completata = False  # Reset del flag

pygame.quit()
