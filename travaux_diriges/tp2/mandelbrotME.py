from mpi4py import MPI
import numpy as np
from PIL import Image
import matplotlib.cm
from time import time
from mandelbrot import MandelbrotSet

# Initialisation MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Paramètres de l'image
width, height = 1024, 1024
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)

scaleX, scaleY = 3.0 / width, 2.25 / height

# Processus maître
if rank == 0:
    start_time = time()

    # Initialisation du tableau pour stocker l’image complète
    global_convergence = np.empty((width, height), dtype=np.double)

    # Gestion dynamique des tâches : envoyer une ligne à chaque esclave
    next_row = 0  # Ligne actuelle à calculer
    num_active_workers = 0  # Nombre de processus esclaves actifs

    # Envoyer la première ligne à chaque esclave
    for worker in range(1, size):
        if next_row < height:
            comm.send(next_row, dest=worker, tag=1)
            next_row += 1
            num_active_workers += 1

    # Réception des résultats et distribution des nouvelles tâches
    while num_active_workers > 0:
        source, row, data = comm.recv(source=MPI.ANY_SOURCE, tag=2)
        global_convergence[:, row] = data  # Stocker la ligne reçue

        if next_row < height:
            comm.send(next_row, dest=source, tag=1)  # Envoyer nouvelle ligne
            next_row += 1
        else:
            comm.send(None, dest=MPI.ANY_SOURCE, tag=0)  # Fin des tâches
            num_active_workers -= 1

    end_time = time()
    print(f"Temps total (maître-esclave) : {end_time - start_time:.6f} secondes")

    # Sauvegarde de l'image
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(global_convergence.T) * 255))
    image.save("mandelbrot_master_slave.png")
    print("Image enregistrée sous 'mandelbrot_master_slave.png'.")

# Processus esclaves
else:
    while True:
        row = comm.recv(source=0, tag=MPI.ANY_TAG)
        if row is None:  # Fin des tâches
            break

        # Calcul de la ligne demandée
        row_data = np.zeros(width, dtype=np.double)
        for x in range(width):
            c = complex(-2.0 + scaleX * x, -1.125 + scaleY * row)
            row_data[x] = mandelbrot_set.convergence(c, smooth=True)

        # Envoyer la ligne calculée au maître
        comm.send((row, row_data), dest=0, tag=2)
