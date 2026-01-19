import numpy as np

# Dimensione della scacchiera
dimensione = 8

# Creazione delle coordinate delle celle scure (somma dispari di riga e colonna)
celle_scure = [(colonna, riga) for riga in range(dimensione) for colonna in range(dimensione) if (riga + colonna) % 2 != 0]
celle_scure = np.array(celle_scure)  # Converti in array NumPy

# Funzione per calcolare gli ID delle celle adiacenti sulle diagonali
def calcola_diagonali(id_cella, coordinate, dimensione):
    x, y = coordinate[id_cella]
    diagonali = []
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < dimensione and 0 <= ny < dimensione:
            try:
                id_adiacente = np.where((celle_scure == [nx, ny]).all(axis=1))[0][0]
                diagonali.append(id_adiacente)
            except IndexError:
                pass
    return diagonali

# Creazione di un array per salvare gli ID delle diagonali
diagonali_array = np.empty(len(celle_scure), dtype=object)

# Riempimento degli ID delle diagonali
for i in range(len(celle_scure)):
    diagonali_array[i] = calcola_diagonali(i, celle_scure, dimensione)

# Stampa del risultato
for i, cella in enumerate(celle_scure):
    print(f"Cella ID {i}: Diagonali {diagonali_array[i]}, Coordinate {tuple(cella)}")
