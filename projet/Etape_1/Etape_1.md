# Rapport de Parallélisation - Étape 1 : OpenMP

## Résumé des modifications apportées

Dans cette première étape du projet de parallélisation de la simulation de feu de forêt, j'ai implémenté une version parallélisée de la fonction `Model::update()` en utilisant OpenMP. Voici les principales modifications apportées au code original :

### 1. Conception de la classe `Profiler`

J'ai créé une classe `Profiler` pour mesurer précisément les performances de la simulation, avec les fonctionnalités suivantes :
- Enregistrement des temps d'exécution pour différentes sections du code (mise à jour, affichage, etc.)
- Stockage des résultats dans un fichier CSV pour analyse ultérieure
- Identification des bottlenecks dans la simulation

### 2. Parallélisation de l'avancement du temps

Dans la fonction `Model::update()`, j'ai remplacé la boucle séquentielle par une approche parallèle en suivant ces étapes :
- Collecte des clés du dictionnaire `fire_front` dans un vecteur d'itérateurs
- Parallélisation du traitement avec `#pragma omp parallel`
- Utilisation de `#pragma omp for schedule(dynamic, 64)` pour répartir la charge de travail entre les threads
- Mise en place d'un système d'accumulation locale des mises à jour pour éviter les conflits d'accès

### 3. Structure des mises à jour locales

J'ai implémenté une approche où chaque thread :
- Maintient son propre vecteur de mises à jour locales
- Traite un sous-ensemble des cellules en feu
- Accumule les modifications à apporter aux cartes
- Fusionne ensuite les mises à jour de tous les threads de manière sécurisée

### 4. Parallélisation de la mise à jour de la végétation

J'ai également parallélisé la boucle de mise à jour de la végétation en utilisant une directive `#pragma omp parallel for` avec un ordonnancement dynamique.

## Instrumentation et mesure des performances

Pour analyser les performances de la version parallelisée, j'ai instrumenté le code de la façon suivante :

```cpp
int main(int nargs, char *args[])
{
    // [...] Initialisation
    
    Profiler profiler("Informations sur la simulation...");
    int num_threads = omp_get_max_threads();
    std::cout << "OpenMP threads: " << num_threads << std::endl;

    while (true)
    {
        profiler.start("total");
        
        profiler.start("update");
        bool updating = simu.update();
        profiler.stop("update");
        
        if (!updating) break;
        
        // [...] Gestion des événements
        
        profiler.start("display");
#ifdef active_display
        displayer->update(simu.vegetal_map(), simu.get_fire_map());
#endif
        profiler.stop("display");
        
        profiler.stop("total");
        
        // [...] Affichage périodique
        
        profiler.log(simu.get_time_step() - 1);
    }
    
    return EXIT_SUCCESS;
}
```

## Défis rencontrés et solutions

1. **Gestion des conflits d'accès** : Pour éviter les conflits d'écriture entre threads, j'ai implémenté un système où chaque thread accumule ses modifications localement avant de les fusionner dans une phase séquentielle.

2. **Équilibrage de charge** : L'utilisation d'un ordonnancement dynamique (`schedule(dynamic, 64)`) permet une meilleure répartition du travail entre les threads, chaque thread traitant un bloc de 64 éléments à la fois.

3. **Préservation du déterminisme** : Pour garantir que la simulation parallèle produise des résultats identiques à la version séquentielle, j'ai veillé à préserver l'ordre de traitement des cellules et utilisé des générateurs de nombres pseudo-aléatoires déterministes basés sur les indices et le pas de temps.

## Accès au code

Si vous souhaitez voir le code de la fonction `Model::update()` après la parallélisation de l'étape 1, il est disponible dans le fichier **`model_etape_1.cpp`** situé dans ce répertoire.
