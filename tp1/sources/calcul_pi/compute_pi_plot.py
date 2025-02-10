import matplotlib.pyplot as plt

# Données obtenues
processes = [1, 2, 4, 6]
times = [1.816711664199829, 1.0812108516693115, 0.7567012310028076, 0.6910133361816406]
pi_values = [3.14144016, 3.14153852, 3.14169612, 3.14175068]

# Création d'une figure avec deux sous-graphes (subplots)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Premier graphique : Temps d'exécution vs Nombre de processus
ax1.plot(processes, times, marker='o', linestyle='-', color='blue')
ax1.set_xlabel("Nombre de processus")
ax1.set_ylabel("Temps d'exécution (secondes)")
ax1.set_title("Temps d'exécution vs Nombre de processus")
ax1.grid(True)

# Deuxième graphique : Approximation de π vs Nombre de processus
ax2.plot(processes, pi_values, marker='s', linestyle='-', color='red')
ax2.set_xlabel("Nombre de processus")
ax2.set_ylabel("Valeur approximative de π")
ax2.set_title("Approximations de π vs Nombre de processus")
ax2.grid(True)

plt.tight_layout()
plt.show()
