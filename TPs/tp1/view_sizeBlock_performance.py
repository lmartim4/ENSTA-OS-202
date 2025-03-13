import matplotlib.pyplot as plt

# Data provided for matrix size 2048
block_sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
cpu_times = [118.754, 92.5633, 25.71, 11.9335, 7.92738, 5.58489, 4.67631, 4.40002, 4.17148, 4.3505, 4.83713]
mflops    = [144.668, 185.601, 668.216, 1439.64, 2167.16, 3076.13, 3673.81, 3904.5, 4118.41, 3948.94, 3551.67]

# Create a figure with two subplots (one for CPU time and one for MFLOPs)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Plot CPU time vs block size
ax1.plot(block_sizes, cpu_times, marker='o', linestyle='-')
ax1.set_xscale('log', base=2)  # Use log scale for block sizes
ax1.set_ylabel("CPU Time (seconds)")
ax1.set_title("Performance vs Block Size (Matrix Size = 2048)")
ax1.grid(True)

# Plot MFLOPs vs block size
ax2.plot(block_sizes, mflops, marker='o', color='orange', linestyle='-')
ax2.set_xscale('log', base=2)  # Use log scale for block sizes
ax2.set_xlabel("Block Size")
ax2.set_ylabel("MFLOPs")
ax2.grid(True)

plt.tight_layout()
plt.show()
