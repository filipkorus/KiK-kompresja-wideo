import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the data from CSV files
df_compression_results = pd.read_csv('compression_results.csv')
df_b_i_p_frames = pd.read_csv('b_i_p_frames.csv')

df = pd.merge(df_compression_results, df_b_i_p_frames, on='filename', how='left')

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
resolutions = df['resolution'].unique()
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

# Plot compression_time vs bitrate_kbps for each resolution and codec
for resolution in resolutions:
    subset = df[df['resolution'] == resolution]
    fig, ax = plt.subplots(figsize=(10, 6))
    for codec, color in zip(codecs, colors):
        subset_codec = subset[subset['codec'] == codec]
        ax.plot(subset_codec['bitrate_kbps'], subset_codec['compression_time'],
                marker='x', linestyle='-', color=color, label=codec)
    ax.set_title(f'Compression Time vs Bitrate ({resolution})')
    ax.set_xlabel('Bitrate (kbps)')
    ax.set_ylabel('Compression Time [s]')
    ax.legend()
    save_plot(fig, f'compression_time_vs_bitrate_{resolution}.png')

# Plotting PSNR vs Bitrate, Compression Ratio vs Bitrate, and Compression Ratio vs PSNR for every resolution
plot_titles = ['PSNR vs Bitrate', 'Compression Ratio vs Bitrate', 'Compression Ratio vs PSNR']
x_labels = ['Bitrate (kbps)', 'Bitrate (kbps)', 'PSNR (dB)']
y_labels = ['PSNR (dB)', 'Compression Ratio', 'Compression Ratio']
y_columns = ['PSNR', 'compression_ratio', 'compression_ratio']

for i, (title, x_label, y_label, y_col) in enumerate(zip(plot_titles, x_labels, y_labels, y_columns)):
    for resolution in resolutions:
        subset = df[df['resolution'] == resolution]
        fig, ax = plt.subplots(figsize=(10, 6))
        for codec, color in zip(codecs, colors):
            subset_codec = subset[subset['codec'] == codec]
            ax.plot(subset_codec['PSNR'] if 'PSNR' in x_label else subset_codec['bitrate_kbps'], subset_codec[y_col],
                    marker='x', linestyle='-', color=color, label=codec)
        ax.set_title(f'{title} ({resolution})')
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.legend()
        save_plot(fig, f'{title.lower().replace(" ", "_")}_{resolution}.png')
