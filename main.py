import os
import requests
import m3u8
import concurrent.futures
import ffmpeg
import re

"""
This script downloads and merges video segments from an .m3u8 playlist.
It fetches all .ts segments, merges them, and saves the final output as an .mp4 file.
The output filename must only contain alphanumeric characters.
"""

def download_segment(url, output_path):
    """ Downloads a single .ts segment """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Downloaded: {output_path}")
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")

def validate_filename(filename):
    """ Checks if the filename contains only alphanumeric characters """
    return re.fullmatch(r"[a-zA-Z0-9-_]+", filename) is not None

def download_m3u8(m3u8_url, output_filename):
    """ Downloads and merges video segments from an .m3u8 playlist """
    response = requests.get(m3u8_url)
    response.raise_for_status()
    playlist = m3u8.loads(response.text)
    
    if not playlist.segments:
        print("No segments found in the .m3u8 file")
        return
    
    base_url = os.path.dirname(m3u8_url)  # Base URL for segments
    segment_urls = [segment.uri if segment.uri.startswith("http") else f"{base_url}/{segment.uri}" for segment in playlist.segments]
    
    os.makedirs("segments", exist_ok=True)
    segment_files = [f"segments/segment_{i}.ts" for i in range(len(segment_urls))]
    
    # Downloading segments concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download_segment, segment_urls, segment_files)
    
    # Merging segments into an MP4 file
    concat_list_path = "segments/concat_list.txt"

    with open(concat_list_path, "w") as f:
        for segment_file in segment_files:
            f.write(f"file '{os.path.basename(segment_file)}'\n")

    
    ffmpeg.input(concat_list_path, format='concat', safe=0).output(output_filename + ".mp4", c='copy').run(overwrite_output=True)
    print(f"Video saved as: {output_filename}.mp4")
    
    # Cleaning up downloaded segments
    for segment_file in segment_files:
        os.remove(segment_file)
    os.remove(concat_list_path)
    os.rmdir("segments")

if __name__ == "__main__":
    m3u8_url = input("Enter the .m3u8 URL: ")
    output_filename = input("Enter the output filename (without extension): ")
    
    if not validate_filename(output_filename):
        print("Error: The filename can only contain letters and numbers (no spaces or special characters).")
    else:
        download_m3u8(m3u8_url, output_filename)
