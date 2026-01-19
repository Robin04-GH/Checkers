# Creazione di un vettore per rappresentare le celle scure
celle_scure = []

# Dimensione della scacchiera (8x8 tipica per la dama)
dimensione = 8

# Creazione del vettore
for riga in range(dimensione):
    for colonna in range(dimensione):
        # Una cella scura è tale se la somma di riga e colonna è dispari
        if (riga + colonna) % 2 != 0:
            id_corrente = len(celle_scure)  # ID implicito nell'indice
            x, y = colonna, riga  # Coordinate della cella

            # Calcolo degli ID delle celle adiacenti sulle diagonali
            diagonali = []
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < dimensione and 0 <= ny < dimensione:
                    id_adiacente = (ny * (dimensione // 2)) + (nx // 2)
                    diagonali.append(id_adiacente)

            # Salvataggio della cella come tupla
            celle_scure.append((diagonali, (x, y)))

# Stampa del risultato
for idx, cella in enumerate(celle_scure):
    print(f"Cella ID {idx}: Diagonali {cella[0]}, Coordinate {cella[1]}")
