from mpi4py import MPI
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
import matplotlib.cm
import time

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def convergence(self, c: complex, smooth=False) -> float:
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

# Initialisation MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # Identifiant du processus
size = comm.Get_size()  # Nombre total de processus

# Paramètres de l'image
width, height = 1024, 1024
scaleX = 3. / width
scaleY = 2.25 / height
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)

# Répartition équitable des lignes entre les processus
rows_per_process = height // size
start_row = rank * rows_per_process
end_row = height if rank == size - 1 else (rank + 1) * rows_per_process

# Calcul du temps de début
start_time = time.time()

# Calcul de l'ensemble de Mandelbrot pour les lignes assignées
local_convergence = np.empty((width, end_row - start_row), dtype=np.double)
for y in range(start_row, end_row):
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
        local_convergence[x, y - start_row] = mandelbrot_set.convergence(c, smooth=True)

# Rassemblement des résultats
if rank == 0:
    global_convergence = np.empty((width, height), dtype=np.double)
else:
    global_convergence = None

comm.Gather(local_convergence, global_convergence, root=0)

# Fin du calcul
end_time = time.time()

if rank == 0:
    print(f"Temps d'exécution avec {size} processus : {end_time - start_time} secondes")

    # Constitution et sauvegarde de l'image
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(global_convergence.T) * 255))
    image.save("mandelbrot_parallel.png")
    print("Image sauvegardée : mandelbrot_parallel.png")


