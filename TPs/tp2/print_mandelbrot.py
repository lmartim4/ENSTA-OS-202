import matplotlib.pyplot as plt
import numpy as np

# Nombre de processus utilisés
n_proc = np.array([1, 2, 4, 6])

# Temps d'exécution correspondants en secondes
temps = np.array([2.965691089630127, 
                  1.6723082065582275, 
                  1.0292437076568604, 
                  0.8911781311035156])

# Calcul du speedup : temps avec 1 processus divisé par le temps avec N processus
speedup = temps[0] / temps

# Affichage du graphique
plt.figure(figsize=(8, 6))
plt.plot(n_proc, speedup, marker='o', linestyle='-', color='blue')
plt.title("Graphique d'accélération (Speedup) en fonction du nombre de processus", fontsize=14)
plt.xlabel("Nombre de processus", fontsize=12)
plt.ylabel("Speedup", fontsize=12)
plt.xticks(n_proc)
plt.grid(True)
plt.show()
