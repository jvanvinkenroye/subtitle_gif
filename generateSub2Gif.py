import whisper
import subprocess
import os
import sys

def srt_timestamp(seconds: float) -> str:
    """
    Convert fractional seconds into SRT's HH:MM:SS,mmm format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def load_model():
    return whisper.load_model("small")

def transcribe_video(model, input_video):
    return model.transcribe(input_video)

def generate_srt(result, srt_file):
    srt_lines = []
    cue_index = 1

    for seg in result["segments"]:
        seg_start = seg["start"]
        seg_end   = seg["end"]
        text      = seg["text"].strip()

        # Split into individual words
        words = text.split()
        if not words:
            continue

        seg_duration = seg_end - seg_start
        word_duration = seg_duration / len(words)

        for i, w in enumerate(words):
            word_start = seg_start + i * word_duration
            word_end   = seg_start + (i + 1) * word_duration

            start_str = srt_timestamp(word_start)
            end_str   = srt_timestamp(word_end)

            srt_lines.append(str(cue_index))
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(w)
            srt_lines.append("")  # blank line
            cue_index += 1

    with open(srt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

def burn_subtitles(input_video, srt_file, output_video):
    ffmpeg_filter = (
        f"subtitles={srt_file}:force_style="
        f"'Alignment=2,FontSize=60,MarginV=100'"
    )

    command = [
        "ffmpeg",
        "-y",             # overwrite without asking
        "-i", input_video,
        "-vf", ffmpeg_filter,
        output_video
    ]

    print("Burning subtitles into MP4 with bigger text...")
    subprocess.run(command, check=True)

def generate_palette(output_video, palette_file):
    command_palette = [
        "ffmpeg",
        "-y",
        "-i", output_video,
        "-vf", "fps=10,scale=320:-1:flags=lanczos,palettegen",
        palette_file
    ]

    print("Generating palette for GIF...")
    subprocess.run(command_palette, check=True)

def convert_to_gif(output_video, palette_file, gif_file):
    command_gif = [
        "ffmpeg",
        "-y",
        "-i", output_video,
        "-i", palette_file,
        "-lavfi", "fps=10,scale=320:-1:flags=lanczos,paletteuse",
        gif_file
    ]

    print("Converting to animated GIF...")
    subprocess.run(command_gif, check=True)

def process_video(input_video):
    base_name = os.path.splitext(input_video)[0]
    srt_file = f"{base_name}.srt"
    output_video = f"{base_name}_output.mp4"
    palette_file = f"{base_name}_palette.png"
    gif_file = f"{base_name}.gif"

    model = load_model()
    result = transcribe_video(model, input_video)
    generate_srt(result, srt_file)
    burn_subtitles(input_video, srt_file, output_video)
    generate_palette(output_video, palette_file)
    convert_to_gif(output_video, palette_file, gif_file)

    print(f"Done! Animated GIF saved as {gif_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generateSub2Gif.py <input_video>")
        sys.exit(1)

    input_video = sys.argv[1]
    process_video(input_video)