
### Deuxième étape 

- Repartez de la version originale du code
- Mettre en place l'environnement MPI dans votre code
- Séparez l'affichage qui sera fait par le processus n°0 du calcul qui sera fait par les processus de numéro non nuls.
- Testez le code avec deux processus et  mesurez le temps global moyen pris par itération en temps.
- Interprétez votre résultat par rapport au temps global mesuré sur le code d'origine.

### Troisième étape 

- Reprenez la parallélisation OPENMP effectuée à la première étape et utilisez-là pour paralléliser l'avancement en temps du code obtenu à la deuxième étape
- Calculez en fonction du nombre de threads l'accélération globale et interprétez le résultat obtenu
- Calculez en fonction du nombre de threads l'accélération de l'avancement en temps et interprétez le résultat obtenu (en fonction également de l'accélération globale)
- BONUS : essayez de rendre asynchrone l'affichage et l'avancement en temps. Calculez l'accélération globale obtenue ainsi que son interprétation.

**NOTE** : Pour que la parallélisation OpenMP fonctionne, il est possible que vous devriez rajouter avec OpenMPI l'option *--bind-to none* à mpiexec (ou mpirun) lors du lancement de votre programme.

### Quatrième étape

On se propose de paralléliser l'avancement en temps à l'aide de MPI
à partir du code obtenu à l'étape 2.

- Définissez un groupe de communication pour les processus impliqués dans le calcul de la simulation
- Découpez la zone en tranche en fonction du nombre de processus impliqués dans le calcul
- Parallélisez le calcul à partir de ce découpage en tranche et en utilisant des cellules fantômes
- Calculez l'accélération globale ainsi que l'accélération de l'avancement en temps.
- Comparez les résultats obtenus avec les résultats obtenus dans le code écrit pour la troisième étape.
- En analysant vos résultats, suggérez des méthodes afin d'améliorer l'accélération obtenue avec MPI.

**REMARQUE** : Pour chaque accélération calculée, on donnera un tableau et une courbe dans le rapport final

**NOTE** : Si votre PC personnel possède que peu de coeurs de calcul (typiquement deux), il est conseillé de calculer les différentes accélérations sur les machines de l'ENSTA !

