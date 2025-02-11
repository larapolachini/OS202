from mpi4py import MPI
import numpy as np
from PIL import Image
import matplotlib.cm
from time import time
from mandelbrot import MandelbrotSet

# Initialise MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Configuration de l'imagem
width, height = 1024, 1024
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)

# Mesurer le temps total (uniquement dans le processus 0)
if rank == 0:
    start_time = time()

# Répartir les threads entre les processus
rows_per_proc = height // size  # Chaque processus reçoit un certain nombre de lignes
extra_rows = height % size      # Lignes supplémentaires (si non divisibles)
if rank < extra_rows:
    start_row = rank * (rows_per_proc + 1)
    end_row = start_row + rows_per_proc + 1
else:
    start_row = rank * rows_per_proc + extra_rows
    end_row = start_row + rows_per_proc

local_height = end_row - start_row  # Nombre de lignes que ce processus calcule
local_convergence = np.zeros((width, local_height))

# Calculer Mandelbrot pour les lignes attribuées
scaleX, scaleY = 3.0 / width, 2.25 / height
for y in range(local_height):
    for x in range(width):
        c = complex(-2.0 + scaleX * x, -1.125 + scaleY * (start_row + y))
        local_convergence[x, y] = mandelbrot_set.convergence(c, smooth=True)


# Préparation de la réception en cours 0
recv_counts = comm.gather(local_height * width, root=0)
recv_displacements = [sum(recv_counts[:i]) for i in range(size)] if rank == 0 else None
global_convergence = np.empty((width, height), dtype=np.double) if rank == 0 else None

# Utilisation de Gatherv pour éviter les erreurs de troncature
comm.Gatherv(local_convergence, (global_convergence, recv_counts, recv_displacements, MPI.DOUBLE), root=0)

# Enregistrer l'image en cours 0
if rank == 0:
    end_time = time()
    total_time = end_time - start_time
    print(f"Tempo total: {total_time:.6f} segundos")

    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(global_convergence.T) * 255))
    image.save("mandelbrot_parallel.png")
    print("Imagem salva como mandelbrot_parallel.png")
