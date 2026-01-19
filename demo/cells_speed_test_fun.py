import timeit
import numpy as np

# Approccio con liste
def approccio_lista():
    celle_scure = []
    dimensione = 8
    for riga in range(dimensione):
        for colonna in range(dimensione):
            if (riga + colonna) % 2 != 0:
                x, y = colonna, riga
                diagonali = []
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < dimensione and 0 <= ny < dimensione:
                        diagonali.append((nx, ny))
                celle_scure.append((diagonali, (x, y)))

# Approccio con NumPy
def approccio_numpy():
    dimensione = 8
    celle_scure = np.array([(colonna, riga) for riga in range(dimensione)
                            for colonna in range(dimensione) if (riga + colonna) % 2 != 0])
    def calcola_diagonali():
        diagonali_array = np.empty(len(celle_scure), dtype=object)
        for i, (x, y) in enumerate(celle_scure):
            diagonali = []
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < dimensione and 0 <= ny < dimensione:
                    try:
                        id_adiacente = np.where((celle_scure == [nx, ny]).all(axis=1))[0][0]
                        diagonali.append(id_adiacente)
                    except IndexError:
                        pass
            diagonali_array[i] = diagonali

    calcola_diagonali()

# Misurazione delle prestazioni
tempo_lista = timeit.timeit("approccio_lista()", globals=globals(), number=1000)
tempo_numpy = timeit.timeit("approccio_numpy()", globals=globals(), number=1000)

print(f"Tempo con liste: {tempo_lista:.5f} secondi")
print(f"Tempo con NumPy: {tempo_numpy:.5f} secondi")
