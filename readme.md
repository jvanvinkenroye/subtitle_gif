# Subtitle GIF Generator

This project generates animated GIFs with word-by-word subtitles from a video file using Whisper and FFmpeg.

## Requirements

- Python 3.9 or higher
- FFmpeg

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/subtitle_gif.git
    cd subtitle_gif
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Ensure FFmpeg is installed on your system. You can download it from [FFmpeg.org](https://ffmpeg.org/download.html).

## Usage

To generate an animated GIF with subtitles from a video file, run the following command:

```sh
python generateSub2Gif.py <input_video>