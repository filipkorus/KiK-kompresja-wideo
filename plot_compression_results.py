import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the data from CSV file
compression_results = pd.read_csv('compression_results.csv')
b_i_p_frames = pd.read_csv('b_i_p_frames.csv')

df = pd.merge(compression_results, b_i_p_frames, on='filename', how='left')

print(df.head())

# Convert bitrate_kbps to numeric
df['bitrate_kbps'] = pd.to_numeric(df['bitrate_kbps'], errors='coerce')

# Ensure plots directory exists
plots_dir = 'plots'
os.makedirs(plots_dir, exist_ok=True)

# Function to save plot to PNG file
def save_plot(fig, filename):
    filepath = os.path.join(plots_dir, filename)
    fig.savefig(filepath)
    plt.close(fig)

# Plotting
codecs = df['codec'].unique()
colors = plt.cm.tab10.colors[:len(codecs)]

# Plot 1: PSNR vs Bitrate for every codec
for codec in codecs:
    subset = df[df['codec'] == codec]
    fig, ax = plt.subplots(figsize=(10, 6))
    for resolution, group in subset.groupby('resolution'):
        ax.plot(group['bitrate_kbps'], group['PSNR'], marker='x', linestyle='-', label=resolution)
    ax.set_title(f'PSNR vs Bitrate ({codec})')
    ax.set_xlabel('Bitrate (kbps)')
    ax.set_ylabel('PSNR (dB)')
    ax.legend()
    save_plot(fig, f'psnr_vs_bitrate_{codec}.png')

# Plot 2: Compression Ratio vs Bitrate for every codec
for codec in codecs:
    subset = df[df['codec'] == codec]
    fig, ax = plt.subplots(figsize=(10, 6))
    for resolution, group in subset.groupby('resolution'):
        ax.plot(group['bitrate_kbps'], group['compression_ratio'], marker='x', linestyle='-', label=resolution)
    ax.set_title(f'Compression Ratio vs Bitrate ({codec})')
    ax.set_xlabel('Bitrate (kbps)')
    ax.set_ylabel('Compression Ratio')
    ax.legend()
    save_plot(fig, f'compression_ratio_vs_bitrate_{codec}.png')

# Plot 3: Compression Ratio vs PSNR for every codec
for codec in codecs:
    subset = df[df['codec'] == codec]
    fig, ax = plt.subplots(figsize=(10, 6))
    for resolution, group in subset.groupby('resolution'):
        ax.plot(group['PSNR'], group['compression_ratio'], marker='x', linestyle='-', label=resolution)
    ax.set_title(f'Compression Ratio vs PSNR ({codec})')
    ax.set_xlabel('PSNR (dB)')
    ax.set_ylabel('Compression Ratio')
    ax.legend()
    save_plot(fig, f'compression_ratio_vs_psnr_{codec}.png')
