from PIL import Image
import numpy as np
from scipy import signal
from mpi4py import MPI
import csv
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def upsize_chunk(image_data, start_row, end_row):
    img_chunk = image_data[start_row:end_row, :, :]
    img_chunk = np.repeat(np.repeat(img_chunk, 2, axis=0), 2, axis=1) / 255.0
    return img_chunk

def apply_blur_filter(image_chunk):
    blur_image = np.zeros_like(image_chunk, dtype=np.float64)
    blur_mask = np.array([[1., 2., 1.],
                          [2., 4., 2.],
                          [1., 2., 1.]]) / 16.
    for i in range(3):
        blur_image[:, :, i] = signal.convolve2d(
            image_chunk[:, :, i], blur_mask, mode='same'
        )
    return blur_image

def apply_sharpen_filter(blur_chunk):
    sharpen_mask = np.array([
        [ 0., -1.,  0.],
        [-1.,  5., -1.],
        [ 0., -1.,  0.]
    ])

    sharpen_image = np.zeros_like(blur_chunk, dtype=np.float64)
    sharpen_image[:, :, :2] = blur_chunk[:, :, :2]
    sharpen_image[:, :, 2] = np.clip(
        signal.convolve2d(blur_chunk[:, :, 2], sharpen_mask, mode='same'),
        0.0, 1.0
    )
    return sharpen_image

def main():
    comm.Barrier()
    start_time = MPI.Wtime()

    path = "datas/"
    image_path = path + "paysage.jpg"

    if rank == 0:
        img = Image.open(image_path)
        print(f"Taille originale (width x height): {img.size}")
        img = img.convert('HSV')
        img_array = np.array(img, dtype=np.double)
        img_shape = img_array.shape
    else:
        img_array = None
        img_shape = None

    img_shape = comm.bcast(img_shape, root=0)

    if rank != 0:
        img_array = np.empty(img_shape, dtype=np.double)

    comm.Bcast(img_array, root=0)

    rows_per_proc = img_shape[0] // size
    start_row = rank * rows_per_proc
    end_row = (rank + 1) * rows_per_proc if rank < size - 1 else img_shape[0]

    upscaled_chunk = upsize_chunk(img_array, start_row, end_row)
    blur_chunk = apply_blur_filter(upscaled_chunk)
    sharpen_chunk = apply_sharpen_filter(blur_chunk)
    sharpen_chunk = (255.0 * sharpen_chunk).astype(np.uint8)
    
    local_shape = sharpen_chunk.shape
    all_shapes = comm.gather(local_shape, root=0)

    if rank == 0:
        total_height = sum(shape[0] for shape in all_shapes)
        full_processed_shape = (total_height, all_shapes[0][1], all_shapes[0][2])
        full_processed = np.empty(full_processed_shape, dtype=np.uint8)

        recv_counts = [sh[0] * sh[1] * sh[2] for sh in all_shapes]
        displacements = [0]
        for i in range(1, len(recv_counts)):
            displacements.append(displacements[i - 1] + recv_counts[i - 1])
    else:
        full_processed = None
        recv_counts = None
        displacements = None

    sendbuf = sharpen_chunk.ravel()
    comm.Gatherv(
        sendbuf=sendbuf,
        recvbuf=(full_processed, recv_counts, displacements, MPI.UNSIGNED_CHAR),
        root=0
    )

    if rank == 0:
        final_image = Image.fromarray(full_processed, mode='HSV').convert('RGB')
        print(f"Nouvelle taille (width x height): {final_image.size}")
        final_image.save("sorties/paysage_double.jpg")
        print("Image sauvegardée")

        end_time = MPI.Wtime()
        elapsed_time = end_time - start_time

        with open("performance_metrics.csv", "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["ElapsedTime (s)", "Number of Processors"])
            csvwriter.writerow([elapsed_time, size])
        print(f"Performance metrics written: {elapsed_time:.4f} seconds with {size} processes.")

if __name__ == "__main__":
    main()