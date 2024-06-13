import subprocess
import time
import os


def recompress_video(input_file, codec_name, codec, resolution, bitrate, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    width, height = resolution.split('x')
    output_file = os.path.join(
        output_dir,
        f"{os.path.splitext(os.path.basename(input_file))[0]}_{codec_name}_{resolution}_{bitrate}k.{'mp4' if codec != 'h261' else 'avi'}"
    )

    # Construct the ffmpeg command for recompression
    command = [
        'ffmpeg',
        '-y',
        '-i', input_file,
        '-vf', f'scale={width}:{height}',
        '-c:v', codec,
        '-b:v', f'{bitrate}k',
        '-c:a', 'copy',
        output_file
    ]

    print(f"Recompressing {input_file} to {resolution} at {bitrate}kbps using {codec_name}...")
    subprocess.run(command, check=True)
    print(f"Saved to {output_file}")

    return output_file


def calculate_psnr_and_sizes(reference_file, encoded_file, resolution):
    command = [
        'ffmpeg',
        '-i', reference_file,
        '-vf', f'scale={":".join(resolution.split("x"))}',
        '-y',  # Overwrite output files without asking
        'ref.y4m'
    ]
    subprocess.run(command, check=True)

    # Calculate PSNR between recompressed reference and encoded file
    command = [
        'ffmpeg', '-i', 'ref.y4m', '-i', encoded_file,
        '-lavfi', 'psnr=stats_file=psnr.log', '-y', '-f', 'null', '-'
    ]
    subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    # Parse PSNR from the log file generated by ffmpeg
    with open('psnr.log', 'r') as f:
        psnr_output = f.read()

    # Example line from ffmpeg log: "frame:0 mse_avg:165.137 psnr_avg:37.97..."
    psnr_line = psnr_output.strip().split('\n')[-1]  # Taking the last line assuming it's the summary
    psnr = float(psnr_line.split('psnr_avg:')[1].split()[0])

    compressed_file_size = get_video_size(encoded_file)
    original_file_size = get_video_size('ref.y4m')

    # Clean up the psnr.log and recompressed reference file
    os.remove('psnr.log')
    os.remove('ref.y4m')

    return psnr, original_file_size, compressed_file_size


def get_video_size(file_path):
    return os.path.getsize(file_path)


def main():
    output_csv_file = 'compression_results.csv'
    input_file = 'videos/BigBuckBunny.y4m'
    output_dir = 'output'

    codecs = {
        'h261': 'h261',
        'mpeg1': 'mpeg1video',
        'mpeg4': 'mpeg4',
        'h264': 'libx264',
        'h265': 'libx265'
    }

    # resolutions to test
    resolutions = ['1920x1080', '1280x720', '720x480', '352x288', '176x144']
    h261_resolutions = ['352x288', '176x144']

    # bit rates to test
    bitrates = [100, 200, 300, 400, 500, 750, 1000, 1250, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 7500, 10000, 15000]

    print('filename,filesize,codec,compression_time,compression_ratio,resolution,bitrate_kbps,PSNR', file=open(output_csv_file, 'a'))

    for codec_name, codec in codecs.items():
        for resolution in (h261_resolutions if codec_name == 'h261' else resolutions):
            for bitrate in bitrates:
                start_time = time.time()
                compressed_file = recompress_video(input_file, codec_name, codec, resolution, bitrate, output_dir)
                end_time = time.time()
                encoding_time = end_time - start_time

                psnr_value, original_file_size, compressed_file_size = calculate_psnr_and_sizes(input_file, compressed_file, resolution)

                compression_ratio = original_file_size / compressed_file_size

                print(f'{os.path.basename(compressed_file)},{compressed_file_size},{codec_name},{encoding_time},{compression_ratio},{resolution},{bitrate},{psnr_value}', file=open(output_csv_file, 'a'))


if __name__ == '__main__':
    main()
