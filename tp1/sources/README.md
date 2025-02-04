
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`

## lscpu

*lscpu donne des infos utiles sur le processeur : nb core, taille de cache :*

```

Architecture:             x86_64
  CPU op-mode(s):         32-bit, 64-bit
  Address sizes:          39 bits physical, 48 bits virtual
  Byte Order:             Little Endian
  CPU(s):                   8
  On-line CPU(s) list:    0-7
  Vendor ID:                GenuineIntel
  Model name:             11th Gen Intel(R) Core(TM) i7-1165G7 @ 2.80GHz
    CPU family:           6
    Model:                140
    Thread(s) per core:   2
    Core(s) per socket:   4
    Socket(s):            1
    Stepping:             1
    BogoMIPS:             5606.40


On peut voir qui mon ordinateurs a 8 CPUs disponibles avec les mémoires suivants:

Caches (sum of all):      
  L1d:                    192 KiB (4 instances)
  L1i:                    128 KiB (4 instances)
  L2:                     5 MiB (4 instances)
  L3:                     12 MiB (1 instance)


Ces données seront utilisés pour l'analyse des performances
```




## Produit matrice-matrice

### Effet de la taille de la matrice

  n            | MFlops
---------------|--------
1024 (origine) |294.658
1023           |480.016
1025           |609.252
2047           |131.68
2048           |118.702
2049           |130.93


*On note qu'il y a une grand différence entre l'exécution avec une matrix de taille égale à une puissances de 2.
Ce comportement peut être justifié avec la façon que la mémoire est gérer pour la CPU et pour la construction de la mémoire.
Quand on utilise une variable à la position i c'est commun d'utiliser la variable à la position i+1. Le CPU considère ce principe et enregistre des variables en sequence.
La mémoire est construit à partir des structures binaires donc elle aura une taille multiple de 2. Son addressage sera fait à partir du module de la taille de la mémoire.
Quand il y a une matrice d'une taille multiple de 2, le module se rendre toujours au même endroit et donc chaque fois qui le CPU veut enregistre une variable il faut recopier tous les données en prenant plus de temps.*


### Permutation des boucles

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc. Par exemple :*

`make TestProduct.exe && ./TestProduct.exe 1024`


  ordre           | time    | MFlops  | MFlops(n=2048)
------------------|---------|---------|----------------
i,j,k (origine)   | 3.55083 | 604.784 |252.582
j,i,k             | 5.233   | 410.373 |218.305
i,k,j             | 9.04561 | 237.406 |122.861
k,i,j             | 4.96214 | 432.774 |111.105
j,k,i             | 0.59416 | 3614.33 |2615.17
k,j,i             | 0.93504 | 2296.69 |1441.64


*L’ordre des boucles influence fortement la performance, l’ordre j, k, i est le plus performant, tandis que i, k, j est le plus lent.
L’ordre i, j, k, souvent utilisé par défaut, est loin d’être optimal.
Ces différences sont liées à la localité des données en mémoire cache.
Un bon ordre de boucle maximise les accès séquentiels à la mémoire et minimise les mauvais accès (cache miss).
L’ordre j, k, i exploite mieux la structure des matrices en favorisant un parcours cohérent en mémoire.*



### OMP sur la meilleure boucle

`make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

  OMP_NUM         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
1                 |3414.21  |2888.13         |4051.49         |2858.39
2                 |6395.85  |4100.39         |6970.01         |3982.33
3                 |8909.17  |4995.36         |9214.97         |4372.9
4                 |11489    |6263.53         |10591.6         |4484.03
5                 |11419.8  |7042.35         |10316.7         |4552.59
6                 |13290.7  |7287.84         |9915.43         |4496
7                 |12689.2  |7008.14         |12599           |4399.54
8                 |11452.5  |6016.81         |12690.6         |4548.64

*Tracer les courbes de speedup (pour chaque valeur de n), discuter les résultats.*

Le speedup est visible jusqu’à environ 4 à 6 threads, mais au-delà, les performances plafonnent ou diminuent légèrement.
L’augmentation du nombre de threads améliore les performances mais pas de manière linéaire.
Le coût de synchronisation et la gestion des threads deviennent un facteur limitant à partir d’un certain nombre de threads.
La saturation mémoire se produit lorsque plusieurs threads accèdent en parallèle aux mêmes régions de mémoire, ce qui crée un goulot d’étranglement.
La meilleure performance est observée pour 6 threads dans plusieurs cas, ce qui indique que l’architecture de la machine teste peut supporter efficacement cette charge sans engorgement.



### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
32                |8497.15  |2939.45         |7117.87         |944.124
64                |9152.75  |2650.65         |8426.15         |1260.41
128               |12104.5  |5540.8          |7651.93         |2094.93
256               |9966.23  |6592.67         |4732.42         |3599.2
512               |6442.15  |6851.58         |3845.15         |5485.15
1024              |3625.73  |4473.88         |-------         |5565.76

*La méthode par blocs améliore significativement les performances.
Une taille de bloc intermédiaire (128-256) semble être le meilleur compromis.
Le produit matriciel est limité par les accès mémoire. Une taille de bloc appropriée améliore l’utilisation du cache.
Si le bloc est trop petit, il y a trop d’appels mémoire et peu de calculs par bloc.
Si le bloc est trop grand, il ne tient plus dans le cache et la performance diminue.*



### Bloc + OMP


  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|----------------|----------------|---------------|
1024           |  1      |3540.87  |2704.05         |----------------|2711.82        |
1024           |  8      |3654.31  |4500.34         |----------------|5974.31        |
512            |  1      |3759.94  |2771.79         |3817.06         |2478.31        |
512            |  8      |6716.77  |8690.29         |3937.14         |6297.5         |

*BLAS et Eigen sont beaucoup plus rapides que notre implémentation maison, même en OpenMP.
Les bibliothèques optimisées dépassent de loin les performances obtenues avec les boucles manuelles.
Ces bibliothèques utilisent des optimisations avancées, comme :
SIMD (Single Instruction, Multiple Data)
Cache blocking optimal
Optimisation spécifique au processeur
L’implémentation manuelle, bien qu’efficace, ne peut pas rivaliser avec des années d’optimisation effectuées par des experts en calcul scientifique.*


### Comparaison avec BLAS, Eigen et numpy


MFlops=48544.4 pour OMP_NUM_THREADS=1
MFlops=35914.3 pour OMP_NUM_THREADS=8


*L’ordre des boucles et la gestion de la mémoire cache ont un impact considérable sur les performances.
Le parallélisme OpenMP améliore les résultats, mais il est limité par les conflits mémoire et la synchronisation des threads.
Le produit par blocs améliore considérablement les performances, mais il faut ajuster la taille du bloc.
Les bibliothèques optimisées comme BLAS et Eigen surpassent largement l’implémentation naïve.*

# Tips

```
	env
	OMP_NUM_THREADS=1 ./test_product_matrice_blas.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```
