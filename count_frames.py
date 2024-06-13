import subprocess
from glob import glob
import re


def count_frames(video_path):
    ffprobe_cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'frame=pict_type', '-of', 'csv=p=0', video_path
    ]

    # Run ffprobe command
    try:
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error running ffprobe command:", e)
        return

    # Parse ffprobe output to count frame types
    frame_counts = {'I': 0, 'P': 0, 'B': 0}
    for line in re.split(r'\s|,\s*', result.stdout.strip()):
        frame_type = line.strip()
        if frame_type in frame_counts:
            frame_counts[frame_type] += 1

    return frame_counts


if __name__ == "__main__":
    output_csv_file = 'b_i_p_frames.csv'
    print('filename,B_frames,I_frames,P_frames', file=open(output_csv_file, 'a'))

    h261_files = glob('./output/*h261*.avi')
    mpeg1_files = glob('./output/*mpeg1*.mp4')
    mpeg4_files = glob('./output/*mpeg4*.mp4')

    files = []
    files.extend(h261_files)
    files.extend(mpeg1_files)
    files.extend(mpeg4_files)
    files = [f.split('\\')[-1] for f in files]

    for file in files:
        frame_counts = count_frames(f'./output/{file}')
        i, p, b = frame_counts.get('I', 0), frame_counts.get('P', 0), frame_counts.get('B', 0)

        print(f'{file},{b},{i},{p}', file=open(output_csv_file, 'a'))
        print(f'file: {file}\nB: {b}, I: {i}, P: {p}\n')
