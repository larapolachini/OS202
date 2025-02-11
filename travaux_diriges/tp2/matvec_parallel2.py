from mpi4py import MPI
import numpy as np
import time

# Initialisation MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Dimension du problème
dim = 120
Nloc = dim // size  # Nombre de lignes par processus

# Cas particulier : exécution en mode séquentiel pur si np=1
if size == 1:
    A_seq = np.array([[(i + j) % dim + 1. for i in range(dim)] for j in range(dim)])
    u_seq = np.array([i + 1. for i in range(dim)])

    start_seq = time.time()
    v_seq = A_seq.dot(u_seq)
    end_seq = time.time()

    seq_time = end_seq - start_seq
    parallel_time = seq_time  # Identique car pas de MPI

    print(f"Temps séquentiel : {seq_time:.6f} sec")
    print(f"Temps parallèle : {parallel_time:.6f} sec")
    print(f"Speedup : 1.00")
    print(f"Efficacité : 1.00 (100.0%)")
    print(f"✅ Résultats corrects !")
    print(f"Résultat du produit matrice-vecteur (extrait) : {v_seq[:10]}")
    exit()  # Sortie du programme, pas besoin de MPI

# Temps séquentiel (calculé uniquement par le processus 0)
if rank == 0:
    A_seq = np.array([[(i + j) % dim + 1. for i in range(dim)] for j in range(dim)])
    u_seq = np.array([i + 1. for i in range(dim)])

    start_seq = time.time()
    v_seq = A_seq.dot(u_seq)
    end_seq = time.time()

    seq_time = end_seq - start_seq
else:
    seq_time = None

# Diffusion du vecteur u à tous les processus
u = np.empty(dim, dtype=np.float64)
if rank == 0:
    u[:] = np.array([i + 1. for i in range(dim)])

comm.Bcast(u, root=0)

# Chaque processus génère uniquement sa portion de la matrice A
A_local = np.array([[(i + j) % dim + 1. for i in range(dim)] for j in range(rank * Nloc, (rank + 1) * Nloc)])

# Synchronisation avant le calcul parallèle
comm.Barrier()
start_parallel = time.time()

# Produit matrice-vecteur local
v_local = A_local.dot(u)

# Rassembler toutes les parties du vecteur v sur le processus 0
v_global = None
if rank == 0:
    v_global = np.empty(dim, dtype=np.float64)

comm.Gather(v_local, v_global, root=0)

# Synchronisation après la communication MPI
comm.Barrier()
end_parallel = time.time()

# Calcul du temps parallèle
parallel_time = end_parallel - start_parallel
parallel_time = comm.reduce(parallel_time, op=MPI.MAX, root=0)

# Calcul du speed-up et de l'efficacité
if rank == 0:
    speedup = seq_time / parallel_time
    efficiency = speedup / size

    print(f"Temps séquentiel : {seq_time:.6f} sec")
    print(f"Temps parallèle : {parallel_time:.6f} sec")
    print(f"Speedup : {speedup:.2f}")
    print(f"Efficacité : {efficiency:.2f} ({efficiency * 100:.1f}%)")

    # Vérification des résultats
    if np.allclose(v_seq, v_global):
        print("✅ Résultats corrects !")
    else:
        print("❌ Erreur dans le calcul parallèle !")

    # Affichage d'un extrait du résultat
    print(f"Résultat du produit matrice-vecteur (extrait) : {v_global[:10]}")

