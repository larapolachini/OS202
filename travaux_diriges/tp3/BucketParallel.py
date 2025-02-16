from mpi4py import MPI
import numpy as np

def bucket_sort(arr):
    arr.sort()
    return arr

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


N = 10  

if rank == 0:
    # Step 1: Générer le tableau sur le processus 0
    array = np.random.rand(N)
    print(f"Process {rank} generated array: {array}")

    # Step 2: Déterminer les buckets ranges 
    buckets = [[] for _ in range(size)]
    for num in array:
        # Répartir les nombres uniformément dans chaque bucket
        bi = int(num * size)  # Échelle par nombre de buckets
        if bi == size:  # Cas limite
            bi -= 1
        buckets[bi].append(float(num))

else:
    buckets = None

# Step 3: Répartir les buckets sur tous les processus
local_bucket = comm.scatter(buckets, root=0)
print(f"Process {rank} received bucket: {local_bucket}")

# Step 4: Trier chaque bucket localement
sorted_local_bucket = bucket_sort(local_bucket)
print(f"Process {rank} sorted bucket: {sorted_local_bucket}")

# Step 5: Rassembler tous les buckets triés sur le processus 0
sorted_buckets = comm.gather(sorted_local_bucket, root=0)

if rank == 0:
    # Step 6: Concaténer les buckets triés
    sorted_array = [float(num) for bucket in sorted_buckets for num in bucket]
    print(f"Sorted Array: {sorted_array}")


# mpiexec -n 4 python3 BucketParallel.py