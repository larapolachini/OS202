import numpy as np
from mpi4py import MPI
from time import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

deb = time()

# Dimension du problème (peut-être changé)
dim = 120

Nloc = dim // size

# Initialisation de la matrice locale (chaque processus a Nloc lignes)
A_local = np.array([[(i + j) % dim + 1. for i in range(dim)] for j in range(rank * Nloc, (rank + 1) * Nloc)])

# Initialisation du vecteur u (identique pour tous les processus)
u = np.array([i + 1. for i in range(dim)])

# Produit matrice-vecteur local (chaque processus multiplie A_local avec le vecteur entier u)
v_local = A_local.dot(u)

# Initialisation du vecteur résultat global
v_global = np.zeros(dim)

# Collecte des résultats partiels de tous les processus
comm.Allgather(v_local, v_global)

# Affichage du résultat par le processus 0
if rank == 0:
    print(f"v = {v_global}")

fin = time()

print(f"La multiplication a pris {fin-deb} secondes")
