# TD1

## lscpu

### Aperçu du CPU

- **Modèle de processeur :** AMD Ryzen 5 3600X 6-Core Processor  
- **Architecture :** x86_64 (Prend en charge les applications 32 bits et 64 bits)  
- **Nombre total de processeurs logiques (threads) :** 12  
- **Cœurs physiques :** 6  
- **Threads par cœur :** 2  
- **Socket(s) :** 1

### Fréquence et Performance

- **Fréquence de base :** 2200 MHz  
- **Fréquence maximale en mode boost :** ~4408,6 MHz  
- **BogoMIPS :** 7600,34 (Mesure approximative de la performance du CPU)

### Adressage Mémoire & Endianness

- **Taille de l'adresse physique :** 43 bits  
- **Taille de l'adresse virtuelle :** 48 bits  
- **Endianness :** Little Endian

### Architecture du Cache

- **Cache L1 :**  
  - Total : 192 KiB  
  - Détails : Composé de caches L1d (données) et L1i (instructions) distincts par cœur (6 instances chacun)
  
- **Cache L2 :**  
  - Total : 3 MiB (environ 512 KiB par cœur, 6 instances)
  
- **Cache L3 :**  
  - Total : 32 MiB  
  - Partagé entre les cœurs (divisé en 2 instances)

### Virtualisation & NUMA

- **Support de virtualisation :** AMD-V (virtualisation au niveau matériel)  
- **Configuration NUMA :**  
  - Un seul nœud NUMA (le nœud NUMA 0 englobe tous les cœurs)

### Fonctionnalités Utiles pour la Programmation Parallèle

- **Multithreading simultané (SMT) :** Activé, permettant 2 threads par cœur pour une meilleure gestion des tâches parallèles.
- **Extensions du jeu d'instructions :**  
  - Comprend SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, AVX, AVX2, etc., qui sont essentielles pour optimiser les performances dans les tâches parallèles intensives en calcul.
- **Mise à l'échelle dynamique de la fréquence :**  
  - La technologie Turbo Boost permet au CPU d'augmenter dynamiquement sa fréquence en fonction de la charge de travail.

### Sécurité & Stabilité

- **Mitigations des vulnérabilités :**  
  - Des protections contre les vulnérabilités courantes liées à l'exécution spéculative (par exemple, Spectre v1, Spectre v2) sont en place, garantissant un environnement sécurisé pour l'exécution de code parallèle.

# Reponses 
👉 **Toutes les réponses détaillées sont disponibles dans le [PDF Sujet](https://github.com/lmartim4/ENSTA-OS-202/blob/main/tp1/Sujet.pdf)**
