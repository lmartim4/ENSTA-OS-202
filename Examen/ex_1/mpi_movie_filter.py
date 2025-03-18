from mpi4py import MPI
from PIL import Image
import os
import numpy as np
from scipy import signal
import time
import csv
import matplotlib.pyplot as plt

def apply_filter(image):
    img = Image.open(image)
    print(f"Taille originale {img.size}")

    img = img.convert('HSV')
    img = np.repeat(np.repeat(np.array(img), 2, axis=0), 2, axis=1)
    img = np.array(img, dtype=np.double) / 255.
    print(f"Nouvelle taille : {img.shape}")

    mask_gauss = np.array([[1., 2., 1.],
                           [2., 4., 2.],
                           [1., 2., 1.]]) / 16.
    blur_image = np.zeros_like(img, dtype=np.double)
    for i in range(3):
        blur_image[:, :, i] = signal.convolve2d(img[:, :, i],
                                                mask_gauss,
                                                mode='same')

    mask_sharp = np.array([[ 0., -1.,  0.],
                           [-1.,  5., -1.],
                           [ 0., -1.,  0.]])
    sharpen_image = np.zeros_like(blur_image)
    sharpen_image[:, :, 0:2] = blur_image[:, :, 0:2]
    sharpen_image[:, :, 2] = signal.convolve2d(blur_image[:, :, 2],
                                               mask_sharp,
                                               mode='same')
    sharpen_image = np.clip(sharpen_image, 0., 1.)

    sharpen_image *= 255.
    sharpen_image = sharpen_image.astype(np.uint8)
    
    return Image.fromarray(sharpen_image, 'HSV').convert('RGB')

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    # Synchronisation avant de démarrer le chronomètre global
    comm.Barrier()
    global_start = time.time()

    n_images = 37
    # Liste locale pour stocker les tuples (index_image, nom_image, temps_traitement)
    processing_times_local = []

    for i in range(rank, n_images, size):
        image_index = i + 1
        image_in = os.path.join("datas/perroquets/", f"Perroquet{image_index:04d}.jpg")
        
        start_time = time.time()
        sharpen_image = apply_filter(image_in)
        end_time = time.time()
        t_image = end_time - start_time
        
        processing_times_local.append((image_index, f"Perroquet{image_index:04d}.jpg", t_image))
        
        image_out = os.path.join("sorties/perroquets/", f"Perroquet{image_index:04d}.jpg")
        sharpen_image.save(image_out)
        print(f"[Rank {rank}] Image {image_index} traitée et sauvegardée en {t_image:.2f} sec.")

    comm.Barrier()
    global_end = time.time()
    local_total = global_end - global_start
    total_time = comm.reduce(local_total, op=MPI.MAX, root=0)

    all_processing_times = comm.gather(processing_times_local, root=0)

    if rank == 0:
        flat_processing_times = [item for sublist in all_processing_times for item in sublist]
        flat_processing_times.sort(key=lambda x: x[0])
        
        with open('mpi_original_time.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Image', 'ProcessingTime'])
            for (idx, image_name, t) in flat_processing_times:
                writer.writerow([image_name, t])
            writer.writerow(['Total', total_time])
        print("Fichier original_time.csv créé.")

        indices = [t[0] for t in flat_processing_times]
        times = [t[2] for t in flat_processing_times]
        
        plt.figure(figsize=(10, 6))
        plt.bar(indices, times)
        plt.xlabel("Index de l'image")
        plt.ylabel("Temps de traitement (s)")
        plt.title("Temps de traitement par image")
        plt.figtext(0.5, 0.01, f"Temps total de traitement : {total_time:.2f} secondes", ha="center", fontsize=12)
        plt.xticks(indices)
        plt.tight_layout()
        plt.savefig("processing_times.png")
        plt.show()

if __name__ == "__main__":
    main()
