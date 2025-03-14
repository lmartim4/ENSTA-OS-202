## Travail à effectuer

Il est très conseillé de suivre les différentes étapes que nous allons décrire ici afin d'amener le projet à son terme !

Il faudra également conserver le code pour chaque étape décrit ici et rendre en fin de projet les sources pour chaque étape.

### Première étape

- Regarder le nombre de coeurs physiques sur votre machine et la taille des différentes mémoires caches que vous donnerez dans votre rapport.
- Mesurer les temps moyen ris pour chaque pas de temps, puis pour l'affichage et l'avancement en temps
- Paralléliser l'avancement en temps à l'aide d'OPENMP :

  - Récupérez dans un tableau toutes les clefs contenues dans le dictionnaire et à l'aide d'un indice, parcourez ces clefs pour l'avancement en temps
  - Vérifiez que vous obtenez exactement toujours la même simulation
  - Parallélisez la nouvelle boucle avec OpenMP
- Assurez-vous que vous avez exactement la même simulation qu'en séquentiel !
- Mesurer l'accélération obtenue globalement et uniquement pour l'avancement en temps en fonction du nombre de threads utilisés. Donner les tableaux et les courbes d'accélération dans votre rapport ainsi que votre interprétation des résultats obtenus.
