import re
import os
import subprocess
import base64

from ffmpeg_progress_yield import FfmpegProgress
from tqdm import tqdm

import file_utils


def insert_subtitle(input_media_path: str, subtitles_path: [str], burn_subtitles: bool, output_video_path: str, crf: int = 20, maxrate: str = "2M", video_codec: str = "h264", audio_codec: str = "aac", preset: str = None):
    # set bufsize as double of maxrate
    bufsize = str(float(re.match(r"([0-9.]+)([a-zA-Z]*)", maxrate).group(1))
                  * 3) + re.match(r"([0-9.]+)([a-zA-Z]*)", maxrate).group(2)
    
    # use only valid srt files
    subtitles_path = file_utils.validate_files(subtitles_path)

    # insert in comand the basics of ffmpeg
    cmd_ffmpeg = ["ffmpeg", "-y"]
    cmd_ffmpeg_input_map = []
   
    # add ffmpeg input main media
    cmd_ffmpeg.extend(["-i", "file:" + input_media_path])
    # map everything from input media
    map_index = cmd_ffmpeg.count("-i") - 1
    cmd_ffmpeg_input_map.extend(["-map", f"{map_index}"])
    
    # detect if input has video channels
    result: str = subprocess.run(["ffprobe", "-i", "file:" + input_media_path, "-show_streams", "-select_streams", "v", "-loglevel", "error"], capture_output = True, text = True).stdout
    no_video = True if result is None or result.replace(" ", "").replace("  ", "") == "" else False
    
    # if input has no video channels, map a 1280x720 black screen
    if no_video:
        # create a background image if media is only audio
        background_tempfile: file_utils.TempFile = file_utils.TempFile("", ".jpeg")
    
        # create a 1280x720 jpeg image
        with open(file=background_tempfile.getname(), mode="wb") as file:
            file.write(base64.b64decode("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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/EACAQAAMBAAICAgMAAAAAAAAAAAABERAgMEFgMXBAkND/2gAIAQEAAQUC/QFPoKE7JzQ+p9MJzhPb7jITITIQgljRCEyY8SGTITIeYQmQg8Q9hNpRkITIT2ZbCY2LX1IYh4hi+HrzyLEPHiHi3yLHw8iH7S8Ysg8nB5MWvFrJjzyLFrxasnF5MXyIfx7NfwL0XheaJj6rwv0hS/0nf//EABQRAQAAAAAAAAAAAAAAAAAAALD/2gAIAQMBAT8BYQ//xAAUEQEAAAAAAAAAAAAAAAAAAACw/9oACAECAQE/AWEP/8QAFBABAAAAAAAAAAAAAAAAAAAA0P/aAAgBAQAGPwJhA//EACMQAAMBAQACAwABBQAAAAAAAAABERAxQVEgIWAwQGFwkND/2gAIAQEAAT8h/wBAVf4BSuX/AEelESX8NOv4VQ4+SV/X67jgTovkSTLX3FiBqCogfoUWQQhAwlSBKHGUQkFSGoIQNQgnGYHAlSMpM4OcSpGJ9zGYGTFRA/QSrzA1P0vWPomY4FwgfZ3Ep5OBWdI73E/uZb9ZHe55DQanGcnOHRaT0yvPwtWPhwNBOrfBznA1fIh8Z9OlpxkfvEfA1OP0yd1qLh2NGdII8C4dXPOcCdIGkhs4cb7nRAlPj9D4N4+PjW8DVIH36E6RPGonUQyJYPn6mUW5XtaK8sKyvblbWUu0XLCsr95X7yv2Imf2MSi3Sv2V+8rK3tF2tr95f+mB/wD/2gAMAwEAAgADAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIBCADCBACCMBCBACCCBCJBADIDCBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFLHGEGHHMMBABNBJKPAHKFCBHJHOKFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEEAMEMAAAEIAAEAIIMBAEIMAEAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAALD/2gAIAQMBAT8QYQ//xAAUEQEAAAAAAAAAAAAAAAAAAACw/9oACAECAQE/EGEP/8QAJxABAAIBAwQBBQADAAAAAAAAAQARMRAhYUFRcZFgIDBwgbGQodD/2gAIAQEAAT8Q/wAAQxcRGn8ALwJTuzsMx9u1Z+srWRSh9kCWMQ7fs1LupVu7+peBKd2PYxKaflgsHeBRRBVBcAWTBCg2wHVlMgTO8W4jveZjiccrL9IFjegWFy8tnHKyzERUQLmCmusz6BY3mCCrhAqw0Be8Gt92ccv8QqyxPBEVssO1cqWYl/iccpedoNavfT+8wedHe0C5iU22lt6BRRNzY2hVvsygTMzHYnHNm/SFQxHRZxzOMfJcOgRDALKiC1Jj8SxQRWLMRShqJlaG/GF9A8TaLjxo5gq9FsQVemR61oK/aog26xbX0mfTL5mDzMEdFgBYy5dhKdlfaGCOlaGZ/ExxaVGsZgaf3mDzofeJhSBClubE0Q3CAFkzwKKijZXQUotJ7EW1zP8AJjHMQcgzBLVGCY/Ew+JkMMQFOIF0vzKNhvEIqIbGZg1fmCJZAFgLuALIs3ArSEKPWIJSQDYbTPoskQFJCjY6TFcMof7ncXEUHWGCOn+cz+IZu/UQcl6YGn99Sq36g5SkxEdgIY5iy0gAbbEtUYIXIRRcRWk3Rl8TJmb5NicsVk6UdX3FXLehgMW66CwYtllHV96CmGopyrBTDU5Yq5b0CwxS2rFOV15Za7tirluCwZyzM5HuW3d7zke4KYanI9y0tbiq3P2zaItw7aCMKTke5yPegXWOQ68sU5dLrE5Yq5bgphqcj3BTCkU5X3+ChRsgupFOCpn/AKTt/9k="))
        
        # get input media duration
        duration_sec = subprocess.run(["ffprobe", "-i", "file:" + input_media_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"], capture_output = True, text = True).stdout.split("\n")[0].replace("\n", "").replace(" ", "").replace("   ", "").replace("00:", "").replace(":", ".")
    
        cmd_ffmpeg.extend(["-t", f"{duration_sec}", "-loop", "1", "-i", background_tempfile.getname()])
        map_index = cmd_ffmpeg.count("-i") - 1
        cmd_ffmpeg_input_map.extend(["-map", f"{map_index}:v"])
        
    # map each subtitle
    for i, subtitle in enumerate(subtitles_path):
        cmd_ffmpeg.extend(["-i", "file:" + subtitle])
        map_index = cmd_ffmpeg.count("-i") - 1
        cmd_ffmpeg_input_map.extend(["-map", f"{map_index}:s"])

    # add comand to burn subtitles if its demanded and has at least one valid subtitle in the array. Burn the first one. Also ensure hwupload if necessary
    vf_hwupload = True if video_codec.endswith(("_nvenc", "_amf", "_v4l2m2m", "_qsv", "_vaapi", "_videotoolbox", "_cuvid")) else False
    hw_device = video_codec.split("_")[-1] if vf_hwupload else None
    # set hw_device as cuda if api is nvenc or cuvid
    if hw_device == "nvenc" or hw_device == "cuvid":
        hw_device = "cuda"
        vf_hwupload = False
        
    # set hw_device as vaapi if api is v4l2m2m or amf
    if hw_device == "v4l2m2m" or hw_device == "amf":
        hw_device = "vaapi"

    if burn_subtitles and len(subtitles_path) > 0:
        # create temp file for .srt
        srt_temp = file_utils.TempFile(
            "", file_ext=".srt")
        
        file_utils.copy_file_if_different(
            subtitles_path[0], srt_temp.temp_file.name, True)
        
        # align subtitles to botton center if hass video and to center center if only audio with black screen
        sub_align = 10 if no_video else 2
        
        # insert scale, subtitles filter and hwupload if required
        cmd_ffmpeg.extend(
            ["-vf", f"format=nv12, scale=-1:'max(480,ih)', subtitles=\'{add_ffmpeg_escape_chars(srt_temp.temp_file.name)}\':force_style='Alignment={sub_align},Fontname=Verdana,PrimaryColour=&H03fcff,Fontsize=20,BackColour=&H80000000,Spacing=0.12,Outline=1,Shadow=1.2'" + (', hwupload' if vf_hwupload else '')])
    else:
        if vf_hwupload:
             cmd_ffmpeg.extend(["-vf", f"format=nv12, hwupload"])
        burn_subtitles = False
    
    cmd_ffmpeg.extend(cmd_ffmpeg_input_map)
    
    if preset is not None:
        cmd_ffmpeg.extend(["-preset", preset])

    # init a hw_device if hwupload is set on video filters
    if hw_device is not None:
        cmd_ffmpeg.extend(["-init_hw_device", hw_device])
        
    # add the remaining parameters and output path
    cmd_ffmpeg.extend(["-c:v", video_codec, "-c:a", audio_codec, "-c:s", "mov_text", 
                       "-af", "loudnorm", "-crf", str(crf), "-maxrate", maxrate, 
                       "-bufsize", bufsize, "-pix_fmt", "yuv420p", 
                       "-movflags", "+faststart", "-sws_flags", "bicubic+accurate_rnd+full_chroma_int+full_chroma_inp", 
                       "file:" + output_video_path])

    # run FFmpeg command with a fancy progress bar
    ff = FfmpegProgress(cmd_ffmpeg)
    with tqdm(total=100, position=0, ascii="░▒█", desc="Inserting subtitles" if not burn_subtitles else "Burning subtitles", unit="%", unit_scale=True, leave=True, bar_format="{desc} [{bar}] {percentage:3.0f}% | ETA: {remaining} | {rate_fmt}{postfix}") as pbar:
        for progress in ff.run_command_with_progress():
            pbar.update(progress - pbar.n)
            
    # destroy unecessary file  
    if 'srt_temp' in locals():
        srt_temp.destroy()


def extract_audio_mp3(input_media_path: str, output_path: str):
    # set the FFMpeg command
    cmd_ffmpeg = ["ffmpeg", "-y", "-i", "file:" + input_media_path,
                  "-vn", "-c:a", "mp3", "-af", "loudnorm", "-ar", "44100", "file:" + output_path]

    # run FFmpeg command with a fancy progress bar
    ff = FfmpegProgress(cmd_ffmpeg)
    with tqdm(total=100, position=0, ascii="░▒█", desc="Extracting audio", unit="%", unit_scale=True, leave=True, bar_format="{desc} {percentage:3.0f}% | ETA: {remaining}") as pbar:
        for progress in ff.run_command_with_progress():
            pbar.update(progress - pbar.n)
            
def extract_short_mp3(input_media_path: str, output_path: str):
    # get input media duration
    duration_sec = subprocess.run(["ffprobe", "-i", "file:" + input_media_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"], capture_output = True, text = True).stdout.split("\n")[0].replace("\n", "").replace(" ", "").replace("   ", "").replace("00:", "").replace(":", "").split(".")[0]
    
    if int(duration_sec) > 240:
        start_sec = int(duration_sec) - 120
        end_sec = int(duration_sec) - 60
    elif int(duration_sec) > 120:
        start_sec = int(duration_sec) - 80
        end_sec = int(duration_sec) - 20
    elif int(duration_sec) > 80:
        start_sec = int(duration_sec) - 60
        end_sec = int(duration_sec) - 20
    else:
        start_sec = 0
        end_sec = int(duration_sec)
    
    # set the FFMpeg command
    cmd_ffmpeg = ["ffmpeg", "-y", "-ss", f"{start_sec}", "-t", f"{end_sec}",  "-i", "file:" + input_media_path,
                  "-vn", "-c:a", "mp3", "-af", "loudnorm", "-ar", "44100", "file:" + output_path]

    # run FFmpeg command with a fancy progress bar
    ff = FfmpegProgress(cmd_ffmpeg)
    with tqdm(total=100, position=0, ascii="░▒█", desc="Extracting audio", unit="%", unit_scale=True, leave=False, bar_format="{desc} {percentage:3.0f}% | ETA: {remaining}") as pbar:
        for progress in ff.run_command_with_progress():
            pbar.update(progress - pbar.n)
            
def add_ffmpeg_escape_chars(string):
    new_string = ""
    for char in string:  
        if os.name == 'nt':
            if char == ":" or char == "\x5c":
                new_string += "\x5c"
        new_string += char
    return new_string
