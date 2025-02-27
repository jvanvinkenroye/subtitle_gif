import whisper
import subprocess
import os
import sys
from typing import Dict, List

def srt_timestamp(seconds: float) -> str:
    """
    Converts fractional seconds into SRT's HH:MM:SS,mmm format.

    Args:
        seconds: The time in seconds (float).

    Returns:
        The SRT timestamp string.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def load_whisper_model(model_size: str = "small") -> whisper.Whisper:
    """
    Loads the Whisper model.

    Args:
        model_size: The size of the Whisper model to load (e.g., "small", "medium", "large").

    Returns:
        The loaded Whisper model.
    """
    print(f"Loading Whisper model: {model_size}")
    return whisper.load_model(model_size)


def transcribe_video(model: whisper.Whisper, input_video: str) -> Dict:
    """
    Transcribes the audio from a video file using the Whisper model.

    Args:
        model: The loaded Whisper model.
        input_video: The path to the video file.

    Returns:
        The transcription result as a dictionary.
    """
    print(f"Transcribing video: {input_video}")
    return model.transcribe(input_video)


def generate_word_by_word_srt(transcription_result: Dict, srt_file_path: str) -> None:
    """
    Generates an SRT file with word-by-word timestamps.

    Args:
        transcription_result: The transcription result from Whisper.
        srt_file_path: The path to save the SRT file.
    """
    print(f"Generating word-by-word SRT file: {srt_file_path}")
    srt_lines: List[str] = []
    cue_index = 1

    for segment in transcription_result["segments"]:
        segment_start = segment["start"]
        segment_end = segment["end"]
        text = segment["text"].strip()

        words = text.split()
        if not words:
            continue

        segment_duration = segment_end - segment_start
        word_duration = segment_duration / len(words)

        for i, word in enumerate(words):
            word_start = segment_start + i * word_duration
            word_end = segment_start + (i + 1) * word_duration

            start_str = srt_timestamp(word_start)
            end_str = srt_timestamp(word_end)

            srt_lines.append(str(cue_index))
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(word)
            srt_lines.append("")  # Blank line
            cue_index += 1

    with open(srt_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    print(f"Done writing SRT {srt_file_path}")


def burn_subtitles(input_video: str, srt_file_path: str, output_video_path: str) -> None:
    """
    Burns the subtitles from an SRT file into a video using FFmpeg.

    Args:
        input_video: The path to the input video.
        srt_file_path: The path to the SRT file.
        output_video_path: The path to save the output video with subtitles.
    """
    print(f"Burning subtitles into video: {output_video_path}")

    ffmpeg_filter = (
        f"subtitles={srt_file_path}:force_style=" # Corrected line
        f"'Alignment=2,FontSize=40,MarginV=100,"
        f"PrimaryColour=&H00FFFFFF,"  # added white text
        f"OutlineColour=&H00000000,"  # added black outline
        f"Outline=2,"  # added outline thickness
        f"Shadow=1'" # removed shadow
    )

    command = [
        "ffmpeg",
        "-y",  # Overwrite without asking
        "-i", input_video,
        "-vf", ffmpeg_filter,
        output_video_path
    ]

    subprocess.run(command, check=True)
    print(f"Done burning subtitles into {output_video_path}")


def generate_palette(output_video_path: str, palette_file_path: str) -> None:
    """
    Generates a color palette for the GIF.

    Args:
        output_video_path: The path to the video used to generate the palette.
        palette_file_path: The path to save the palette file.
    """
    print(f"Generating palette for GIF: {palette_file_path}")
    command_palette = [
        "ffmpeg",
        "-y",
        "-i", output_video_path,
        "-vf", "fps=10,scale=320:-1:flags=lanczos,palettegen",
        palette_file_path
    ]

    subprocess.run(command_palette, check=True)
    print(f"Done generating palette {palette_file_path}")


def convert_to_gif(output_video_path: str, palette_file_path: str, gif_file_path: str) -> None:
    """
    Converts the video to an animated GIF using the generated palette.

    Args:
        output_video_path: The path to the video.
        palette_file_path: The path to the palette file.
        gif_file_path: The path to save the GIF.
    """
    print(f"Converting to animated GIF: {gif_file_path}")
    command_gif = [
        "ffmpeg",
        "-y",
        "-i", output_video_path,
        "-i", palette_file_path,
        "-lavfi", "fps=10,scale=320:-1:flags=lanczos,paletteuse",
        gif_file_path
    ]

    subprocess.run(command_gif, check=True)
    print(f"Done converting to GIF {gif_file_path}")


def process_video(input_video: str) -> None:
    """
    Processes the input video to generate a GIF with subtitles.

    Args:
        input_video: The path to the input video file.
    """
    base_name = os.path.splitext(input_video)[0]
    srt_file_path = f"{base_name}.srt"
    output_video_path = f"{base_name}_output.mp4"
    palette_file_path = f"{base_name}_palette.png"
    gif_file_path = f"{base_name}.gif"

    model = load_whisper_model()
    transcription_result = transcribe_video(model, input_video)
    generate_word_by_word_srt(transcription_result, srt_file_path)
    burn_subtitles(input_video, srt_file_path, output_video_path)
    generate_palette(output_video_path, palette_file_path)
    convert_to_gif(output_video_path, palette_file_path, gif_file_path)

    print(f"Done! Animated GIF saved as {gif_file_path}")


def main():
    """
    Main function to process the command-line arguments and start the video processing.
    """
    if len(sys.argv) != 2:
        print("Usage: python generateSub2Gif.py <input_video>")
        sys.exit(1)

    input_video = sys.argv[1]
    process_video(input_video)


if __name__ == "__main__":
    main()